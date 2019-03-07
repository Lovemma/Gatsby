# -*- coding: utf-8 -*-

import re
import random
from html.parser import HTMLParser

import mistune
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from app.extenions import db
from .base import BaseModel
from .comment import CommentMixin
from .consts import K_POST, ONE_HOUR
from .mc import cache, clear_mc
from .react import ReactMixin
from .utils import trunc_utf8

MC_KEY_TAGS_BY_POST_ID = 'post:%s:tags'
MC_KEY_RELATED = 'post:related_posts:%s'
MC_KEY_POST_BY_SLUG = 'post:%s:slug'
MC_KEY_FEED = 'core:feed'
MC_KEY_SITEMAP = 'core:sitemap'

BQ_REGEX = re.compile(r'<blockquote>.*?</blockquote>')


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


class BlogHtmlFormatter(HtmlFormatter):
    def __init__(self, **options):
        super().__init__(**options)
        self.lang = options.get('lang', '')

    def _wrap_div(self, inner):
        style = []
        if (self.noclasses and not self.nobackground and
                self.style.background_color is not None):
            style.append('background: %s' % (self.style.background_color,))
        if self.cssstyles:
            style.append(self.cssstyles)
        style = '; '.join(style)

        yield 0, ('<figure' + (
                    self.cssclass and ' class="%s"' % self.cssclass) +  # noqa
                  (style and (' style="%s"' % style)) +
                  (self.lang and ' data-lang="%s"' % self.lang) +
                  '><table><tbody><tr><td class="code">')
        for tup in inner:
            yield tup
        yield 0, '</table></figure>\n'

    def _wrap_pre(self, inner):
        style = []
        if self.prestyles:
            style.append(self.prestyles)
        if self.noclasses:
            style.append('line-height: 125%')
        style = '; '.join(style)

        if self.filename:
            yield 0, ('<span class="filename">' + self.filename + '</span>')

        # the empty span here is to keep leading empty lines from being
        # ignored by HTML parsers
        yield 0, ('<pre' + (style and ' style="%s"' % style) + (
                    self.lang and f' class="hljs {self.lang}"') + '><span></span>')
        for tup in inner:
            yield tup
        yield 0, '</pre>'


def block_code(text, lang, inlinestyles=False, linenos=False):
    if not lang:
        text = text.strip()
        return '<pre><code>%s</code></pre>\n' % mistune.escape(text)

    try:
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = BlogHtmlFormatter(
            noclasses=inlinestyles, linenos=linenos,
            cssclass='highlight %s' % lang, lang=lang
        )
        code = highlight(text, lexer, formatter)
        return code
    except Exception:
        return '<pre class="%s"><code>%s</code></pre>\n' % (
            lang, mistune.escape(text)
        )


class BranRenderer(mistune.Renderer):

    def block_code(self, text, lang):
        inlinestyles = self.options.get('inlinestyles')
        linenos = self.options.get('linenos')
        return block_code(text, lang, inlinestyles, linenos)


renderer = BranRenderer(linenos=False, inlinestyles=False)
markdown = mistune.Markdown(escape=True, renderer=renderer)


class Post(CommentMixin, ReactMixin, BaseModel):
    __tablename__ = 'posts'

    STATUSES = (
        STATUS_UNPUBLISHED,
        STATUS_ONLINE
    ) = [False, True]

    title = db.Column(db.String(length=100), unique=True)
    author_id = db.Column(db.Integer)
    slug = db.Column(db.String(length=100))
    summary = db.Column(db.String(length=255))
    can_comment = db.Column(db.Boolean, default=True)
    status = db.Column(db.Boolean, default=STATUSES)
    kind = K_POST

    @classmethod
    def create(cls, **kwargs):
        tags = kwargs.pop('tags', [])
        content = kwargs.pop('content')
        obj = super().create(**kwargs)
        if tags:
            PostTag.update_multi(obj.id, tags)
        obj.set_content(content)
        return obj

    def update_tags(self, tagnames):
        if tagnames:
            PostTag.update_multi(self.id, tagnames)
        return True

    @property
    @cache(MC_KEY_TAGS_BY_POST_ID % ('{self.id}'))
    def tags(self):
        pts = PostTag.query.filter_by(post_id=self.id).all()
        if not pts:
            return []
        ids = [pt.tag_id for pt in pts]
        return Tag.query.filter(Tag.id.in_(ids)).all()

    @property
    def author(self):
        from app.models import User
        return User.query.get(self.author_id)

    def preview_url(self):
        return f'/{self.__class__.__name__.lower()}/{self.id}/preview'

    def set_content(self, content):
        return self.set_props_by_key('content', content)

    def save(self, **kwargs):
        content = kwargs.pop('content', None)
        if content is not None:
            self.set_content(content)
        return super().save()

    @property
    def content(self):
        rv = self.get_props_by_key('content')
        if rv:
            return rv.decode('utf-8')

    @property
    def html_content(self):
        content = self.content
        if not content:
            return ''
        return markdown(content)

    @property
    def excerpt(self):
        if self.summary:
            return self.summary
        s = MLStripper()
        s.feed(self.html_content)
        return trunc_utf8(BQ_REGEX.sub('', s.get_data().replace('\n', ''), 100))

    @cache(MC_KEY_RELATED % ('{self.id}'), ONE_HOUR)
    def get_related(self, limit=4):
        tag_ids = [tag.id for tag in self.tags]
        post_ids = set(PostTag.query.filter(
            PostTag.post_id != self.id, PostTag.tag_id.in_(tag_ids))
                       .with_entities(PostTag.post_id).all())

        excluded_ids = (self.query.filter(Post.status != self.STATUS_ONLINE)
                        .with_entities(Post.id).all())

        post_ids -= set(excluded_ids)

        try:
            post_ids = random.sample(post_ids, limit)
        except ValueError:
            pass

        return self.get_multi(post_ids)

    def clear_mc(self):
        clear_mc(MC_KEY_RELATED % self.id)
        clear_mc(MC_KEY_POST_BY_SLUG % self.slug)
        for key in [MC_KEY_FEED, MC_KEY_SITEMAP]:
            clear_mc(key)

    @classmethod
    @cache(MC_KEY_POST_BY_SLUG % '{slug}')
    def get_by_slug(cls, slug):
        return cls.query.filter_by(slug=slug).first()

    @classmethod
    def cache(cls, ident):
        obj = super().cache(ident)
        if not obj:
            return cls.get_by_slug(ident)
        return obj


class Tag(BaseModel):
    __tablename__ = 'tags'

    name = db.Column(db.String(length=100), unique=True)

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def create(cls, **kwargs):
        name = kwargs.pop('name')
        kwargs['name'] = name.lower()
        return super().create(**kwargs)


class PostTag(BaseModel):
    __tablename__ = 'post_tags'

    post_id = db.Column(db.Integer)
    tag_id = db.Column(db.Integer)

    @classmethod
    def update_multi(cls, post_id, tags):
        tags = set(tags)
        origin_tags = set([t.name for t in Post.query.get(post_id).tags])

        need_add = tags - origin_tags
        need_del = origin_tags - tags
        need_add_tag_ids = set()
        need_del_tag_ids = set()
        for tag_name in need_add:
            tag, _ = Tag.get_or_create(name=tag_name)
            need_add_tag_ids.add(tag.id)
        for tag_name in need_del:
            tag, _ = Tag.get_or_create(name=tag_name)
            need_del_tag_ids.add(tag.id)

        if need_del_tag_ids:
            cls.query.filter(cls.post_id == post_id,
                             cls.tag_id.in_(need_del_tag_ids)).delete(
                synchronize_session=False)
            db.session.commit()
        for tag_id in need_add_tag_ids:
            PostTag.get_or_create(post_id=post_id, tag_id=tag_id)

        clear_mc(MC_KEY_TAGS_BY_POST_ID % post_id)

# -*- coding: utf-8 -*-

from pathlib import Path

import click
import cssmin
from sqlalchemy.exc import IntegrityError

from app import create_app
from app.extenions import db
from app.models import create_user
from app.config import HERE


@click.group()
def cli():
    ...


@cli.command()
def initdb():
    db.drop_all(app=create_app())
    db.create_all(app=create_app())
    print('Init database successfully.')


def _adduser(**kwargs):
    with create_app().app_context():
        try:
            user = create_user(**kwargs)
        except IntegrityError as e:
            click.echo(str(e))
        else:
            click.echo(f'User {user.name} created!!! ID: {user.id}')


@cli.command()
@click.option('--name', required=True, prompt=True)
@click.option('--email', required=False, default=None, prompt=True)
@click.option('--password', required=True, prompt=True, hide_input=True,
              confirmation_prompt=True)
def adduser(name, email, password):
    _adduser(name=name, email=email, password=password)


@cli.command()
def build_css():
    build_map = {
        'main.min.css': ['pure-min.css', 'base.css'],
        'index.min.css': ['main.min.css', 'fontawesome.min.css'],
        'post.min.css': ['index.min.css', 'react.css', 'gitment.css',
                         'social-sharer.css']
    }
    css_map = {}
    css_dir = Path(HERE) / 'static/css/'
    for css, files in build_map.items():
        data = ''
        for file in files:
            if file in css_map:
                data += css_map[file]
            else:
                with open(css_dir / file) as f:
                    data_ = f.read()
                    css_map[file] = data_
                data += data_
        with open(css_dir / css, 'w') as f:
            f.write(cssmin.cssmin(data))
            css_map[css] = data


if __name__ == '__main__':
    cli()

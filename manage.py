# -*- coding: utf-8 -*-

import click
from sqlalchemy.exc import IntegrityError

from app import db, create_app
from app.models import create_user


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


if __name__ == '__main__':
    cli()

# -*- coding: utf-8 -*-

import click

from app import db, create_app


@click.group()
def cli():
    ...


@cli.command()
def initdb():
    import app.models
    db.drop_all(app=create_app())
    db.create_all(app=create_app())
    print('Init database successfully.')


if __name__ == '__main__':
    cli()

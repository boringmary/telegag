import click

from db import db

cli = click.CommandCollection(sources=[db])

if __name__ == '__main__':
    cli()

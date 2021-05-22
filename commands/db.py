import click
import pymongo

from app.helpers import load_yaml

CFG_NAME = "app/config.yaml"


@click.group()
def db():
    '''
    '''
    pass


@db.command()
def init_db():
    '''
    '''
    cfg = load_yaml(CFG_NAME)
    client = pymongo.MongoClient(cfg['MONGO_URI'])
    db = client[cfg['MONGO_DB']]

    collist = db.list_collection_names()
    if "jobs" not in collist:
        db["jobs"]

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def load_yaml(filepath):
    '''Load yaml file and return python dictionary.
    :param: filepath: full path of the file
    '''
    try:
        with open(filepath, 'r') as stream:
            return yaml.load(stream, Loader=Loader)
    except FileNotFoundError as exc:
        # TODO implement yaml error handling
        raise
    except yaml.YAMLError as exc:
        # TODO implement yaml error handling
        raise
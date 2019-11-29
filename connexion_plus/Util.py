
from urllib.parse import urlparse
import os
import requests
import yaml


def load_oai(files):
    """
    Loads the given files. Either files is from type String or List of Strings.

    For convenience, you can use multiple files separated by ";" in a string:
    e.g. "file1;../file2;http://rawfile.com/petstore.yaml"
    """
    if isinstance(files, str):
        # split, if string are multiple files separated by ;
        split = parse_env(files)
        files = split if len(split) > 1 else [files]

    if isinstance(files, list):
        oai = [internal_load_oai(f) for f in files]
        return oai
    
    raise ValueError("Files need to be from type string or list of strings.")

def parse_env(env: str):
    """
    For internal use only.
    """
    return env.split(";")

def internal_load_oai(file: str):
    """
    For internal use only.
    """
    openapi_file = None
    # the file is an url and should be loaded
    if is_url(file):
        # download file
        openapi_file = requests.get(file)
        # read in yaml
        openapi_file = openapi_file.content

    # else if the file is a file, read it
    elif is_file(file):
        with open(file, 'r') as f:
            openapi_file = f.read()
    else:
        raise ValueError(f"Not a valid oai url or filepath: {file}.")

    return yaml.full_load(openapi_file)


def is_url(url):
    """
    For internal use only.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_file(path):
    """
    For internal use only.
    """
    return (os.path.exists(path) and not os.path.isdir(path))

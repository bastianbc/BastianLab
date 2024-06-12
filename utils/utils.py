from django.utils.http import urlencode
from django.urls import reverse
from functools import wraps
import re
import time

def build_url(*args, **kwargs):
    ##This function builds a url for redirect, incorporating search parameters. This solved a difficult problem of returning 
    # to the BlockList of the same project after e.g. deleting or updating a block
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urlencode(get)
    return url

def sorted_nicely(l): 
    """ Sort the given iterable in the way that humans expect. Jeff Atwood""" 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)


def calculate_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time:.6f} seconds")
        return result
    return wrapper
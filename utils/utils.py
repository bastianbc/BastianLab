from django.utils.http import urlencode
from django.urls import reverse

import re

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

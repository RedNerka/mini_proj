import json
import os


def openCache(CACHENAME):
    '''
    The function opens the local cache file and reads the content into a Python object.

    Parameters:
    CACHENAME: string
        The name of the cache file.

    Returns:
    list
        A list Python object read from the cache file.
    '''
    try:
        cache_file = open(CACHENAME, 'r')
        cache_contents = cache_file.read()
        cache_list = json.loads(cache_contents)
        cache_file.close()
    except BaseException:
        cache_list = []
    return cache_list


def writeCache(cache_list, CACHENAME):
    '''
    The procedure writes a Python object into a local cache file.

    Parameters:
    cache_list: list
        The list Python object to be stored into the cache file.
    CACHENAME: string
        The name of the cache file.
    '''
    dumped_cache = json.dumps(cache_list)
    fw = open(CACHENAME, "w")
    fw.write(dumped_cache)
    fw.close()


def clearCache(CACHENAME):
    '''
    The procedure clears the content of the cache file.

    Parameters:
    CACHENAME: string
        The name of cache file to be cleared.
    '''
    os.remove(CACHENAME)
    open(CACHENAME, 'w').close()

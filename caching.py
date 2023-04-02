import json
import os


def openCache(CACHENAME):
    try:
        cache_file = open(CACHENAME, 'r')
        cache_contents = cache_file.read()
        cache_list = json.loads(cache_contents)
        cache_file.close()
    except BaseException:
        cache_list = []
    return cache_list


def writeCache(cache_list, CACHENAME):
    dumped_cache = json.dumps(cache_list)
    fw = open(CACHENAME, "w")
    fw.write(dumped_cache)
    fw.close()


def clearCache(CACHENAME):
    os.remove(CACHENAME)
    open(CACHENAME, 'w').close()

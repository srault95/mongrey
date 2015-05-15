try:
    import pymongo
    HAVE_PYMONGO = True
    if pymongo.version_tuple[0] < 3:
        PYMONGO2 = True
    else:
        PYMONGO2 = False
except ImportError:
    HAVE_PYMONGO = False

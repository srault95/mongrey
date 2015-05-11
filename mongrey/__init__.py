try:
    from gevent import monkey
    monkey.patch_all(thread=False)
except:
    pass
import gc, sys


def find_names(obj):
    frame = sys._getframe(1)
    while frame is not None:
        frame.f_locals
        frame = frame.f_back
    result = set()
    for referrer in gc.get_referrers(obj):
        if isinstance(referrer, dict):
            for k, v in referrer.iteritems():
                if v is obj:
                    result.add(k)
    return tuple(result)


if __name__ == '__main__':
    b = c = a = []
    print 'Name for %r: %s' % (a, find_names(a))

import gevent
import random

from datetime import datetime

def tm(f):
    def w(*a, **k):
        s = datetime.now()
        r = f(*a, **k)
        print(datetime.now() - s)
        return r
    return w


def task(pid):
    """
    Some non-deterministic task
    """
    gevent.sleep(random.randint(0,2)*0.001)
    print('Task %s done' % pid)

@tm
def synchronous():
    for i in range(1,10):
        task(i)

@tm
def asynchronous():
    threads = [gevent.spawn(task, i) for i in range(10)]
    gevent.joinall(threads)

print('Synchronous:')
synchronous()

print('Asynchronous:')
asynchronous()
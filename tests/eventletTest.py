import eventlet
eventlet.monkey_patch()

from time import sleep

global f1
global f2

def func2():
    # suspend me and run something else 
    # but switch back to me after 2 seconds (if you can)
    sleep(4.0)
    print "=> func2"
    f2 = eventlet.spawn(func2)
    f2.wait()

def func1():
    # suspend me and run something else 
    # but switch back to me after 2 seconds (if you can)
    eventlet.sleep(0.2)
    print "func1"
    f1 = eventlet.spawn(func1)
    f1.wait()


f1 = eventlet.spawn(func1)
f2 = eventlet.spawn(func2)

f1.wait()

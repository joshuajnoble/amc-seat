import eventlet

global f1

def func1():
    # suspend me and run something else 
    # but switch back to me after 2 seconds (if you can)
    eventlet.sleep(0.2)
    print "func1"
    f1 = eventlet.spawn(func1)
    f1.wait()


f1 = eventlet.spawn(func1)
f1.wait()
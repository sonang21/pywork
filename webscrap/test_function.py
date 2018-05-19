def fn1(msg):
    print("fn1: %s" % msg)

def fn2(msg):
    print("fn2: %s" % msg)

def fn3(msg):
    print("fn3: %s" % msg)


for fn in [fn1, fn2, fn3]:
    fn("test message")

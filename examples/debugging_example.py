from dasst.profiling.debugger import pdb_try_wrapper, try_wrapper
from dasst.profiling import register_logger

logger = register_logger('example')

b = []

@try_wrapper(logger = logger, level = 100)
def test1(a):
    c = a + 5
    return c


@pdb_try_wrapper(Exception)
def test2(num):
    a = 0
    for ind in range(num):
        a *= a

    #global b
    b += 1000*['b']
    return a

if __name__ == '__main__':

    test1(5)
    test1('c')
    test1(b'xx')

    test2(100)
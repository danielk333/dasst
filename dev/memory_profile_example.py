import numpy as np

from dasst.profiling import ProfileMemory
from dasst.profiling import record_memory_usage, format_snapshot, MEMORY_SNAPSHOTS

@record_memory_usage('test1')
def test1(num):
    a = 0
    for ind in range(num):
        a += a
    return a

b = []

@record_memory_usage('test2')
def test2(num):
    a = 0
    for ind in range(num):
        a *= a

    global b
    b += 1000*['b']
    return a


class MyClass:
    def __init__(self, num: int):
        self.data = None
        self.num = num

    def generate(self):
        self.data = np.random.randn(self.num)

    def __str__(self):
        with np.printoptions(precision=3, suppress=True):
            str_ = str(self.data)
        str_ += f'\n size: {self.num}'
        return str_


class MyProfiledClass(MyClass, ProfileMemory):
    pass


obj = MyProfiledClass(100)

obj.start_profiling()
obj.generate()
obj.generate()
snapshot = obj.stop_profiling()

print(format_snapshot(snapshot))

test1(100)
test2(100)

print(MEMORY_SNAPSHOTS)

print(format_snapshot(MEMORY_SNAPSHOTS['test1'][0][0]))
print(format_snapshot(MEMORY_SNAPSHOTS['test2'][0][0]))
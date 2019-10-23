
from dasst.profiling import record_execution_time, format_time_record, EXECUTION_TIMES
from dasst.profiling import function_log_call, register_logger

my_logger = register_logger('test_logger')

@record_execution_time('test1')
def test1(num):
    a = 0
    for ind in range(num):
        a += a
    return a

@record_execution_time('test2')
def test2(num):
    a = 0
    for ind in range(num):
        a *= a
    return a

@function_log_call('{0|num} iterations test', my_logger, 'always')
def run(num):
    for ind in range(num):
        test1(ind)
        test2(ind)

run(100)

print(EXECUTION_TIMES)

print(format_time_record())
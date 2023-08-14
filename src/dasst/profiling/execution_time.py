#!/usr/bin/env python

'''

'''

#Python standard import
import logging
import datetime
import time
import pathlib

#Third party import


#Local import


EXECUTION_TIMES = {}


def format_time_record():
    '''Saves time record to log at info level
    '''
    str_ = ''

    max_key_len = 0
    for key in EXECUTION_TIMES:
        if len(key) > max_key_len:
            max_key_len = len(key)

    header = [' Name ', ' Executions ', ' Mean time [s] ', ' Total time [s] ']
    col_widts = [max_key_len, len(header[1]), 15, 15]
    fmt = [' {}', ' {:d}', ' {:.5e}', ' {:.3e}']

    header_str = ['{:<{}}'.format(name, size) for name, size in zip(header, col_widts)]
    header_str = '|'.join(header_str)

    str_ += 'TIME ANALYSIS' + '\n'
    str_ += '-'*len(header_str) + '\n'
    str_ += header_str + '\n'
    str_ += '-'*len(header_str) + '\n'

    for key, val in EXECUTION_TIMES.items():
            row = [key, val[1], val[0]/val[1], val[0]]
            row_str = [ft.format(data).ljust(size) for ft, data, size in zip(fmt, row, col_widts)]
            str_ += '|'.join(row_str) + '\n'

    return str_


def _add_recorded_time(name, dt):
    global EXECUTION_TIMES
    if name in EXECUTION_TIMES:
        EXECUTION_TIMES[name][0] += dt
        EXECUTION_TIMES[name][1] += 1
    else:
        EXECUTION_TIMES[name] = [dt,1]


def record_execution_time(name):
    def record_time_wrapper(func):
        def timed(*args, **kwargs):
            t0 = time.time()
            ret = func(*args, **kwargs)
            t1 = time.time()

            _add_recorded_time(name, t1-t0)

            return ret

        return timed
    return record_time_wrapper
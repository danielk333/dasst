#!/usr/bin/env python

'''

'''

#Python standard import
import linecache
import os
import tracemalloc

#Third party import


#Local import


MEMORY_SNAPSHOTS = {}


class ProfileMemory:
    def start_profiling(self):
        tracemalloc.start()

    def stop_profiling(self):
        if tracemalloc.is_tracing():
            snapshot = tracemalloc.take_snapshot()
            #overhead tracemalloc.get_tracemalloc_memory()
            tracemalloc.stop()

            return snapshot


def _add_snapshot(name, snapshot):
    global MEMORY_SNAPSHOTS
    if name in MEMORY_SNAPSHOTS:
        MEMORY_SNAPSHOTS[name][0] += [snapshot]
        MEMORY_SNAPSHOTS[name][1] += 1
    else:
        MEMORY_SNAPSHOTS[name] = [[snapshot],1]


def record_memory_usage(name):

    def memory_usage_wrapper(func):
        def profiled(*args, **kwargs):
            tracemalloc.start()

            ret = func(*args, **kwargs)

            if tracemalloc.is_tracing():
                snapshot = tracemalloc.take_snapshot()
                #overhead tracemalloc.get_tracemalloc_memory()
                tracemalloc.stop()

                _add_snapshot(name, snapshot)

            return ret

        return profiled
    return memory_usage_wrapper


def format_snapshot(snapshot, key_type='lineno', limit=10, filter_list=[]):
    str_ = ''
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    for filt in filter_list:
        snapshot = snapshot.filter_traces((
            tracemalloc.Filter(False, filt),
        ))
    top_stats = snapshot.statistics(key_type)

    str_ += f'Top {limit} lines\n'
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]

        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        str_ += f'#{index}: {filename}:{frame.lineno}: {stat.size/1024:.1f} KiB\n'
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            str_ += f'    {line}\n'

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        str_ += f'{len(other)} other: {size/1024:.1f} KiB\n'
    total = sum(stat.size for stat in top_stats)
    str_ += f'Total allocated size: {total/1024:.1f} KiB\n'

    return str_
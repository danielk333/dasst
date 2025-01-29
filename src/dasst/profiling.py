"""
Package-wide execution time profiling system.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Module containing profiling systems using yappi

"""
import pathlib
import os
import time
import logging
from functools import wraps
import linecache
import tracemalloc

try:
    import yappi
except ImportError:
    yappi = None

MEMORY_SNAPSHOTS = {}

file_logger = logging.getLogger(__name__)

PACKAGE_PATH = str(pathlib.Path(__file__).parent)
START_TIME = None


def _path_to_module(path):
    if PACKAGE_PATH not in path:
        return ""
    stem = pathlib.Path(path).stem
    path = "pyant" + os.sep + path.replace(PACKAGE_PATH, "").strip(os.sep)
    module = path.split(os.sep)
    module[-1] = stem
    return ".".join(module)


def check_yappi(func):
    def checked_func(*args, **kwargs):
        if yappi is None:
            raise ImportError("'yappi' not installed, please install to profile")
        return func(*args, **kwargs)

    return checked_func


@check_yappi
def profile():
    global START_TIME
    START_TIME = time.time()
    yappi.set_clock_type("cpu")
    yappi.start()


@check_yappi
def get_profile(modules=None):
    if modules is None:
        modules = ["dasst"]
    stats = yappi.get_func_stats(
        filter_callback=lambda x: any(
            list(_path_to_module(x.module).startswith(mod) for mod in modules)
        ),
    )
    stats = stats.sort("ttot", "desc")

    total = time.time() - START_TIME
    return stats, total


def print_profile(stats, total=None):
    header = [
        "Name",
        "Module",
        "Calls",
        "Total [s]",
        "Function [s]",
        "Average [s]",
    ]
    column_sizes = [len(title) for title in header]
    formats = [""] * 3 + ["1.4e"] * 3

    if total is not None:
        header += ["Total [%]"]
        column_sizes += [len(header[-1])]
        formats += ["2.3f"]

    if total is None:
        total = 1

    for ind in range(3, len(header)):
        if column_sizes[ind] < 6:
            column_sizes[ind]

    datas = [
        (
            fn.name,
            _path_to_module(fn.module),
            f"{fn.ncall}",
            fn.ttot,
            fn.tsub,
            fn.tavg,
            fn.ttot / total * 100,
        )
        for fn in stats
    ]
    for data in datas:
        for ind in range(3):
            if column_sizes[ind] < len(data[ind]):
                column_sizes[ind] = len(data[ind])

    _str = " | ".join([f"{title:^{size}}" for title, size in zip(header, column_sizes)])
    print(_str)
    print("-" * len(_str))

    for data in datas:
        _str = " | ".join(
            [
                f"{x:{fmt}}".ljust(size)
                for x, size, fmt in zip(data[: len(header)], column_sizes, formats)
            ]
        )
        print(_str)


@check_yappi
def profile_stop(clear=True):
    yappi.stop()
    if clear:
        global START_TIME
        START_TIME = None
        yappi.clear_stats()


def log(logger, level):
    """Decorator that logs the function call at the desired level"""

    def log_func(func):
        @wraps(func)
        def logged_func(*args, **kwargs):
            logger.log(level, f'Function "{func.__name__}" called')
            return func(*args, **kwargs)

        return logged_func

    return log_func


def _add_snapshot(name, snapshot):
    global MEMORY_SNAPSHOTS
    if name in MEMORY_SNAPSHOTS:
        MEMORY_SNAPSHOTS[name].append(snapshot)
    else:
        MEMORY_SNAPSHOTS[name] = [snapshot]


def record_memory_usage(name):
    def memory_usage_wrapper(func):
        def profiled(*args, **kwargs):
            tracemalloc.start()

            ret = func(*args, **kwargs)

            if tracemalloc.is_tracing():
                snapshot = tracemalloc.take_snapshot()
                # overhead tracemalloc.get_tracemalloc_memory()
                tracemalloc.stop()

                _add_snapshot(name, snapshot)

            return ret

        return profiled

    return memory_usage_wrapper


def format_snapshot(snapshot, key_type="lineno", limit=10, filter_list=[]):
    str_ = ""
    snapshot = snapshot.filter_traces(
        (
            tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
            tracemalloc.Filter(False, "<unknown>"),
        )
    )
    for filt in filter_list:
        snapshot = snapshot.filter_traces((tracemalloc.Filter(False, filt),))
    top_stats = snapshot.statistics(key_type)

    str_ += f"Top {limit} lines\n"
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]

        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        str_ += f"#{index}: {filename}:{frame.lineno}: {stat.size/1024:.1f} KiB\n"
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            str_ += f"    {line}\n"

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        str_ += f"{len(other)} other: {size/1024:.1f} KiB\n"
    total = sum(stat.size for stat in top_stats)
    str_ += f"Total allocated size: {total/1024:.1f} KiB\n"

    return str_

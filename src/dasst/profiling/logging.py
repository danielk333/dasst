#!/usr/bin/env python

'''

'''

#Python standard import
import logging
import datetime
import time
import pathlib

#Third party import
try:
    from mpi4py import MPI
    PROCESS_ID = MPI.COMM_WORLD.Get_rank()
except ImportError:
    MPI = None
    PROCESS_ID = 0


#Local import


LOGGERS = {}

def add_logging_level(num, name):
    def fn(self, message, *args, **kwargs):
        if self.isEnabledFor(num):
            self._log(num, message, args, **kwargs)
    logging.addLevelName(num, name)
    setattr(logging, name, num)
    return fn

logging.Logger.always = add_logging_level(100, 'ALWAYS')


def set_logger_level(logger, level):
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def set_logger(logger, **kwargs):
    if 'level' in kwargs:
        set_logger_level(logger, level=kwargs['level'])
    if 'logpath' in kwargs:
        if not isinstance(kwargs['logpath'], pathlib.Path):
            kwargs['logpath'] = pathlib.Path(kwargs['logpath'])
        enable_logfile(
            logger = logger,
            log_fname = kwargs['logpath'],
            level = kwargs.get('file_level', logging.INFO),
        )


def set_loggers(**kwargs):
    for name, logger in LOGGERS.items():
        set_logger(logger, **kwargs)


def enable_logfile(logger, log_fname, level=logging.INFO):
    if not isinstance(log_fname, pathlib.Path):
        log_fname = pathlib.Path(log_fname)

    fh = logging.FileHandler(log_fname)
    fh.setLevel(level)
    form_fh = logging.Formatter(
        '%(asctime)s PID{} %(levelname)-8s; %(message)s'.format(PROCESS_ID),
        '%Y-%m-%d %H:%M:%S'
        )
    fh.setFormatter(form_fh)
    logger.addHandler(fh) #id 0



def register_logger(
        name,
        level = logging.INFO,
    ):
    '''Returns a logger object
    '''

    logname = name.replace(' ', '_')

    now = datetime.datetime.now()
    datetime_str = now.strftime("%Y-%m-%d_at_%H-%M")

    logger = logging.getLogger(logname)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    form_ch = logging.Formatter('PID{} %(levelname)-8s; %(message)s'.format(PROCESS_ID))
    ch.setFormatter(form_ch)
    logger.addHandler(ch) #id 0

    global LOGGERS
    LOGGERS[name] = logger

    return logger

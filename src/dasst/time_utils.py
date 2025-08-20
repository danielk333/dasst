import time
import numpy as np


sec = np.timedelta64(1000000000, "ns")
"""numpy.datetime64: Interval of 1 second
"""


def unix_to_jd(unix):
    """Convert Unix time to JD UT1

    Constant is due to 0h Jan 1, 1970 = 2440587.5 JD

    :param float/numpy.ndarray unix: Unix time in seconds.
    :return: Julian Date UT1
    :rtype: float/numpy.ndarray
    """
    return unix / 86400.0 + 2440587.5


def npdt_to_date(dt):
    """
    Converts a numpy datetime64 value to a date tuple

    :param numpy.datetime64 dt: Date and time (UTC) in numpy datetime64 format

    :return: tuple (year, month, day, hours, minutes, seconds, microsecond)
             all except usec are integer
    """

    t0 = np.datetime64("1970-01-01", "s")
    ts = (dt - t0) / sec

    it = int(np.floor(ts))
    usec = 1e6 * (dt - (t0 + it * sec)) / sec

    tm = time.localtime(it)
    return tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec, usec


def npdt_to_mjd(dt):
    """
    Converts a numpy datetime64 value (UTC) to a modified Julian date
    """
    return (dt - np.datetime64("1858-11-17")) / np.timedelta64(1, "D")


def mjd_to_npdt(mjd):
    """
    Converts a modified Julian date to a numpy datetime64 value (UTC)
    """
    day = np.timedelta64(24 * 3600 * 1000 * 1000, "us")
    return np.datetime64("1858-11-17") + day * mjd


def unix_to_npdt(unix):
    return np.datetime64("1970-01-01") + np.timedelta64(1000 * 1000, "us") * unix


def npdt_to_unix(dt):
    return (dt - np.datetime64("1970-01-01")) / np.timedelta64(1, "s")


def jd_to_unix(jd_ut1):
    """Convert JD UT1 time to Unix time

    Constant is due to 0h Jan 1, 1970 = 2440587.5 JD

    :param float/numpy.ndarray jd_ut1: Julian Date UT1
    :return: Unix time in seconds
    :rtype: float/numpy.ndarray
    """
    return (jd_ut1 - 2440587.5) * 86400.0


def jd_to_mjd(jd):
    """Convert Julian Date (relative 12h Jan 1, 4713 BC) to
    Modified Julian Date (relative 0h Nov 17, 1858)"""
    return jd - 2400000.5


def mjd_to_jd(mjd):
    """Convert Modified Julian Date (relative 0h Nov 17, 1858) to
    Julian Date (relative 12h Jan 1, 4713 BC)"""
    return mjd + 2400000.5


def mjd_to_j2000(mjd_tt):
    """Convert from Modified Julian Date to days past J2000.

    :param float/numpy.ndarray mjd_tt: MJD in TT
    :return: Days past J2000
    :rtype: float/numpy.ndarray
    """
    return mjd_to_jd(mjd_tt) - 2451545.0

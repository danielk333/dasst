#!/usr/bin/env python

'''

'''

#Python standard import


#Third party import
import numpy as np


#Local import


sec = np.timedelta64(1000000000, 'ns')
'''numpy.datetime64: Interval of 1 second
'''

gps0_tai = np.datetime64('1980-01-06 00:00:19')
'''numpy.datetime64: Epoch of GPS time, in TAI
'''


leapseconds = np.array([
    '1972-01-01T00:00:00',
    '1972-07-01T00:00:00',
    '1973-01-01T00:00:00',
    '1974-01-01T00:00:00',
    '1975-01-01T00:00:00',
    '1976-01-01T00:00:00',
    '1977-01-01T00:00:00',
    '1978-01-01T00:00:00',
    '1979-01-01T00:00:00',
    '1980-01-01T00:00:00',
    '1981-07-01T00:00:00',
    '1982-07-01T00:00:00',
    '1983-07-01T00:00:00',
    '1985-07-01T00:00:00',
    '1988-01-01T00:00:00',
    '1990-01-01T00:00:00',
    '1991-01-01T00:00:00',
    '1992-07-01T00:00:00',
    '1993-07-01T00:00:00',
    '1994-07-01T00:00:00',
    '1996-01-01T00:00:00',
    '1997-07-01T00:00:00',
    '1999-01-01T00:00:00',
    '2006-01-01T00:00:00',
    '2009-01-01T00:00:00',
    '2012-07-01T00:00:00',
    '2015-07-01T00:00:00',
    '2017-01-01T00:00:00',
], dtype='M8[ns]')
'''numpy.ndarray: Leapseconds added since 1972. 

Leapseconds code from gdar by Norut/NORCE
Contributed by Tom Grydeland <tgry@norceresearch.no>
Modified by Daniel Kastinen

Must be maintained manually.

*Source:* `tai-utc <ftp://maia.usno.navy.mil/ser7/tai-utc.dat>`_
'''


def leapseconds_before(ytime, tai=False):
    '''Calculate the number of leapseconds has been added before given date.
    '''
    leaps = leapseconds_tai if tai else leapseconds

    if np.isscalar(ytime):
        return np.sum(leaps <= ytime) + 9
    else:
        rval = np.sum(leaps[np.newaxis, :] <= ytime.ravel()[..., np.newaxis], 1) + 9
        rval.shape = ytime.shape
        return rval


def tai_to_utc(ytime):
    '''TAI to UTC conversion using Leapseconds data.
    '''
    return ytime - leapseconds_before(ytime, tai=True)*sec

def utc_to_tai(ytime):
    '''UTC to TAI conversion using Leapseconds data.
    '''
    return ytime + leapseconds_before(ytime)*sec


leapseconds_tai = utc_to_tai(leapseconds)
'''numpy.ndarray: Leapseconds in TAI. 

This can only be initialized after utc_to_tai has been defined.

Leapseconds code from gdar by Norut/NORCE
Contributed by Tom Grydeland <tgry@norceresearch.no>
Modified by Daniel Kastinen
'''



def mjd_to_gmst(mjd_UT1):
    '''Returns the Greenwich Mean Sidereal Time (rotation of the earth) at a specific UTC Modified Julian Date.
    Defined as the hour angle between the meridian of Greenwich and mean equinox of date at 0 h UT1
    
    :param float/numpy.ndarray mjd_UT1: UTC Modified Julian Date.
    :return: Greenwich Mean Sidereal Time in radians between 0 and :math:`2\pi`.
    
    *Reference:* Montenbruck & Gill: Satellite orbits
    '''
    frac = lambda a: a - np.floor(a)
    
    secs = 86400.0 # Seconds per day
    MJD_J2000 = 51544.5

    # Mean Sidereal Time
    mjd_0 = np.floor(mjd_UT1)
    UT1 = secs*(mjd_UT1 - mjd_0)
    T_0 = (mjd_0 - MJD_J2000)/36525.0
    T = (mjd_UT1 - MJD_J2000)/36525.0
    
    gmst = 24110.54841 \
        + 8640184.812866*T_0 \
        + 1.002737909350795*UT1 \
        + np.multiply(np.multiply((0.093104 - 6.2e-6*T), T), T)
                
    return 2*np.pi*frac(gmst/secs)



def unix_to_jd(unix):
    '''Convert Unix time to JD UT1

    Constant is due to 0h Jan 1, 1970 = 2440587.5 JD

    :param float/numpy.ndarray unix: Unix time in seconds.
    :return: Julian Date UT1
    :rtype: float/numpy.ndarray
    '''
    return unix/86400.0 + 2440587.5


def npdt_to_date(dt):
    '''    
    Converts a numpy datetime64 value to a date tuple

    :param numpy.datetime64 dt: Date and time (UTC) in numpy datetime64 format

    :return: tuple (year, month, day, hours, minutes, seconds, microsecond)
             all except usec are integer
    '''

    t0 = np.datetime64('1970-01-01', 's')
    ts = (dt - t0)/sec

    it = int(np.floor(ts))
    usec = 1e6 * (dt - (t0 + it*sec))/sec

    tm = time.localtime(it)
    return tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec, usec


def npdt_to_mjd(dt):
    '''
    Converts a numpy datetime64 value (UTC) to a modified Julian date
    '''
    return (dt - np.datetime64('1858-11-17'))/np.timedelta64(1, 'D')


def mjd_to_npdt(mjd):
    '''
    Converts a modified Julian date to a numpy datetime64 value (UTC)
    '''
    day = np.timedelta64(24*3600*1000*1000, 'us')
    return np.datetime64('1858-11-17') + day * mjd


def unix_to_npdt(unix):
    return np.datetime64('1970-01-01') + np.timedelta64(1000*1000,'us')*unix

def npdt_to_unix(dt):
    return (dt - np.datetime64('1970-01-01'))/np.timedelta64(1,'s')


def jd_to_unix(jd_ut1):
    '''Convert JD UT1 time to Unix time
    
    Constant is due to 0h Jan 1, 1970 = 2440587.5 JD

    :param float/numpy.ndarray jd_ut1: Julian Date UT1
    :return: Unix time in seconds
    :rtype: float/numpy.ndarray
    '''
    return (jd_ut1 - 2440587.5)*86400.0


def jd_to_mjd(jd):
    '''Convert Julian Date (relative 12h Jan 1, 4713 BC) to Modified Julian Date (relative 0h Nov 17, 1858)
    '''
    return jd - 2400000.5


def mjd_to_jd(mjd):
    '''Convert Modified Julian Date (relative 0h Nov 17, 1858) to Julian Date (relative 12h Jan 1, 4713 BC)
    '''
    return mjd + 2400000.5


def mjd_to_j2000(mjd_tt):
    '''Convert from Modified Julian Date to days past J2000.
    
    :param float/numpy.ndarray mjd_tt: MJD in TT
    :return: Days past J2000
    :rtype: float/numpy.ndarray
    '''
    return mjd_to_jd(mjd_tt) - 2451545.0


"""Module that implements the variables and criterions to discriminate between
orbits of comets and asteroids. This is a crude first order check on orbits if
they are likely of cometary or asteroidal origin.

"""

import numpy as np
import pyorb

"""Semi-major axis of Jupiter in AU
"""
SEMI_MAJOR_JUP = 5.2038
SIDEREAL_YEAR_J2000 = 365.256363004
GAUSS_GRAV_K = (
    2 * np.pi / (SIDEREAL_YEAR_J2000 * np.sqrt(1 + pyorb.M_earth / pyorb.M_sol))
)


def K_i(a, e, i):
    """K-i criterion [1]

    ASSUMES UNITS IN AU and DEGREES

    _[1] Jopek, T. J., and Williams, I. P. (2013). Stream and sporadic meteoroids
        associated with near-Earth objects.
        Mon. Not. R. Astron. Soc. 430, 2377-2389.
        doi:10.1093/mnras/stt057
    """
    K = np.log(a * (1 + e) / (1 - e)) - 1
    return np.logical_or(K > 0, i > 75)


def P_i(P, e, i):
    """P-i criterion [1]

    ASSUMES UNITS in YEARS and DEGREES

    _[1] Jopek, T. J., and Williams, I. P. (2013). Stream and sporadic meteoroids
        associated with near-Earth objects.
        Mon. Not. R. Astron. Soc. 430, 2377-2389.
        doi:10.1093/mnras/stt057
    """
    return np.logical_or(P * e > 2.5, i > 75)


def Q_i(a, e, i):
    """Q-i criterion [1]

    ASSUMES UNITS IN AU and DEGREES

    _[1] Jopek, T. J., and Williams, I. P. (2013). Stream and sporadic meteoroids
        associated with near-Earth objects.
        Mon. Not. R. Astron. Soc. 430, 2377-2389.
        doi:10.1093/mnras/stt057
    """
    Q = a * (1 + e)
    return np.logical_or(Q < 4.6, i > 75)


def E_i(a, i):
    """E-i criterion [1]

    ASSUMES UNITS IN AU and DEGREES

    _[1] Jopek, T. J., and Williams, I. P. (2013). Stream and sporadic meteoroids
        associated with near-Earth objects.
        Mon. Not. R. Astron. Soc. 430, 2377-2389.
        doi:10.1093/mnras/stt057
    """
    E = -(GAUSS_GRAV_K**2) / (2 * a)
    return np.logical_or(E > -5.28e-5, i > 75)


def T_jupiter_i(a, e, i):
    """T-i criterion [1]

    ASSUMES UNITS IN AU and DEGREES

    _[1] Jopek, T. J., and Williams, I. P. (2013). Stream and sporadic meteoroids
        associated with near-Earth objects.
        Mon. Not. R. Astron. Soc. 430, 2377-2389.
        doi:10.1093/mnras/stt057
    """
    Tj = 1 / a + 2 * SEMI_MAJOR_JUP ** (-1.5) * np.sqrt(a * (1 - e**2)) * np.cos(
        np.radians(i)
    )
    return np.logical_or(Tj < 0.58, i > 75)

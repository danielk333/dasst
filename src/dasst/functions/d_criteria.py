#!/usr/bin/env python

"""Implementation of standard D-criteria

"""

# Python standard import


# Third party import
import numpy as np

import pyorb

# Local import


def D_SH(orb_a, orb_b):
    """Southworth and Hawkings, 1963

    :param orb_a pyorb.Orbit: First input orbit into criterion calculation
    :param orb_b pyorb.Orbit: Second input orbit into criterion calculation
    :return: Criterion value

    #TODO: make degrees vs radians safe function
    #TODO: make sure correct units are always used (distance in AU?)
    """

    Iabsin = (2 * np.sin((orb_b.i - orb_a.i) * 0.5)) ** 2 + np.sin(orb_a.i) * np.sin(
        orb_b.i
    ) * (2 * np.sin((orb_b.Omega - orb_a.Omega) * 0.5)) ** 2
    I_ab = np.arcsin(0.5 * np.sqrt(Iabsin)) * 2
    PI_ab = (
        orb_b.omega
        - orb_a.omega
        + 2
        * np.arcsin(
            np.cos((orb_b.i - orb_a.i) * 0.5)
            * np.sin((orb_b.Omega - orb_a.Omega) * 0.5)
            / np.cos(I_ab * 0.5)
        )
    )

    D = 0.0
    D += (orb_b.e - orb_a.e) ** 2
    D += (orb_b.a * (1 - orb_b.e) - orb_a.a * (1 - orb_a.e)) ** 2
    D += (2 * np.sin(I_ab * 0.5)) ** 2
    D += ((orb_b.e + orb_a.e) * np.sin(PI_ab * 0.5)) ** 2

    return D


def D_V(orb_a, orb_b, weights=None):
    """Jopek, Rudawska, Bartczak, 2008

    :param orb_a pyorb.Orbit: First input orbit into criterion calculation
    :param orb_b pyorb.Orbit: Second input orbit into criterion calculation
    :return: Criterion value

    #TODO: make sure correct units
    """

    mu_a = orb_a.G * (orb_a.M0 + orb_a.m)
    mu_b = orb_b.G * (orb_b.M0 + orb_b.m)

    # area vector
    c_a = np.cross(orb_a.cartesian[:3, ...], orb_a.cartesian[3:, ...], axis=0)
    c_b = np.cross(orb_b.cartesian[:3, ...], orb_b.cartesian[3:, ...], axis=0)

    # Laplace-Runge-Lenz vector
    ra_norm = np.linalg.norm(orb_a.cartesian[3:, ...], axis=0)
    lrl_a = (
        np.cross(orb_a.cartesian[3:, ...], c_a, axis=0) / mu_a
        - orb_a.cartesian[3:, ...] / ra_norm
    )

    rb_norm = np.linalg.norm(orb_b.cartesian[3:, ...], axis=0)
    lrl_b = (
        np.cross(orb_b.cartesian[3:, ...], c_b, axis=0) / mu_b
        - orb_b.cartesian[3:, ...] / rb_norm
    )

    # Orbital energy
    E_a = 0.5 * np.linalg.norm(orb_a.cartesian[3:, ...], axis=0) ** 2 - mu_a / ra_norm
    E_b = 0.5 * np.linalg.norm(orb_b.cartesian[3:, ...], axis=0) ** 2 - mu_b / rb_norm

    Oa = np.empty((7, orb_a.num), dtype=np.float64)
    Oa[:3, ...] = c_a
    Oa[3:6, ...] = lrl_a
    Oa[6, ...] = E_a

    Ob = np.empty((7, orb_b.num), dtype=np.float64)
    Ob[:3, ...] = c_b
    Ob[3:6, ...] = lrl_b
    Ob[6, ...] = E_b

    D = (Oa - Ob) ** 2
    D[2, ...] *= 1.5
    D[6, ...] *= 2
    if weights is not None:
        D = D * weights[:, None]

    D = np.sqrt(np.sum(D, axis=0))

    return D

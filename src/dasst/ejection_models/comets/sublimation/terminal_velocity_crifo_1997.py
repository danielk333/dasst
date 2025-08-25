"""Equations used in calculating dust particle terminal velocity as from [1] and [2]

[1]: https://doi.org/10.1006/icar.1997.5714

Originally authored by Francisca Emel Tuzcuoglu during IRF internship 2025
Maintained and modified by Daniel Kastinen thereafter
"""

import numpy as np
import scipy.constants as const


def critical_radius_crifo_1997(f_rh, rh, T, Rn, cosz, A):
    V_g0 = np.sqrt(const.GAMMA * const.k * T / const.M_KG)
    factor1 = const.M_AMU * (1 - A) * const.C_SUN / (const.P_DUST * const.A_S * const.L_S * V_g0)
    factor2 = f_rh * cosz / rh**2
    return factor1 * Rn * factor2


def terminal_velocity_crifo_1997(dust_radii, a_star, T):
    W = np.sqrt((const.GAMMA + 1) / (const.GAMMA - 1) * const.GAMMA * const.k * T / const.M_KG)
    Phi = 1.2 + 0.72 * np.sqrt(dust_radii / a_star)
    return W / Phi

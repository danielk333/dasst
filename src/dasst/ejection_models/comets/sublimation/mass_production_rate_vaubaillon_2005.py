"""Originally authored by Francisca Emel Tuzcuoglu during IRF internship 2025
Maintained and modified by Daniel Kastinen thereafter
"""

# The total mass production rate of grains with radii
# in range [a_1, a_2] ejected by the active surface
# by unit of time in all directions at distance rh in kg/s

import numpy as np
from . import constants as const


def W_Crifo1997(T):
    return np.sqrt((const.GAMMA + 1) / (const.GAMMA - 1) * const.GAMMA * const.K_B * T / const.M_KG)


def A_func_Vaubaillon2005(x, s, a_1, a_2):
    return (a_2 ** (x - s) - a_1 ** (x - s)) / (x - s) if x != s else np.log(a_2 / a_1)


def BETA_Vaubaillon2005(a_star0):
    return 0.72 / np.sqrt(a_star0)


def J_Vaubaillon2005(T, s, a_1, a_2, a_star0):
    return W_Crifo1997(T) / (
        const.ALPHA * A_func_Vaubaillon2005(3, s, a_1, a_2)
        + BETA_Vaubaillon2005(a_star0) * const.I * A_func_Vaubaillon2005(3.5, s, a_1, a_2)
    )


def Qm_Vaubaillon2005(T, s, a_1, a_2, a_star0, Afp0, A_phi, q, rh):
    factor = (
        4
        / 3
        * np.pi
        * const.P_DUST
        * J_Vaubaillon2005(T, s, a_1, a_2, a_star0)
        * Afp0
        / A_phi
        * A_func_Vaubaillon2005(4, s, a_1, a_2)
    )
    return factor * (q / rh) ** const.VAR_INDEX


def factor_rh_func_Vaubaillon2005(q):
    if const.VAR_INDEX != 1:
        factor_rh = (
            q**const.VAR_INDEX
            / (1 - const.VAR_INDEX)
            * (3 ** (1 - const.VAR_INDEX) - q ** (1 - const.VAR_INDEX))
        )
    else:
        factor_rh = q**const.VAR_INDEX * np.log(3 / q)
    return round(factor_rh, 3)


def Mg_tot_Vaubaillon2005(factor_t, factor_rh, T, s, a_1, a_2, a_star0, Afp0, A_phi, q, rh):
    return factor_t * factor_rh * Qm_Vaubaillon2005(T, s, a_1, a_2, a_star0, Afp0, A_phi, q, rh)


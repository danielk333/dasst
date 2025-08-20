"""Originally authored by Francisca Emel Tuzcuoglu during IRF internship 2025
Maintained and modified by Daniel Kastinen thereafter
"""

import numpy as np
from . import constants as const
import scipy.special


def U_Rodionov2002(M0):  # eq given after eq (96)
    return M0 * np.sqrt(const.GAMMA / 2)


def Psat_Panale1984(T):  # eq (7)
    return 3.56e12 * np.exp(-6141.667 / T)  # Pa


def ZHK_Rodionov2002(T_ice):  # eq given after eq (97)
    return Psat_Panale1984(T_ice) / np.sqrt(2 * np.pi * const.M_KG * const.K_B * T_ice)


def P_factor_Rodionov2002(M0, T_ice, T0):  # eq (96)
    return (
        0.5
        - U_Rodionov2002(M0) * np.sqrt(T0 / np.pi / T_ice)
        + (
            (U_Rodionov2002(M0) ** 2 + 0.5) * np.sqrt(T0 / T_ice)
            - (U_Rodionov2002(M0) * np.sqrt(np.pi) / 2)
        )
        * scipy.special.erfc(U_Rodionov2002(M0))
        * np.exp(U_Rodionov2002(M0) ** 2)
    )


def Z_minus_Rodionov2002(M0, T_ice, T0):  # eq (98)
    factor = 1 - 2 * U_Rodionov2002(M0) * np.sqrt(np.pi) * P_factor_Rodionov2002(
        M0, T_ice, T0
    ) * np.sqrt(T_ice / T0)
    return factor * ZHK_Rodionov2002(T_ice)


def Z0_Rodionov2002(M0, T_ice, T0):  # eq (97)
    return ZHK_Rodionov2002(T_ice) - Z_minus_Rodionov2002(M0, T_ice, T0)


def T0_Rodionov2002(M0, T_ice):  # eq (95)
    prefactor = np.sqrt(
        1 + (U_Rodionov2002(M0) * np.sqrt(np.pi) / 2 * (const.GAMMA - 1) / (const.GAMMA + 1)) ** 2
    ) - (U_Rodionov2002(M0) * np.sqrt(np.pi) / 2 * (const.GAMMA - 1) / (const.GAMMA + 1))
    return prefactor**2 * T_ice


def F_Rodionov2002(A, cosz, rh):
    return (1 - A) * const.C_SUN * np.max(cosz, 0) / (rh**2)  # eq (6)


def T_ice_Energy_Budget_eq_Rodionov2002(T_ice, A, cosz, rh, f, M0):  # eq (7)
    F = F_Rodionov2002(A, cosz, rh)
    T0 = T0_Rodionov2002(M0, T_ice)  # eq (95)
    Z0 = Z0_Rodionov2002(M0, T_ice, T0)
    return const.E * const.SIGMA * T_ice**4 + f * const.A_S * const.L_S_M * Z0 - F


def T_ice_bisection_method(A, cosz, rh, f, M0, tol=1.48e-8):
    lower_bound = 1
    upper_bound = 600

    error = abs(upper_bound - lower_bound)

    while error > tol:

        mid = (lower_bound + upper_bound) / 2

        if (
            T_ice_Energy_Budget_eq_Rodionov2002(lower_bound, A, cosz, rh, f, M0)
            * T_ice_Energy_Budget_eq_Rodionov2002(upper_bound, A, cosz, rh, f, M0)
            > 0
        ):
            print("Bisection method failed, no root or multiple roots found")
            return np.nan

        elif (
            T_ice_Energy_Budget_eq_Rodionov2002(mid, A, cosz, rh, f, M0)
            * T_ice_Energy_Budget_eq_Rodionov2002(lower_bound, A, cosz, rh, f, M0)
            <= 0
        ):
            upper_bound = mid
            error = abs(upper_bound - lower_bound)

        elif (
            T_ice_Energy_Budget_eq_Rodionov2002(mid, A, cosz, rh, f, M0)
            * T_ice_Energy_Budget_eq_Rodionov2002(upper_bound, A, cosz, rh, f, M0)
            < 0
        ):
            lower_bound = mid
            error = abs(upper_bound - lower_bound)

        else:
            print("Something went wrong")
            return np.nan

    return (lower_bound + upper_bound) / 2


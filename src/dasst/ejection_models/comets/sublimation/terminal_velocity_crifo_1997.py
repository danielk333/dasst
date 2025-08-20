"""Equations used in calculating dust particle terminal velocity as from [1] and [2]

[1]: https://doi.org/10.1006/icar.1997.5714

Originally authored by Francisca Emel Tuzcuoglu during IRF internship 2025
Maintained and modified by Daniel Kastinen thereafter
"""

import numpy as np
import matplotlib.pyplot as plt
from . import constants as const


def dust_radius(n, a_min, a_max):
    return np.random.uniform(a_min, a_max, int(n))


def critical_radius_Crifo1997(f_rh, rh, T, Rn, cosz, A):
    V_g0 = np.sqrt(const.GAMMA * const.K_B * T / const.M_KG)
    factor1 = const.M_AMU * (1 - A) * const.C_SUN / (const.P_DUST * const.A_S * const.L_S * V_g0)
    factor2 = f_rh * cosz / rh**2
    return factor1 * Rn * factor2


def terminal_velocity_Crifo1997(dust_radii, a_star, T):
    W = np.sqrt((const.GAMMA + 1) / (const.GAMMA - 1) * const.GAMMA * const.K_B * T / const.M_KG)
    Phi = 1.2 + 0.72 * np.sqrt(dust_radii / a_star)
    return W / Phi


def terminal_velocity_histogram(terminal_velocity, comet_name):
    fig = plt.figure()
    plt.hist(terminal_velocity, bins="fd", color="white", edgecolor="black")
    plt.xlabel("Terminal velocity (m/s)")
    plt.ylabel("Number of particles")
    plt.title(f"Terminal velocity histogram of {comet_name}")
    return fig


def solar_zenith_angle_draw(n):
    z = np.arccos(np.random.rand(n))
    return np.degrees(z)


def t_vs_z_plot(T, z, rh):
    valid = np.isfinite(T)
    fig = plt.figure()
    plt.scatter(z[valid], T[valid], s=20, alpha=0.8)
    plt.xlabel(r"Solar zenith angle $z$ (deg)", fontsize=18)
    plt.ylabel(r"Gas temperature $T$ (K)", fontsize=18)
    plt.title(rf"$T$ vs $z$ ($r_h$ = {rh})", fontsize=20)
    return fig


def vt_vs_z_plot(terminal_velocities, z, a_d, rh):
    valid = np.isfinite(terminal_velocities)
    fig = plt.figure()
    plt.scatter(z[valid], terminal_velocities[valid], s=20, alpha=0.8)
    plt.xlabel(r"Solar zenith angle $z$ (deg)", fontsize=18)
    plt.ylabel(r"Terminal velocity $V_\infty$ (m/s)", fontsize=18)
    plt.title(rf"$V_\infty$ vs $z$ (for dust size = {a_d} and $r_h$ = {rh})", fontsize=20)
    return fig


def vt_hist_plot(terminal_velocities, z, a_d, rh):
    valid = np.isfinite(terminal_velocities)
    fig = plt.figure()
    plt.hist(terminal_velocities[valid], bins=int(np.sqrt(len(terminal_velocities))))
    plt.xlabel(r"Terminal velocity $V_\infty$ (m/s)", fontsize=18)
    plt.title(rf"$V_\infty$ distribtuion (for dust size = {a_d} and $r_h$ = {rh})", fontsize=20)
    return fig

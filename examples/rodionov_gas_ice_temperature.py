import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from dasst.ejection_models.comets.sublimation import temperature_rodionov_2002 as temp
import dasst.constants


A_S = 1
alpha_S = 1
epsilon = 0.9
W = 0
gamma = 4 / 3
m_kg = 18 * 1.66053906660e-27


def residual_Tice(T, E_in, f, M0):
    E_out = temp.ice_temperature_energy_budget_rodionov_2002(
        T,
        f,
        dasst.constants.L_S,
        alpha_S,
        M0,
        epsilon,
        W,
        gamma,
        m_kg,
    )
    return E_in - E_out


def solve_Tice(F, M0, f=1, Ti_lo=1, Ti_hi=600):
    return brentq(residual_Tice, Ti_lo, Ti_hi, args=(F, f, M0), xtol=1e-8, maxiter=200)


def TempMachF_plot_Rodionov2002(
    f=1, nM0=201, nF=301, M0_min=0.01, M0_max=1, Fmin_norm=0.01, Fmax_norm=3
):

    M0_vals = np.logspace(np.log10(M0_min), np.log10(M0_max), nM0)
    F_vals = np.logspace(np.log10(Fmin_norm), np.log10(Fmax_norm), nF) * dasst.constants.C_SUN

    T0_map = np.full((nM0, nF), np.nan, dtype=float)

    pbar = tqdm(total=len(M0_vals)*len(F_vals))
    for i, M0 in enumerate(M0_vals):
        for j, F in enumerate(F_vals):
            Ti = solve_Tice(F, M0, f=f)
            pbar.update(1)
            if np.isfinite(Ti):
                T0_map[i, j] = temp.gas_temperature_rodionov_2002(M0, Ti, gamma)
    pbar.close()
    X, Y = np.meshgrid(F_vals / dasst.constants.C_SUN, M0_vals)
    fig, ax = plt.subplots()
    h = ax.contourf(X, Y, T0_map, levels=30, cmap="turbo")
    cb = fig.colorbar(h, ax=ax, label=r"$T$ [K]")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(Fmin_norm, Fmax_norm)
    ax.set_ylim(M0_min, M0_max)
    ax.set_xlabel(r"$F/C_\odot$", fontsize=18)
    ax.set_ylabel(r"$M_0$", fontsize=18)
    ax.set_title(
        r"Initial Gas Temperature ($T$) vs $F/C_\odot$ and Mach Number ($M_0$)", fontsize=20
    )

    ax.tick_params(axis="both", labelsize=14)
    cb.ax.tick_params(labelsize=14)
    cb.set_label(r"$T_0$ [K]", fontsize=18)

    plt.show()


TempMachF_plot_Rodionov2002()

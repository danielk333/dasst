import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from dasst.ejection_models.comets.sublimation import terminal_velocity_crifo_1997 as vel
from dasst.ejection_models.comets.sublimation import temperature_rodionov_2002 as temp


def solar_zenith_angle_draw(n):
    """Draws samples according to the area element of solar zenith angle for a spherical body"""
    z = np.arccos(np.random.rand(n))
    return np.degrees(z)


comet_name = "55P/Tempel-Tuttle"

# dust radius in meters
dust_radius = 0.5e-3

# Parameters for 55P/Tempel-Tuttle
rh = 2  # heliocentric distance in AU
M0 = 1
Rn = 1.8e3  # nucleus radius in meters
f_rh = 0.24  # active surface icy area fraction
A = 0.04  # albedo
gamma = 4 / 3
m_kg = 18 * 1.66053906660e-27
rho_d = 1000  # dust density kg/m^3
rho_n = 1.13e13 / (4/3 * np.pi * Rn**3)  # nucleus density kg/m^3

z_vec = np.linspace(0, 90, num=1000)  # n number of solar zenith angles in degrees
z_samp = solar_zenith_angle_draw(10_000)  # n number of solar zenith angles in degrees


def calc_ejection(z):
    cosz = np.cos(np.radians(z))
    n = len(z)

    T_ice = np.full(n, np.nan, dtype=np.float64)
    for i in tqdm(range(n), total=n):
        T_ice[i] = temp.solve_ice_temperature_rodionov_2002(A, cosz[i], rh, f_rh, M0, gamma, m_kg)
    T = temp.gas_temperature_rodionov_2002(M0, T_ice, gamma)  # initial gas temperature in K

    # Calculate the critical radius from Crifo's formula (1997)
    critical_radius = vel.critical_radius_crifo_1997(f_rh, rh, T, Rn, cosz, A, gamma, m_kg, rho_d)

    # Calculate the maximum particle size
    # todo: something wrong here
    max_particle = vel.maximum_particle_crifo_1997(
        f_rh,
        rh,
        T,
        Rn,
        cosz,
        A,
        gamma,
        m_kg,
        rho_d,
        rho_n,
    )

    # Calculate the terminal velocity from Crifo's formula (1997) using the critical radius
    terminal_velocities = vel.terminal_velocity_crifo_1997(
        dust_radius, critical_radius, T, gamma, m_kg
    )
    return T_ice, T, critical_radius, terminal_velocities, max_particle


T_ice, T, critical_radius, terminal_velocities, max_particle = calc_ejection(z_vec)
_, _, _, V_inf_samp, _ = calc_ejection(z_samp)

valid_T = np.isfinite(T)
valid_V = np.isfinite(terminal_velocities)
valid_max = np.isfinite(max_particle)

fig, ax = plt.subplots()
ax.plot(z_vec[valid_T], T[valid_T])
ax.set_xlabel(r"Solar zenith angle $z$ (deg)", fontsize=18)
ax.set_ylabel(r"Gas temperature $T$ (K)", fontsize=18)
ax.set_title(rf"$T$ vs $z$ ($r_h$ = {rh})", fontsize=20)

fig, ax = plt.subplots()
ax.plot(z_vec[valid_V], terminal_velocities[valid_V])
ax.set_xlabel(r"Solar zenith angle $z$ (deg)", fontsize=18)
ax.set_ylabel(r"Terminal velocity $V_\infty$ (m/s)", fontsize=18)
ax.set_title(rf"$V_\infty$ vs $z$ (for dust size = {dust_radius} and $r_h$ = {rh})", fontsize=20)

fig, ax = plt.subplots()
ax.semilogy(z_vec[valid_max], max_particle[valid_max])
ax.set_xlabel(r"Solar zenith angle $z$ (deg)", fontsize=18)
ax.set_ylabel(r"Maxumum ejecable particle $a_M$ (m)", fontsize=18)
ax.set_title(rf"$T$ vs $z$ ($r_h$ = {rh})", fontsize=20)

fig, ax = plt.subplots()
ax.hist(V_inf_samp, bins=int(np.sqrt(len(V_inf_samp))))
ax.set_xlabel(r"terminal velocity $v_\infty$ (m/s)", fontsize=18)
ax.set_title(
    rf"$v_\infty$ distribtuion (for dust size = {dust_radius} and $r_h$ = {rh})", fontsize=20
)

plt.show()

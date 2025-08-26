import scipy.constants as const
import matplotlib.pyplot as plt
import numpy as np

from dasst.ejection_models.comets import sublimation
import dasst.constants

helio_distances = np.linspace(0.8, 5, 400)
helio_distance = 1.2
body_radius = 1e3
body_mass = 10e4
particle_bulk_density = 1e3
particle_mass = 1e-7
particle_masses = 10 ** np.linspace(-9, -2, 1000)
m_kg = 18 * 1.66053906660e-27

f_rh = 0.24  # active surface icy area fraction
A = 0.20  # albedo
gamma = 4 / 3
T = 175


def get_vels(dist, dust_mass, zenith_angle):

    massloss = sublimation.whipple_1951.dMdt(
        dist * const.au,
        body_radius,
        albedo=A,
        solar_luminosity=4e26,
        sublimation_heat=dasst.constants.L_S,
    )
    vel_whipple = sublimation.whipple_1951.velocity(
        dist * const.au,
        body_radius,
        body_mass,
        particle_bulk_density,
        dust_mass,
        massloss,
        gas_molecule_mass=m_kg,
        surface_temperature_coeff=300,
        K_drag=26.0 / 9.0,
    )

    particle_radius = np.cbrt(3 / (4 * np.pi) * (dust_mass / particle_bulk_density))
    critical_radius = sublimation.terminal_velocity_crifo_1997.critical_radius_crifo_1997(
        f_rh, dist, T, body_radius, np.cos(np.radians(zenith_angle)), A, gamma, m_kg, particle_bulk_density
    )
    vel_crifo = sublimation.terminal_velocity_crifo_1997.terminal_velocity_crifo_1997(
        particle_radius, critical_radius, T, gamma, m_kg
    )
    return vel_whipple, vel_crifo


vel_whipple, vel_crifo = get_vels(helio_distances, particle_mass, 0)

fig, ax = plt.subplots()

ax.plot(helio_distances, vel_whipple, label="Whipple 1951")
ax.plot(helio_distances, vel_crifo, label="Crifo 1997")
ax.legend()
ax.set_xlabel("Heliocentric distance [AU]")
ax.set_ylabel("Terminal ejection velocity [m/s]")
ax.set_title(
    f"Whipple 1951 vs Crifo 1997 dust ejection model - particle mass = {particle_mass:.2e} kg"
)

za2 = 80
vel_whipple, vel_crifo = get_vels(helio_distance, particle_masses, 0)
_, vel_crifo_2 = get_vels(helio_distance, particle_masses, 60)
fig, ax = plt.subplots()

ax.semilogx(particle_masses, vel_whipple, label="Whipple 1951")
ax.semilogx(particle_masses, vel_crifo, "--", label="Crifo 1997 - Za=0 deg")
ax.semilogx(particle_masses, vel_crifo_2, "--", label=f"Crifo 1997 - Za={za2} deg")
ax.legend()
ax.set_xlabel("Particle mass [kg]")
ax.set_ylabel("Terminal ejection velocity [m/s]")
ax.set_title(
    f"Whipple 1951 vs Crifo 1997 dust ejection model - Heliocentric distance = {helio_distance:.2e} AU"
)
plt.show()

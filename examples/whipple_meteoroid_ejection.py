import scipy.constants as constants
import matplotlib.pyplot as plt
import numpy as np

from dasst.ejection_models.comets import sublimation

helio_distance = np.linspace(0.8, 5, 400)
body_radius = 1e3
body_mass = 10e4
particle_bulk_density = 1e3
particle_mass = 1e-7

massloss = sublimation.whipple_1951.dMdt(
    helio_distance * constants.au,
    body_radius,
    albedo=0.2,
    solar_luminosity=4e26,
    sublimation_heat=1.88e6,
)
vel = sublimation.whipple_1951.velocity(
    helio_distance * constants.au,
    body_radius,
    body_mass,
    particle_bulk_density,
    particle_mass,
    massloss,
    gas_molecule_mass=20 * 1.661e-24 * 1e-3,
    surface_temperature_coeff=300,
    K_drag=26.0 / 9.0,
)

print(f"Whipple model at {helio_distance[0]} AU")
print(f"dM/dt = {massloss[0]} kg/s")
print(f"velocity = {vel[0]} m/s")

fig, axes = plt.subplots(2, 1)
axes[0].plot(helio_distance, massloss)
axes[0].set_xlabel("Heliocentric distance [AU]")
axes[0].set_ylabel("Mass loss [kg/s]")

axes[1].plot(helio_distance, vel)
axes[1].set_xlabel("Heliocentric distance [AU]")
axes[1].set_ylabel("Terminal ejection velocity [m/s]")
fig.suptitle(f"Whipple 1951 dust ejection model - particle mass = {particle_mass:.2e} kg")
plt.show()

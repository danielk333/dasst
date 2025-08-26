import numpy as np
import matplotlib.pyplot as plt

from dasst.ejection_models.comets import sublimation

q = 0.988
rh = np.linspace(q, 3, 1000)

# todo: there is something wrong with the calculation, some parameters are missing, need testing!
print("warning - not yet working")

min_size, max_size = 0.1e-3, 0.5e-3
size_index = 3
active_fraction = 0.24
nucleus_radius = 1.8e3
nucleus_geometric_albedo = 0.04
mach_number = 1
afp_0 = 78.9  # cm
observed_albedo = 0.24
gamma = 4 / 3
m_kg = 18 * 1.66053906660e-27
dust_density = 1e3
alpha_coef = 1.2
index_of_variation = 2.025

n = rh.size

T_ice = 180
T0 = sublimation.gas_temperature_rodionov_2002(mach_number, T_ice, gamma)

a_star0 = sublimation.critical_radius_crifo_1997(
    active_fraction,
    rh,
    T0,
    nucleus_radius,
    1,
    nucleus_geometric_albedo,
    gamma,
    m_kg,
    dust_density,
)
Q_m = sublimation.total_mass_production_vaubaillon_2005(
    T0,
    size_index,
    dust_density,
    min_size,
    max_size,
    a_star0,
    alpha_coef,
    gamma,
    m_kg,
    afp_0,
    observed_albedo,
    q,
    rh,
    index_of_variation,
)

time_of_outgassing = 3.6e7
M_loss_tot = sublimation.total_mass_loss_vaubaillon_2005(
    time_of_outgassing,
    T0,
    size_index,
    dust_density,
    min_size,
    max_size,
    a_star0[0],
    alpha_coef,
    gamma,
    m_kg,
    afp_0,
    observed_albedo,
    q,
    index_of_variation,
    3,
)
print(f"Total mass loss: {M_loss_tot:.2e} kg")

fig, ax = plt.subplots()
ax.semilogy(rh, Q_m, lw=1.5)
ax.set_xlabel("rh", fontsize=18)
ax.set_ylabel(r"$Q_m$ (kg s$^{-1}$)", fontsize=18)
ax.set_title(r"$Q_m$ vs rh", fontsize=20)
ax.grid(alpha=0.5)
plt.show()

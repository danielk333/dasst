import numpy as np
import matplotlib.pyplot as plt

from dasst.ejection_models.comets import sublimation

rh = np.linspace(1.2, 3, 1000)


min_size, max_size = 0.1e-3, 0.5e-3
size_index = 3
active_fraction = 0.24
nucleus_radius = 1.8e3
nucleus_geometric_albedo = 0.04
mach_number = 1
afp_0 = 78.9 # cm
albedo = 0.24
q = 0.988

n = rh.size
z_deg = solar_zenith_angle_draw(n)
cosz = np.cos(np.radians(z_deg))
cosz = np.clip(cosz, 1e-6, 1.0)

T_ice = np.empty(n)
for i in range(n):
    T_ice[i] = T_ice_bisection_method(A, cosz[i], rh[i], f_rh, M0)
T0 = T0_Rodionov2002(M0, T_ice)

a_star = critical_radius_Crifo1997(f_rh, rh, T0, Rn, cosz, A)
a_star0 = a_star / cosz
Q = Qm_Vaubaillon2005(T0, s, a_1, a_2, a_star0, Afp0, A_phi, q, rh)

plt.plot(jd, Q, lw=1.5)
plt.xlabel("JD", fontsize=18)
plt.ylabel(r"$Q_m$ (kg s$^{-1}$)", fontsize=18)
plt.title(r"$Q_m$ vs JD", fontsize=20)
plt.grid(alpha=0.5)
plt.show()


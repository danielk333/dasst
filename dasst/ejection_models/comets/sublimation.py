import numpy as np
import scipy.constants as const


def whipple_1951_dMdt(body_radius, helio_distance, solar_luminosity = 4e26, body_H_W = 1.88e6):
    return np.pi*body_radius**2*solar_luminosity/(4*np.pi*helio_distance**2)/body_H_W


def whipple_1951_vel(
                helio_distance, body_radius, bulk_density, mass, body_mass, dMdt,
                tau_Wip = 0.25,
                mu_Wip = 20*1.661e-24*1e-3, T_g0 = 300, K_drag = 26.0/9.0,
            ):

    v_g = np.sqrt(8*const.k*T_g0/(np.pi*mu_Wip))/(helio_distance/const.au)**tau_Wip
    v2 = dMdt*K_drag*v_g/(2*np.pi*body_radius)
    s = np.cbrt(mass*3/(4*np.pi*bulk_density))
    grav_effect = 2*const.G*(body_mass)/body_radius

    vel_mag = v2/(s*bulk_density)*(3.0/4.0) - grav_effect
    vel_mag = np.sqrt(vel_mag) 

    return vel_mag

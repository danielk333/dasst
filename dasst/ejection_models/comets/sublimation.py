import numpy as np
import scipy.constants as const


def whipple_1951_dMdt(
                helio_distance, 
                body_radius, 
                albedo = 0.2, 
                solar_luminosity = 4e26, 
                sublimation_heat = 1.88e6,
            ):
    S_flux = solar_luminosity/(4*np.pi*helio_distance**2)
    S_input = np.pi*body_radius**2*S_flux
    return S_input*(1 - albedo)/sublimation_heat


def whipple_1951_vel(
                helio_distance, 
                body_radius,
                body_mass,
                particle_bulk_density,
                particle_mass,
                dMdt,
                gas_molecule_mass = 20*1.661e-24*1e-3, 
                surface_temperature_coeff = 300, 
                K_drag = 26.0/9.0,
            ):
    r = helio_distance/const.au
    T = surface_temperature_coeff/np.sqrt(r)
    v_g = np.sqrt(8*const.k*T/(np.pi*gas_molecule_mass))

    particle_radius = np.cbrt(particle_mass*3/(4*np.pi*particle_bulk_density))
    A = np.pi*particle_radius**2
    A_to_m = A/particle_mass
    
    drag_v = (K_drag*0.5)*(dMdt*v_g/(np.pi*body_radius))*A_to_m
    grav_effect = 2*const.G*body_mass/body_radius

    vel_mag = drag_v - grav_effect
    vel_mag = np.sqrt(vel_mag) 

    return vel_mag

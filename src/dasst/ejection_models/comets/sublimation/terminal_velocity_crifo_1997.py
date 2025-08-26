"""Equations used in calculating dust particle terminal velocity as from [^1] and [^2]

[^1]: Crifo, J. F. & Rodionov, A. V. The Dependence of the Circumnuclear Coma Structure
    on the Properties of the Nucleus I. Comparison between a Homogeneous and an Inhomogeneous
    Spherical Nucleus, with Application to P/Wirtanen. Icarus 127, 319–353 (1997).

[^2]: Crifo, J. F. & Rodionov, A. V. The Dependence of the Circumnuclear Coma Structure
    on the Properties of the Nucleus II. First Investigation of the Coma Surrounding a
    Homogeneous, Aspherical Nucleus. Icarus 129, 72–93 (1997).

Originally authored by Francisca Emel Tuzcuoglu during IRF internship 2025
Maintained and modified by Daniel Kastinen thereafter

#todo: verify all the equations with a test cast and implement as tests
"""

import numpy as np
import scipy.constants as const

import dasst.constants


def maximum_particle_crifo_1997(
    fraction_active_surface,
    heliocentric_distance,
    gas_temperature,
    nuclues_radius,
    local_solar_zenith_cosine,
    albedo,
    vapor_specific_heats_ratio,
    gas_mean_molecular_mass,
    dust_mass_density,
    nucleus_mass,
    ice_latent_sublimation_heat=dasst.constants.L_S,
    ice_sublimation_coefficient=1.0,
    solar_flux=dasst.constants.C_SUN,
):
    """The critical radius of dust particles above which the momentum transfer from the gas drag is
    lower than the gravitational attraction causing particles to fall back down onto the nucleus
    (Appendix E eq 23 in Crifo 2002[^1]).

    [^1]: Crifo, J. F. & Rodionov, A. V. The Dependence of the Circumnuclear Coma Structure
        on the Properties of the Nucleus I. Comparison between a Homogeneous and an Inhomogeneous
        Spherical Nucleus, with Application to P/Wirtanen. Icarus 127, 319–353 (1997).

    """
    a_star = critical_radius_crifo_1997(
        fraction_active_surface,
        heliocentric_distance,
        gas_temperature,
        nuclues_radius,
        local_solar_zenith_cosine,
        albedo,
        vapor_specific_heats_ratio,
        gas_mean_molecular_mass,
        dust_mass_density,
        ice_latent_sublimation_heat=ice_latent_sublimation_heat,
        ice_sublimation_coefficient=ice_sublimation_coefficient,
        solar_flux=solar_flux,
    )
    return (
        a_star
        * np.sqrt(vapor_specific_heats_ratio / (2 * np.pi))
        * (const.k * gas_temperature * nuclues_radius)
        / (gas_mean_molecular_mass * const.G * nucleus_mass)
    )


def critical_radius_crifo_1997(
    fraction_active_surface,
    heliocentric_distance,
    gas_temperature,
    nuclues_radius,
    local_solar_zenith_cosine,
    albedo,
    vapor_specific_heats_ratio,
    gas_mean_molecular_mass,
    dust_mass_density,
    ice_latent_sublimation_heat=dasst.constants.L_S,
    ice_sublimation_coefficient=1.0,
    solar_flux=dasst.constants.C_SUN,
):
    """A "critical radius" for the dynamics of spherical dust grans as defined by the momentum
    budget equation (Appendix D eq 20 in Crifo 2002[^1]).

    [^1]: Crifo, J. F. & Rodionov, A. V. The Dependence of the Circumnuclear Coma Structure
        on the Properties of the Nucleus I. Comparison between a Homogeneous and an Inhomogeneous
        Spherical Nucleus, with Application to P/Wirtanen. Icarus 127, 319–353 (1997).

    """
    V_g0 = np.sqrt(vapor_specific_heats_ratio * const.k * gas_temperature / gas_mean_molecular_mass)
    factor1 = (
        (gas_mean_molecular_mass / const.m_u)
        * (1 - albedo)
        * solar_flux
        / (dust_mass_density * ice_sublimation_coefficient * ice_latent_sublimation_heat * V_g0)
    )
    factor2 = fraction_active_surface * local_solar_zenith_cosine / heliocentric_distance**2
    return factor1 * nuclues_radius * factor2


def terminal_velocity_crifo_1997(
    dust_radius,
    critical_radius,
    gas_temperature,
    vapor_specific_heats_ratio,
    gas_mean_molecular_mass,
):
    """The terminal velocity of a dust particle ejected by the drag force exerted on it during
    sublimation, neglecting gravitational effects (Appendix D eq 18-21 in Crifo 2002[^1]).

    [^1]: Crifo, J. F. & Rodionov, A. V. The Dependence of the Circumnuclear Coma Structure
        on the Properties of the Nucleus I. Comparison between a Homogeneous and an Inhomogeneous
        Spherical Nucleus, with Application to P/Wirtanen. Icarus 127, 319–353 (1997).

    """
    W = np.sqrt(
        (vapor_specific_heats_ratio + 1)
        / (vapor_specific_heats_ratio - 1)
        * vapor_specific_heats_ratio
        * const.k
        * gas_temperature
        / gas_mean_molecular_mass
    )
    Phi = 1.2 + 0.72 * np.sqrt(dust_radius / critical_radius)
    return W / Phi

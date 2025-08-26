"""
# Sublimation

todo: verify all the equations with a test cast and implement as tests
todo: go trough all albedos - is it geometric, effective, or bond alebdo??

Originally authored by Francisca Emel Tuzcuoglu during IRF internship 2025
Maintained and modified by Daniel Kastinen thereafter

## Vaubaillon model

The total mass production rate of grains with radii
in range [a_1, a_2] ejected by the active surface
by unit of time in all directions at distance rh in kg/s

todo

## Rodionov model

The model relates the gas parameters on the top of the Knudsen layer (gas_temperature; p0; mach_number) to the conditions
at the surface (T_I; T_d; f) of the comet.

A Knudsen layer is a thin layer of vapor near a liquid or solid that is evaporating, where the
interaction with the surface dominates and the gas is not in equilibrium.

## Whipple model

todo

## Crifo model

Equations used in calculating dust particle terminal velocity as from [^1] and [^2]

[^1]: Crifo, J. F. & Rodionov, A. V. The Dependence of the Circumnuclear Coma Structure
    on the Properties of the Nucleus I. Comparison between a Homogeneous and an Inhomogeneous
    Spherical Nucleus, with Application to P/Wirtanen. Icarus 127, 319–353 (1997).

[^2]: Crifo, J. F. & Rodionov, A. V. The Dependence of the Circumnuclear Coma Structure
    on the Properties of the Nucleus II. First Investigation of the Coma Surrounding a
    Homogeneous, Aspherical Nucleus. Icarus 129, 72–93 (1997).

"""

import numpy as np
import scipy.constants as const
import scipy.special
import scipy.optimize

import dasst.constants

_coefficient_I = 0.5 * scipy.special.beta(0.75, 0.5)
"""Special constant used in analytic solution of an integral, see
Gradshteyn & Ryzhik (1965) (Eq. (3.194-2)), used in Vaubaillon 2005
"""


def u_rodionov_2002(mach_number, vapor_specific_heats_ratio):
    """Dimensionless speed of the gas close to the surface of the comet
    (eq given after eq 96 in Rodionov 2002[^1]).

    [^1]: Rodionov, A. V., Crifo, J.-F., Szegő, K., Lagerros, J. & Fulle, M.
        An advanced physical model of cometary activity.
        Planetary and Space Science 50, 983–1024 (2002).

    """
    return mach_number * np.sqrt(vapor_specific_heats_ratio / 2)


def p_s_fanale_1984(ice_temperature):
    """Ice-vapor equilibrium interface pressure in Pascal close to the surface of the comet
    (eq 7 Fanale 1984[^1]).

    The constants $A=3.56e12 dynes/cm^2$ and $B=6141.664 K$ are derived by fitting data for water
    vapor over ice (and the form of the expression is informed from the Clapeyron-Clausius equation)

    [^1]: Fanale, F. P. & Salvail, J. R. An idealized short-period comet model:
        Surface insolation, H2O flux, dust flux, and mantle evolution.
        Icarus 60, 476–511 (1984).

    """
    return 3.56e12 * np.exp(-6141.667 / ice_temperature)  # Pa


def z_hk_rodionov_2002(ice_temperature, gas_mean_molecule_mass):
    """Hertz-Knudsen rate, or the gas production rate, close to the surface of the comet
    (eq given after eq 97 in Rodionov 2002[^1]). Combined with the backscattered
    condensing flux ($Z^-$) gives the total initial gas flux ($Z_0$).

    [^1]: Rodionov, A. V., Crifo, J.-F., Szegő, K., Lagerros, J. & Fulle, M.
        An advanced physical model of cometary activity.
        Planetary and Space Science 50, 983–1024 (2002).

    """
    return p_s_fanale_1984(ice_temperature) / np.sqrt(
        2 * np.pi * gas_mean_molecule_mass * const.k * ice_temperature
    )


def pressure_ratio_rodionov_2002(
    mach_number, ice_temperature, gas_temperature, vapor_specific_heats_ratio
):
    """Gas pressure ratio between the pressure at the top of the Knudsen layer and the ice-vapor
    equilibrium interface pressure (eq 96 in Rodionov 2002[^1]).

    [^1]: Rodionov, A. V., Crifo, J.-F., Szegő, K., Lagerros, J. & Fulle, M.
        An advanced physical model of cometary activity.
        Planetary and Space Science 50, 983–1024 (2002).

    """
    u = u_rodionov_2002(mach_number, vapor_specific_heats_ratio)
    return (
        0.5
        - u * np.sqrt(gas_temperature / np.pi / ice_temperature)
        + ((u**2 + 0.5) * np.sqrt(gas_temperature / ice_temperature) - (u * np.sqrt(np.pi) / 2))
        * scipy.special.erfc(u)
        * np.exp(u**2)
    )


def z_minus_rodionov_2002(
    mach_number,
    ice_temperature,
    gas_temperature,
    vapor_specific_heats_ratio,
    gas_mean_molecule_mass,
):
    """Gas pressure ratio between the pressure at the top of the Knudsen layer and the ice-vapor
    equilibrium interface pressure (eq 98 in Rodionov 2002[^1]).

    [^1]: Rodionov, A. V., Crifo, J.-F., Szegő, K., Lagerros, J. & Fulle, M.
        An advanced physical model of cometary activity.
        Planetary and Space Science 50, 983–1024 (2002).

    """
    pressure_ratio = pressure_ratio_rodionov_2002(
        mach_number, ice_temperature, gas_temperature, vapor_specific_heats_ratio
    )
    gas_backscatter_fraction = 1 - 2 * u_rodionov_2002(
        mach_number, vapor_specific_heats_ratio
    ) * np.sqrt(np.pi) * pressure_ratio * np.sqrt(ice_temperature / gas_temperature)
    return gas_backscatter_fraction * z_hk_rodionov_2002(ice_temperature, gas_mean_molecule_mass)


def z_0_rodionov_2002(
    mach_number,
    ice_temperature,
    gas_temperature,
    vapor_specific_heats_ratio,
    gas_mean_molecule_mass,
):
    """Initial gas flux (molecules/m/s), or the ice _net_ sublimation flux,
    (probably?) at the top of the Knudsen layer (eq 97 in Rodionov 2002[^1]).

    [^1]: Rodionov, A. V., Crifo, J.-F., Szegő, K., Lagerros, J. & Fulle, M.
        An advanced physical model of cometary activity.
        Planetary and Space Science 50, 983–1024 (2002).

    """
    return z_hk_rodionov_2002(ice_temperature, gas_mean_molecule_mass) - z_minus_rodionov_2002(
        mach_number,
        ice_temperature,
        gas_temperature,
        vapor_specific_heats_ratio,
        gas_mean_molecule_mass,
    )


def gas_temperature_rodionov_2002(mach_number, ice_temperature, vapor_specific_heats_ratio):
    """Gas temperature at the top of the Knudsen layer
    (eq 95 in Rodionov 2002[^1], based on Cercignani 1981[^2]).

    [^1]: Rodionov, A. V., Crifo, J.-F., Szegő, K., Lagerros, J. & Fulle, M.
        An advanced physical model of cometary activity.
        Planetary and Space Science 50, 983–1024 (2002).

    [^2]: Cercignani, C. Strong evaporation of a polyatomic gas.
        Progress in Astronautics and Aeronautics 74, 305–320 (1981).

    """
    u = u_rodionov_2002(mach_number, vapor_specific_heats_ratio)
    prefactor = np.sqrt(
        1
        + (
            u
            * np.sqrt(np.pi)
            / 2
            * (vapor_specific_heats_ratio - 1)
            / (vapor_specific_heats_ratio + 1)
        )
        ** 2
    ) - (
        u * np.sqrt(np.pi) / 2 * (vapor_specific_heats_ratio - 1) / (vapor_specific_heats_ratio + 1)
    )
    return prefactor**2 * ice_temperature


def absorbed_solar_energy_rodionov_2002(
    nucleus_effective_albedo,
    local_solar_zenith_cosine,
    heliocentric_distance,
    solar_flux=dasst.constants.C_SUN,
):
    """Radiation energy absorbed into the cometary nucleus
    (eq 6 in Rodionov 2002[^1]).

    [^1]: Rodionov, A. V., Crifo, J.-F., Szegő, K., Lagerros, J. & Fulle, M.
        An advanced physical model of cometary activity.
        Planetary and Space Science 50, 983–1024 (2002).

    """
    return (
        (1 - nucleus_effective_albedo)
        * solar_flux
        * np.max(local_solar_zenith_cosine, 0)
        / (heliocentric_distance**2)
    )


def ice_temperature_energy_budget_rodionov_2002(
    ice_temperature,
    icy_area_fraction,
    ice_latent_sublimation_heat,
    ice_sublimation_coefficient,
    mach_number,
    emissivity,
    heat_conduction_flux,
    vapor_specific_heats_ratio,
    gas_mean_molecule_mass,
):
    """LHS of local isothermal (ice temperature = dust temperature) energy budget, i.e. energy
    'usage' in terms of gas sublimation, thermal radiation, and heat conduction as a result
    of an input energy (LHS of eq 7 in Rodionov 2002[^1]).

    [^1]: Rodionov, A. V., Crifo, J.-F., Szegő, K., Lagerros, J. & Fulle, M.
        An advanced physical model of cometary activity.
        Planetary and Space Science 50, 983–1024 (2002).

    """
    gas_temperature = gas_temperature_rodionov_2002(
        mach_number, ice_temperature, vapor_specific_heats_ratio
    )
    z_0 = z_0_rodionov_2002(
        mach_number,
        ice_temperature,
        gas_temperature,
        vapor_specific_heats_ratio,
        gas_mean_molecule_mass,
    )
    return (
        emissivity * const.sigma * ice_temperature**4
        + icy_area_fraction
        * ice_sublimation_coefficient
        * (ice_latent_sublimation_heat * gas_mean_molecule_mass)
        * z_0
        + heat_conduction_flux
    )


def _ice_temperature_energy_budget_equation(
    ice_temperature,
    nucleus_effective_albedo,
    local_solar_zenith_cosine,
    heliocentric_distance,
    icy_area_fraction,
    mach_number,
    ice_latent_sublimation_heat,
    emissivity,
    ice_sublimation_coefficient,
    heat_conduction_flux,
    vapor_specific_heats_ratio,
    gas_mean_molecule_mass,
):
    E_in = absorbed_solar_energy_rodionov_2002(
        nucleus_effective_albedo, local_solar_zenith_cosine, heliocentric_distance
    )
    E_out = ice_temperature_energy_budget_rodionov_2002(
        ice_temperature,
        icy_area_fraction,
        ice_latent_sublimation_heat,
        ice_sublimation_coefficient,
        mach_number,
        emissivity,
        heat_conduction_flux,
        vapor_specific_heats_ratio,
        gas_mean_molecule_mass,
    )
    return E_in - E_out


def solve_ice_temperature_rodionov_2002(
    nucleus_effective_albedo,
    local_solar_zenith_cosine,
    heliocentric_distance,
    icy_area_fraction,
    mach_number,
    vapor_specific_heats_ratio,
    gas_mean_molecule_mass,
    ice_latent_sublimation_heat=dasst.constants.L_S,
    emissivity=0.9,
    ice_sublimation_coefficient=1.0,
    heat_conduction_flux=0,
    absolute_tolerance=1e-3,
    lower_bound=1,
    upper_bound=600,
    maxiter=None,
):
    """The temperature of the ice of the comet during sublimation

    #todo docstring with reference and description
    """
    kw = {}
    if maxiter is not None:
        kw["maxiter"] = maxiter

    try:
        root = scipy.optimize.brentq(
            _ice_temperature_energy_budget_equation,
            lower_bound,
            upper_bound,
            args=(
                nucleus_effective_albedo,
                local_solar_zenith_cosine,
                heliocentric_distance,
                icy_area_fraction,
                mach_number,
                ice_latent_sublimation_heat,
                emissivity,
                ice_sublimation_coefficient,
                heat_conduction_flux,
                vapor_specific_heats_ratio,
                gas_mean_molecule_mass,
            ),
            xtol=absolute_tolerance,
            **kw,
        )
    except ValueError:
        root = np.nan

    return root


def maximum_particle_crifo_1997(
    fraction_active_surface,
    heliocentric_distance,
    gas_temperature,
    nucleus_radius,
    local_solar_zenith_cosine,
    nucleus_effective_albedo,
    vapor_specific_heats_ratio,
    gas_mean_molecule_mass,
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
        nucleus_radius,
        local_solar_zenith_cosine,
        nucleus_effective_albedo,
        vapor_specific_heats_ratio,
        gas_mean_molecule_mass,
        dust_mass_density,
        ice_latent_sublimation_heat=ice_latent_sublimation_heat,
        ice_sublimation_coefficient=ice_sublimation_coefficient,
        solar_flux=solar_flux,
    )
    return (
        a_star
        * np.sqrt(vapor_specific_heats_ratio / (2 * np.pi))
        * (const.k * gas_temperature * nucleus_radius)
        / (gas_mean_molecule_mass * const.G * nucleus_mass)
    )


def critical_radius_crifo_1997(
    fraction_active_surface,
    heliocentric_distance,
    gas_temperature,
    nucleus_radius,
    local_solar_zenith_cosine,
    nucleus_effective_albedo,
    vapor_specific_heats_ratio,
    gas_mean_molecule_mass,
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
    V_g0 = np.sqrt(vapor_specific_heats_ratio * const.k * gas_temperature / gas_mean_molecule_mass)
    factor1 = (
        (gas_mean_molecule_mass / const.m_u)
        * (1 - nucleus_effective_albedo)
        * solar_flux
        / (dust_mass_density * ice_sublimation_coefficient * ice_latent_sublimation_heat * V_g0)
    )
    factor2 = fraction_active_surface * local_solar_zenith_cosine / heliocentric_distance**2
    return factor1 * nucleus_radius * factor2


def terminal_velocity_crifo_1997(
    dust_radius,
    critical_radius,
    gas_temperature,
    vapor_specific_heats_ratio,
    gas_mean_molecule_mass,
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
        / gas_mean_molecule_mass
    )
    Phi = 1.2 + 0.72 * np.sqrt(dust_radius / critical_radius)
    return W / Phi


def w_crifo_1997(gas_temperature, vapor_specific_heats_ratio, gas_mean_molecule_mass):
    """W parameter of the terminal velocity presented in Crifo 1997
    (originating in Probstein 1968).
    """
    return np.sqrt(
        (vapor_specific_heats_ratio + 1)
        / (vapor_specific_heats_ratio - 1)
        * vapor_specific_heats_ratio
        * const.k
        * gas_temperature
        / gas_mean_molecule_mass
    )


def a_x_vaubaillon_2005(
    dust_radius, dust_size_distribution_index, lower_size_limit, upper_size_limit
):
    """Integrated function used in dust production equations, $A_x(a1; a2)$,
    from equation A.9 in Appendix A of Vaubaillon 2005.
    """
    if dust_radius != dust_size_distribution_index:
        a_x = (
            upper_size_limit ** (dust_radius - dust_size_distribution_index)
            - lower_size_limit ** (dust_radius - dust_size_distribution_index)
        ) / (dust_radius - dust_size_distribution_index)
    else:
        a_x = np.log(upper_size_limit / lower_size_limit)
    return a_x


def j_vaubaillon_2005(
    gas_temperature,
    dust_size_distribution_index,
    lower_size_limit,
    upper_size_limit,
    critical_radius,
    alpha_coef,
    vapor_specific_heats_ratio,
    gas_mean_molecule_mass,
):
    """J parameter of the dust production rate as defined in equation B.1 of Appendix B in
    Vaubaillon 2005[^1].

    [^1]: Vaubaillon, J., Colas, F. & Jorda, L. A new method to predict meteor showers:
        I. Description of the model. A&A 439, 751–760 (2005).

    """
    w = w_crifo_1997(gas_temperature, vapor_specific_heats_ratio, gas_mean_molecule_mass)
    beta_coef = 0.72 / np.sqrt(critical_radius)  # eq 11
    a_3 = a_x_vaubaillon_2005(3, dust_size_distribution_index, lower_size_limit, upper_size_limit)
    a_35 = a_x_vaubaillon_2005(
        3.5, dust_size_distribution_index, lower_size_limit, upper_size_limit
    )
    return w / (alpha_coef * a_3 + beta_coef * _coefficient_I * a_35)


def total_mass_production_vaubaillon_2005(
    gas_temperature,
    dust_size_distribution_index,
    dust_mass_density,
    lower_size_limit,
    upper_size_limit,
    critical_radius,
    alpha_coef,
    vapor_specific_heats_ratio,
    gas_mean_molecule_mass,
    afp_0,
    observed_albedo,
    perihelion_distance,
    heliocentric_distance,
    index_of_variation,
):
    """Total mass production from equation B.8 in Appendix B in Vaubaillon 2005.
    """
    j_func = j_vaubaillon_2005(
        gas_temperature,
        dust_size_distribution_index,
        lower_size_limit,
        upper_size_limit,
        critical_radius,
        alpha_coef,
        vapor_specific_heats_ratio,
        gas_mean_molecule_mass,
    )
    a_4 = a_x_vaubaillon_2005(4, dust_size_distribution_index, lower_size_limit, upper_size_limit)
    factor = 4 / 3 * np.pi * dust_mass_density * j_func * afp_0 / observed_albedo * a_4
    return factor * (perihelion_distance / heliocentric_distance) ** index_of_variation


def heliocentric_distance_factor_vaubaillon_2005(
    perihelion_distance, max_activity_distance, index_of_variation
):
    if index_of_variation != 1:
        factor_rh = (
            perihelion_distance**index_of_variation
            / (1 - index_of_variation)
            * (
                max_activity_distance ** (1 - index_of_variation)
                - perihelion_distance ** (1 - index_of_variation)
            )
        )
    else:
        factor_rh = perihelion_distance**index_of_variation * np.log(
            max_activity_distance / perihelion_distance
        )
    return factor_rh


def total_mass_loss_vaubaillon_2005(
    outgassing_duration,
    gas_temperature,
    dust_size_distribution_index,
    dust_mass_density,
    lower_size_limit,
    upper_size_limit,
    critical_radius,
    alpha_coef,
    vapor_specific_heats_ratio,
    gas_mean_molecule_mass,
    afp_0,
    observed_albedo,
    perihelion_distance,
    index_of_variation,
    max_activity_distance,
):
    """Total mass loss during a perihelion passage from equation B.9 in Appendix B in Vaubaillon
    2005, using B.5 and B.6 for definitions of the factors.
    """
    factor_rh = heliocentric_distance_factor_vaubaillon_2005(
        perihelion_distance,
        max_activity_distance,
        index_of_variation,
    )
    q_m = total_mass_production_vaubaillon_2005(
        gas_temperature,
        dust_size_distribution_index,
        dust_mass_density,
        lower_size_limit,
        upper_size_limit,
        critical_radius,
        alpha_coef,
        vapor_specific_heats_ratio,
        gas_mean_molecule_mass,
        afp_0,
        observed_albedo,
        perihelion_distance,
        perihelion_distance,
        index_of_variation,
    )
    return outgassing_duration * factor_rh * q_m


def mass_loss_whipple_1951(
    helio_distance,
    body_radius,
    nucleus_effective_albedo,
    ice_latent_sublimation_heat,
    solar_luminosity=dasst.constants.L_SUN,
):
    """todo docstring"""
    S_flux = solar_luminosity / (4 * np.pi * helio_distance**2)
    S_input = np.pi * body_radius**2 * S_flux
    return S_input * (1 - nucleus_effective_albedo) / ice_latent_sublimation_heat


def terminal_velocity_whipple_1951(
    heliocentric_distance,
    body_radius,
    body_mass,
    particle_bulk_density,
    particle_mass,
    mass_loss,
    gas_mean_molecule_mass=20 * 1.661e-24 * 1e-3,
    surface_temperature_coeff=300,
    K_drag=26.0 / 9.0,
):
    """todo docstring"""
    r = heliocentric_distance / const.au
    T = surface_temperature_coeff / np.sqrt(r)
    v_g = np.sqrt(8 * const.k * T / (np.pi * gas_mean_molecule_mass))

    particle_radius = np.cbrt(particle_mass * 3 / (4 * np.pi * particle_bulk_density))
    A = np.pi * particle_radius**2
    A_to_m = A / particle_mass

    drag_v = (K_drag * 0.5) * (mass_loss * v_g / (np.pi * body_radius)) * A_to_m
    grav_effect = 2 * const.G * body_mass / body_radius

    vel_mag = drag_v - grav_effect
    vel_mag = np.sqrt(vel_mag)

    return vel_mag

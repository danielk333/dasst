"""Originally authored by Francisca Emel Tuzcuoglu during IRF internship 2025
Maintained and modified by Daniel Kastinen thereafter

The model relates the gas parameters on the top of the Knudsen layer (gas_temperature; p0; mach_number) to the conditions
at the surface (T_I; T_d; f) of the comet.

A Knudsen layer is a thin layer of vapor near a liquid or solid that is evaporating, where the
interaction with the surface dominates and the gas is not in equilibrium.
"""

import numpy as np
import scipy.constants as const
import scipy.special
import scipy.optimize

import dasst.constants


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


def z_hk_rodionov_2002(ice_temperature, gas_mean_molecular_mass):
    """Hertz-Knudsen rate, or the gas production rate, close to the surface of the comet
    (eq given after eq 97 in Rodionov 2002[^1]). Combined with the backscattered
    condensing flux ($Z^-$) gives the total initial gas flux ($Z_0$).

    [^1]: Rodionov, A. V., Crifo, J.-F., Szegő, K., Lagerros, J. & Fulle, M.
        An advanced physical model of cometary activity.
        Planetary and Space Science 50, 983–1024 (2002).

    """
    return p_s_fanale_1984(ice_temperature) / np.sqrt(
        2 * np.pi * gas_mean_molecular_mass * const.k * ice_temperature
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
    gas_mean_molecular_mass,
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
    return gas_backscatter_fraction * z_hk_rodionov_2002(ice_temperature, gas_mean_molecular_mass)


def z_0_rodionov_2002(
    mach_number,
    ice_temperature,
    gas_temperature,
    vapor_specific_heats_ratio,
    gas_mean_molecular_mass,
):
    """Initial gas flux (molecules/m/s), or the ice _net_ sublimation flux,
    (probably?) at the top of the Knudsen layer (eq 97 in Rodionov 2002[^1]).

    [^1]: Rodionov, A. V., Crifo, J.-F., Szegő, K., Lagerros, J. & Fulle, M.
        An advanced physical model of cometary activity.
        Planetary and Space Science 50, 983–1024 (2002).

    """
    return z_hk_rodionov_2002(ice_temperature, gas_mean_molecular_mass) - z_minus_rodionov_2002(
        mach_number,
        ice_temperature,
        gas_temperature,
        vapor_specific_heats_ratio,
        gas_mean_molecular_mass,
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


def input_radiation_flux_rodionov_2002(
    effective_albedo,
    local_solar_zenith_cosine,
    heliocentric_distance,
    solar_flux=dasst.constants.C_SUN,
):
    """Radiation influx into the active part of the cometary nuclues
    (probably? #todo double check) (eq 6 in Rodionov 2002[^1]).

    [^1]: Rodionov, A. V., Crifo, J.-F., Szegő, K., Lagerros, J. & Fulle, M.
        An advanced physical model of cometary activity.
        Planetary and Space Science 50, 983–1024 (2002).

    """
    return (
        (1 - effective_albedo)
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
    gas_mean_molecular_mass,
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
        gas_mean_molecular_mass,
    )
    return (
        emissivity * const.sigma * ice_temperature**4
        + icy_area_fraction
        * ice_sublimation_coefficient
        * (ice_latent_sublimation_heat * gas_mean_molecular_mass)
        * z_0
        + heat_conduction_flux
    )


def _ice_temperature_energy_budget_equation(
    ice_temperature,
    effective_albedo,
    local_solar_zenith_cosine,
    heliocentric_distance,
    icy_area_fraction,
    mach_number,
    ice_latent_sublimation_heat,
    emissivity,
    ice_sublimation_coefficient,
    heat_conduction_flux,
    vapor_specific_heats_ratio,
    gas_mean_molecular_mass,
):
    E_in = input_radiation_flux_rodionov_2002(
        effective_albedo, local_solar_zenith_cosine, heliocentric_distance
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
        gas_mean_molecular_mass,
    )
    return E_in - E_out


def solve_ice_temperature_rodionov_2002(
    effective_albedo,
    local_solar_zenith_cosine,
    heliocentric_distance,
    icy_area_fraction,
    mach_number,
    vapor_specific_heats_ratio,
    gas_mean_molecular_mass,
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
                effective_albedo,
                local_solar_zenith_cosine,
                heliocentric_distance,
                icy_area_fraction,
                mach_number,
                ice_latent_sublimation_heat,
                emissivity,
                ice_sublimation_coefficient,
                heat_conduction_flux,
                vapor_specific_heats_ratio,
                gas_mean_molecular_mass,
            ),
            xtol=absolute_tolerance,
            **kw,
        )
    except ValueError:
        root = np.nan

    return root

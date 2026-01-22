from pyorb import M_sol

M_sun = M_sol


C_SUN = 1353  # W/m^2
"""Solar flux at 1 AU in W/m^2

#todo citation?
"""

L_SUN = 4e26
"""Solar luminosity in J/s

#todo citation
"""

L_S = 2.833e6  # J/kg
"""Ice latent heat of sublimation J/kg

#todo citation?
"""

AU: float = 1.495978707e11 # astronomical unit [m]

# Time
DAY: float = 86400.0 # seconds in a day
YEAR: float = 365.25 * DAY # Julian year [s]

# Gravitational parameters
MU_SUN: float = 1.32712440018e20 # GM_sun [m^3/s^2]
MU_EARTH: float = 3.986004418e14 # GM_earth [m^3/s^2]

# Radii
R_SUN: float = 6.957e8 # [m]
R_EARTH: float = 6.371e6 # [m]

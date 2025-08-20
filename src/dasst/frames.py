#!/usr/bin/env python

"""Coordinate frame transformations and related functions.
Main usage is the :code:`convert` function that wraps Astropy frame transformations.

"""

# Python standard import
from collections import OrderedDict

# Third party import
import numpy as np
import astropy.coordinates as coord
import astropy.units as units
from astropy.coordinates import EarthLocation

try:
    from jplephem.spk import SPK
except ImportError:
    SPK = None

CLOSE_TO_POLE_LIMIT = 1e-9**2
CLOSE_TO_POLE_LIMIT_rad = np.arctan(1 / np.sqrt(CLOSE_TO_POLE_LIMIT))

"""List of astropy frames
"""
ASTROPY_FRAMES = {
    "TEME": "TEME",
    "ITRS": "ITRS",
    "ITRF": "ITRS",
    "ICRS": "ICRS",
    "ICRF": "ICRS",
    "GCRS": "GCRS",
    "GCRF": "GCRS",
    "HCRS": "HCRS",
    "HCRF": "HCRS",
    "HeliocentricMeanEcliptic".upper(): "HeliocentricMeanEcliptic",
    "GeocentricMeanEcliptic".upper(): "GeocentricMeanEcliptic",
    "HeliocentricTrueEcliptic".upper(): "HeliocentricTrueEcliptic",
    "GeocentricTrueEcliptic".upper(): "GeocentricTrueEcliptic",
    "BarycentricMeanEcliptic".upper(): "BarycentricMeanEcliptic",
    "BarycentricTrueEcliptic".upper(): "BarycentricTrueEcliptic",
    "SPICEJ2000": "ICRS",
}

ASTROPY_NOT_OBSTIME = [
    "ICRS",
    "BarycentricMeanEcliptic",
    "BarycentricTrueEcliptic",
]

"""Mapping from body name to integer id's used by the kernels.

Taken from `astropy.coordinates.solar_system`
"""
BODY_NAME_TO_KERNEL_SPEC = OrderedDict(
    [
        ("sun", [(0, 10)]),
        ("mercury", [(0, 1), (1, 199)]),
        ("venus", [(0, 2), (2, 299)]),
        ("earth-moon-barycenter", [(0, 3)]),
        ("earth", [(0, 3), (3, 399)]),
        ("moon", [(0, 3), (3, 301)]),
        ("mars", [(0, 4)]),
        ("jupiter", [(0, 5)]),
        ("saturn", [(0, 6)]),
        ("uranus", [(0, 7)]),
        ("neptune", [(0, 8)]),
        ("pluto", [(0, 9)]),
    ]
)


def not_geocentric(frame):
    """Check if the given frame name is one of the non-geocentric frames."""
    frame = frame.upper()
    return frame in ["ICRS", "ICRF", "HCRS", "HCRF"] or frame.startswith(
        "Heliocentric".upper()
    )


def is_geocentric(frame):
    """Check if the frame name is a supported geocentric frame"""
    return not not_geocentric(frame)


def arctime_to_degrees(minutes, seconds):
    return (minutes + seconds / 60.0) / 60.0


def get_solarsystem_body_states(bodies, epoch, kernel, units=None):
    """Open a kernel file and get the statates of the given bodies at epoch in ICRS.

    Note: All outputs from kernel computations are in the Barycentric (ICRS) "eternal" frame.
    """
    assert SPK is not None, "jplephem package needed to directly interact with kernels"
    states = {}

    kernel = SPK.open(kernel)

    epoch_ = epoch.tdb  # jplephem uses Barycentric Dynamical Time (TDB)
    jd1, jd2 = epoch_.jd1, epoch_.jd2

    for body in bodies:
        body_ = body.lower().strip()

        if body_ not in BODY_NAME_TO_KERNEL_SPEC:
            raise ValueError(f'Body name "{body}" not recognized')

        states[body] = np.zeros((6,), dtype=np.float64)

        # if there are multiple steps to go from states to
        # ICRS barycentric, iterate trough and combine
        for pair in BODY_NAME_TO_KERNEL_SPEC[body_]:
            spk = kernel[pair]
            if spk.data_type == 3:
                # Type 3 kernels contain both position and velocity.
                posvel = spk.compute(jd1, jd2).flatten()
            else:
                pos_, vel_ = spk.compute_and_differentiate(jd1, jd2)
                posvel = np.zeros((6,), dtype=np.float64)
                posvel[:3] = pos_
                posvel[3:] = vel_

            states[body] += posvel

        # units from kernels are usually in km and km/day
        if units is None:
            states[body] *= 1e3
            states[body][3:] /= 86400.0
        else:
            states[body] *= units[0]
            states[body][3:] /= units[1]

    return states


def convert(t, states, in_frame, out_frame, **kwargs):
    """Perform predefined coordinate transformations using Astropy.
    Always returns a copy of the array.

    :param numpy.ndarray/float t: Absolute time corresponding to the input states.
    :param numpy.ndarray states: Size `(6,n)` matrix of states in SI units where
        rows 1-3 are position and 4-6 are velocity.
    :param str in_frame: Name of the frame the input states are currently in.
    :param str out_frame: Name of the state to transform to.
    :param Profiler profiler: Profiler instance for checking function performance.
    :param logging.Logger logger: Logger instance for logging the execution of
        the function.
    :rtype: numpy.ndarray
    :return: Size `(6,n)` matrix of states in SI units where rows
        1-3 are position and 4-6 are velocity.

    """

    in_frame = in_frame.upper()
    out_frame = out_frame.upper()

    if in_frame == out_frame:
        return states.copy()

    if in_frame in ASTROPY_FRAMES:
        in_frame_ = ASTROPY_FRAMES[in_frame]
        in_frame_cls = getattr(coord, in_frame_)
    else:
        err_str = (
            f"In frame '{in_frame}' not recognized, "
            "please check spelling or perform manual transformation"
        )
        raise ValueError(err_str)

    kw = {}
    kw.update(kwargs)
    if in_frame_ not in ASTROPY_NOT_OBSTIME:
        kw["obstime"] = t

    astropy_states = _convert_to_astropy(states, in_frame_cls, **kw)

    if out_frame in ASTROPY_FRAMES:
        out_frame_ = ASTROPY_FRAMES[out_frame]
        out_frame_cls = getattr(coord, out_frame_)
    else:
        err_str = (
            f"Out frame '{out_frame}' not recognized, "
            "please check spelling or perform manual transformation"
        )
        raise ValueError(err_str)

    kw = {}
    kw.update(kwargs)
    if out_frame_ not in ASTROPY_NOT_OBSTIME:
        kw["obstime"] = t

    out_states = astropy_states.transform_to(out_frame_cls(**kw))

    rets = states.copy()
    rets[:3, ...] = out_states.cartesian.xyz.to(units.m).value
    rets[3:, ...] = out_states.velocity.d_xyz.to(units.m / units.s).value

    return rets


def _convert_to_astropy(states, frame, **kw):
    state_p = coord.CartesianRepresentation(states[:3, ...] * units.m)
    state_v = coord.CartesianDifferential(states[3:, ...] * units.m / units.s)
    astropy_states = frame(state_p.with_differentials(state_v), **kw)
    return astropy_states


def ecef_to_enu(lat, lon, degrees=True):
    """ECEF coordinate system to local ENU (east,north,up), not including translation.

    :param float lat: Latitude on the ellipsoid
    :param float lon: Longitude on the ellipsoid
    :param numpy.ndarray ecef: (3,n) array x,y and z coordinates in ECEF.
    :param bool radians: If :code:`True` then all values are given in radians instead of degrees.
    :rtype: numpy.ndarray
    :return: (3,3) rotation matrix.
    """
    mx = enu_to_ecef(lat, lon, degrees=degrees)
    return np.linalg.inv(mx)


def enu_to_ecef(lat, lon, degrees=True):
    """ENU (east/north/up) to ECEF coordinate system conversion, not including translation.

    :param float lat: Latitude on the ellipsoid
    :param float lon: Longitude on the ellipsoid
    :param bool radians: If :code:`True` then all values are given in radians instead of degrees.
    :rtype: numpy.ndarray
    :return: (3,3) rotation matrix.
    """
    if degrees:
        lat, lon = np.radians(lat), np.radians(lon)

    mx = np.array(
        [
            [-np.sin(lon), -np.sin(lat) * np.cos(lon), np.cos(lat) * np.cos(lon)],
            [np.cos(lon), -np.sin(lat) * np.sin(lon), np.cos(lat) * np.sin(lon)],
            [0, np.cos(lat), np.sin(lat)],
        ]
    )
    return mx


def geodetic_to_ITRS(lat, lon, alt, degrees=True, ellipsoid=None):
    """Use `astropy.coordinates.EarthLocation` to transform from geodetic to ITRS."""

    if degrees:
        lat, lon = np.radians(lat), np.radians(lon)

    cord = EarthLocation.from_geodetic(
        lon=lon * units.rad,
        lat=lat * units.rad,
        height=alt * units.m,
        ellipsoid=ellipsoid,
    )
    x, y, z = cord.to_geocentric()

    pos = np.empty((3,), dtype=np.float64)

    pos[0] = x.to(units.m).value
    pos[1] = y.to(units.m).value
    pos[2] = z.to(units.m).value

    return pos


def ITRS_to_geodetic(x, y, z, degrees=True, ellipsoid=None):
    """Use `astropy.coordinates.EarthLocation` to transform from geodetic to ITRS.

    :param float x: X-coordinate in ITRS
    :param float y: Y-coordinate in ITRS
    :param float z: Z-coordinate in ITRS
    :param bool radians: If :code:`True` then all values are given in radians instead of degrees.
    :param str/None ellipsoid: Name of the ellipsoid model used for geodetic
    coordinates, for default value see Astropy `EarthLocation`.
    :rtype: numpy.ndarray
    :return: (3,) array of longitude, latitude and height above ellipsoid
    """

    cord = EarthLocation.from_geocentric(
        x=x * units.m,
        y=y * units.m,
        z=z * units.m,
    )
    lon, lat, height = cord.to_geodetic(ellipsoid=ellipsoid)

    llh = np.empty((3,), dtype=np.float64)

    if degrees:
        u_ = units.deg
    else:
        u_ = units.rad
    llh[0] = lat.to(u_).value
    llh[1] = lon.to(u_).value
    llh[2] = height.to(units.m).value

    return llh


def cart_to_sph(
    vec,
    degrees=False,
):
    """Convert from Cartesian coordinates (east, north, up) to Spherical
    coordinates (azimuth, elevation, range) in a angle east of north and
    elevation fashion. Returns azimuth between [-pi, pi] and elevation between
    [-pi/2, pi/2].

    Parameters
    ----------
    vec : numpy.ndarray
        (3, N) or (3,) vector of Cartesian coordinates (east, north, up).
        This argument is vectorized in the second array dimension.
    degrees : bool
        If :code:`True`, use degrees. Else all angles are given in radians.

    Returns
    -------
    numpy.ndarray
        (3, N) or (3, ) vector of Spherical coordinates
        (azimuth, elevation, range).

    Notes
    -----
    Azimuth close to pole convention
        Uses a :code:`CLOSE_TO_POLE_LIMIT` constant when transforming determine
        if the point is close to the pole and sets the azimuth by definition
        to 0 "at" the poles for consistency.

    """

    r2_ = vec[0, ...] ** 2 + vec[1, ...] ** 2

    sph = np.empty(vec.shape, dtype=vec.dtype)

    if len(vec.shape) == 1:
        if r2_ < CLOSE_TO_POLE_LIMIT:
            sph[0] = 0.0
            sph[1] = np.sign(vec[2]) * np.pi * 0.5
        else:
            sph[0] = np.arctan2(vec[0], vec[1])
            sph[1] = np.arctan(vec[2] / np.sqrt(r2_))
    else:
        inds_ = r2_ < CLOSE_TO_POLE_LIMIT
        not_inds_ = np.logical_not(inds_)

        sph[0, inds_] = 0.0
        sph[1, inds_] = np.sign(vec[2, inds_]) * np.pi * 0.5
        sph[0, not_inds_] = np.arctan2(vec[0, not_inds_], vec[1, not_inds_])
        sph[1, not_inds_] = np.arctan(vec[2, not_inds_] / np.sqrt(r2_[not_inds_]))

    sph[2, ...] = np.sqrt(r2_ + vec[2, ...] ** 2)
    if degrees:
        sph[:2, ...] = np.degrees(sph[:2, ...])

    return sph


def sph_to_cart(vec, degrees=False):
    """Convert from spherical coordinates (azimuth, elevation, range) to
    Cartesian (east, north, up) in a angle east of north and elevation fashion.


    Parameters
    ----------
    vec : numpy.ndarray
        (3, N) or (3,) vector of Cartesian Spherical
        (azimuth, elevation, range).
        This argument is vectorized in the second array dimension.
    degrees : bool
        If :code:`True`, use degrees. Else all angles are given in radians.

    Returns
    -------
    numpy.ndarray
        (3, N) or (3, ) vector of Cartesian coordinates (east, north, up).

    """

    _az = vec[0, ...]
    _el = vec[1, ...]
    if degrees:
        _az, _el = np.radians(_az), np.radians(_el)
    cart = np.empty(vec.shape, dtype=vec.dtype)

    cart[0, ...] = vec[2, ...] * np.sin(_az) * np.cos(_el)
    cart[1, ...] = vec[2, ...] * np.cos(_az) * np.cos(_el)
    cart[2, ...] = vec[2, ...] * np.sin(_el)

    return cart


def vector_angle(a, b, degrees=False):
    """Angle between two vectors.

    Parameters
    ----------
    a : numpy.ndarray
        (3, N) or (3,) vector of Cartesian coordinates.
        This argument is vectorized in the second array dimension.
    b : numpy.ndarray
        (3, N) or (3,) vector of Cartesian coordinates.
        This argument is vectorized in the second array dimension.
    degrees : bool
        If :code:`True`, use degrees. Else all angles are given in radians.

    Returns
    -------
    numpy.ndarray or float
        (N, ) or float vector of angles between input vectors.

    Notes
    -----
    Definition
        :math:`\\theta = \\cos^{-1}\\frac{
            \\langle\\mathbf{a},\\mathbf{b}\\rangle
        }{
            |\\mathbf{a}||\\mathbf{b}|
        }`
        where :math:`\\langle\\mathbf{a},\\mathbf{b}\\rangle` is the dot
        product and :math:`|\\mathbf{a}|` denotes the norm.

    """
    a_norm = np.linalg.norm(a, axis=0)
    b_norm = np.linalg.norm(b, axis=0)

    if len(a.shape) == 1:
        proj = np.dot(a, b) / (a_norm * b_norm)
    elif len(b.shape) == 1:
        proj = np.dot(b, a) / (a_norm * b_norm)
    else:
        assert a.shape == b.shape, "Input shapes do not match"
        proj = np.sum(a * b, axis=0) / (a_norm * b_norm)

    if len(a.shape) == 1 and len(b.shape) == 1:
        if proj > 1.0:
            proj = 1.0
        elif proj < -1.0:
            proj = -1.0
    else:
        proj[proj > 1.0] = 1.0
        proj[proj < -1.0] = -1.0

    theta = np.arccos(proj)
    if degrees:
        theta = np.degrees(theta)

    return theta

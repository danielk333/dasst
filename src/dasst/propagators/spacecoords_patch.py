#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
import numpy as np
from astropy.time import Time
from astropy.coordinates import get_body_barycentric_posvel
import astropy.units as units
import astropy.config as config
import spacecoords.celestial as cel

from dasst.types import (
    NDArray_6,
    NDArray_6xN,
)



def _patched_get_solarsystem_body_state(
    body: str,
    time: Time,
    kernel_dir: Path,
    ephemeris: str = "jpl",
) -> NDArray_6xN | NDArray_6:
    '''
    Fixed some errors I encountered. 
    Mainly with time (not being array-like always)
    and velocity parsing from astropy
    '''

    with config.set_temp_cache(path=str(kernel_dir), delete=False):
        pos, vel = get_body_barycentric_posvel(body, time, ephemeris=ephemeris)

    # Positions: (3,) or (3, N)
    pos_xyz = pos.xyz.to(units.m).value

    # Velocities for both versions:
    # Old one:
    if hasattr(vel, "d_xyz"):
        v_xyz = vel.d_xyz
    # New one:
    else:
        v_xyz = vel.xyz

    vel_xyz = v_xyz.to(units.m / units.s).value

    # Scalar vs vector time fix
    if isinstance(time, Time) and time.isscalar:
        state = np.empty((6,), dtype=np.float64)
        state[:3] = pos_xyz
        state[3:] = vel_xyz
    else:
        size = pos_xyz.shape[-1]
        state = np.empty((6, size), dtype=np.float64)
        state[:3, :] = pos_xyz
        state[3:, :] = vel_xyz

    return state


def patch_spacecoords() -> None:
    cel.get_solarsystem_body_state = _patched_get_solarsystem_body_state

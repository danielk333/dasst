#!/usr/bin/env python

"""Wrapper for the REBOUND propagator into SORTS format.
"""
import pathlib

import numpy as np
from tqdm import tqdm

try:
    import rebound
except ImportError:
    rebound = None

from .. import frames


class Rebound:
    """Implementing the REBOUND propagator.

    Internally in the Rebound simulation a ICRS equivalent is always used but
    output is generated in HCRS.
    """

    DEFAULT_MASSIVE = [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Earth",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
    ]
    DEFAULT_MASSES = [
        1.98855e30,
        7.34767309e22,
        0.330104e24,
        4.86732e24,
        5.97219e24,
        0.641693e24,
        1898.13e24,
        568.319e24,
        86.8103e24,
        102.410e24,
    ]

    DEFAULT_SETTINGS = dict(
        out_frame="HCRS",
        in_frame="HCRS",
        integrator="IAS15",
        time_step=60.0,
        termination_check=False,
        termination_check_interval=1,
        massive_objects=DEFAULT_MASSIVE,
        massive_masses=DEFAULT_MASSES,
        tqdm=True,
    )

    def __init__(self, kernel, settings=None):
        self.sim = None
        assert (
            rebound is not None
        ), "Rebound python package not found, try `pip install rebound`"

        self.settings = dict()
        self.settings.update(self.DEFAULT_SETTINGS)
        if settings is not None:
            self.settings.update(settings)

        self.settings["massive_objects"] = [
            x.strip().capitalize() for x in self.settings["massive_objects"]
        ]

        self.kernel_path = kernel

        self.planets_mass = {
            key: val
            for key, val in zip(
                self.settings["massive_objects"],
                self.settings["massive_masses"],
            )
        }

        self.internal_frame = "HCRS"
        self.geo_internal_frame = "GCRS"
        self._earth_ind = self.planet_index("Earth")
        self._sun_ind = self.planet_index("Sun")
        self.N_massive = len(self.settings["massive_objects"])

    def __str__(self):
        from rebound import __version__, __build__

        s = ""
        s += "---------------------------------\n"
        s += "REBOUND version:     \t%s\n" % __version__
        s += "REBOUND built on:    \t%s\n" % __build__
        if self.sim is not None:
            s += "Number of particles: \t%d\n" % self.sim.N
            s += "Selected integrator: \t" + self.sim.integrator + "\n"
            s += "Simulation time:     \t%.16e\n" % self.sim.t
            s += "Current timestep:    \t%f\n" % self.sim.dt
        s += "---------------------------------"
        return s

    def planet_index(self, name):
        return [x.lower().strip() for x in self.settings["massive_objects"]].index(
            name.lower().strip()
        )

    def _setup_sim(self, epoch, init_massive_states=None):
        kpath = pathlib.Path(self.kernel_path)
        if init_massive_states is None:
            assert kpath.is_file(), f'Could not find "{kpath}" kernel file.'

        self.sim = rebound.Simulation()
        self.sim.units = ("m", "s", "kg")
        self.sim.integrator = self.settings["integrator"]

        if init_massive_states is None:
            bodies = self.settings["massive_objects"]
            assert "Sun" in bodies, "Sun not included, aborting"
            states = frames.get_solarsystem_body_states(
                bodies=bodies,
                epoch=epoch,
                kernel=str(kpath),
            )

            # Convert to HCRS
            for key in states:
                if key != "Sun":
                    states[key] -= states["Sun"]
            states["Sun"] -= states["Sun"]

        for i in range(len(self.settings["massive_objects"])):
            body = self.settings["massive_objects"][i]

            if init_massive_states is None:
                state = states[body]
            else:
                state = init_massive_states[:, i]

            self._add_state(state, self.planets_mass[body])

        self.sim.N_active = self.N_massive
        self.sim.dt = self.settings["time_step"]

    def _add_state(self, state, m):
        x, y, z, vx, vy, vz = state.flatten()
        self.sim.add(
            x=x,
            y=y,
            z=z,
            vx=vx,
            vy=vy,
            vz=vz,
            m=m,
        )

    def termination_check(self, t, step_index, massive_states, particle_states):
        raise NotImplementedError(
            "Users need to implement this method to use termination checks"
        )

    def _put_simulation_state(self, massive_states, particle_states, ti):
        if massive_states is not None:
            for p_n in range(self.N_massive):
                particle = self.sim.particles[p_n]
                massive_states[0, ti, p_n] = particle.x
                massive_states[1, ti, p_n] = particle.y
                massive_states[2, ti, p_n] = particle.z
                massive_states[3, ti, p_n] = particle.vx
                massive_states[4, ti, p_n] = particle.vy
                massive_states[5, ti, p_n] = particle.vz
        if particle_states is not None:
            for p_n in range(len(self.sim.particles) - self.N_massive):
                particle = self.sim.particles[self.N_massive + p_n]
                particle_states[0, ti, p_n] = particle.x
                particle_states[1, ti, p_n] = particle.y
                particle_states[2, ti, p_n] = particle.z
                particle_states[3, ti, p_n] = particle.vx
                particle_states[4, ti, p_n] = particle.vy
                particle_states[5, ti, p_n] = particle.vz
        return massive_states, particle_states

    def _get_helio_state(self):
        sun_state = np.zeros((6,), dtype=np.float64)
        sun = self.sim.particles[self._sun_ind]
        sun_state[0] = sun.x
        sun_state[1] = sun.y
        sun_state[2] = sun.z
        sun_state[3] = sun.vx
        sun_state[4] = sun.vy
        sun_state[5] = sun.vz
        return sun_state

    def _get_earth_state(self):
        earth_state = np.zeros((6,), dtype=np.float64)
        earth = self.sim.particles[self._earth_ind]
        earth_state[0] = earth.x
        earth_state[1] = earth.y
        earth_state[2] = earth.z
        earth_state[3] = earth.vx
        earth_state[4] = earth.vy
        earth_state[5] = earth.vz
        return earth_state

    def propagate(self, t, state0, epoch, **kwargs):
        """Propagate a state"""
        times = epoch + t

        if np.any(t.sec < 0):
            t_order = np.argsort(-t.sec)
        else:
            t_order = np.argsort(t.sec)

        state0_cart = state0

        if len(state0_cart.shape) > 1:
            if state0_cart.shape[1] > 1:
                N_testparticle = state0_cart.shape[1]
            else:
                N_testparticle = 1
        else:
            N_testparticle = 1

        if not (np.all(t.sec <= 0) or np.all(t.sec >= 0)):
            states = np.empty((6, len(t), N_testparticle), dtype=np.float64)
            if N_testparticle == 1:
                states.shape = states.shape[:2]

            ret_backward = self.propagate(t[t.sec < 0], state0, epoch, **kwargs)
            ret_forward = self.propagate(t[t.sec >= 0], state0, epoch, **kwargs)

            massive_states = np.empty((6, len(t), self.N_massive), dtype=np.float64)

            states_b, massive_b = ret_backward
            states_f, massive_f = ret_forward

            massive_states[:, t.sec < 0, :] = massive_b
            massive_states[:, t.sec >= 0, :] = massive_f

            states[:, t.sec < 0, ...] = states_b
            states[:, t.sec >= 0, ...] = states_f

            return states, massive_states

        if np.all(t.sec <= 0):
            backwards_integration = True
            t = -t
        else:
            backwards_integration = False

        t_restore = np.argsort(t_order)
        t = t[t_order]
        times = times[t_order]

        init_massive_states = kwargs.get("massive_states", None)

        self._setup_sim(epoch, init_massive_states=init_massive_states)

        m = kwargs.get("m", np.zeros((N_testparticle,), dtype=np.float64))
        if isinstance(m, float) or isinstance(m, int):
            m = np.zeros((N_testparticle,), dtype=np.float64) * m

        if frames.is_geocentric(self.settings["in_frame"]):
            earth_state = self._get_earth_state()

            state0_cart = frames.convert(
                epoch,
                state0_cart,
                in_frame=self.settings["in_frame"],
                out_frame=self.geo_internal_frame,
            )

            if len(state0_cart.shape) > 1:
                state0_cart = state0_cart + earth_state[:, None]
            else:
                state0_cart = state0_cart + earth_state
        else:
            state0_cart = frames.convert(
                epoch,
                state0_cart,
                in_frame=self.settings["in_frame"],
                out_frame=self.internal_frame,
            )

        if len(state0_cart.shape) > 1:
            for ni in range(N_testparticle):
                self._add_state(state0_cart[:, ni], m[ni])
        else:
            self._add_state(state0_cart, m[0])

        self.sim.move_to_com()

        # Fix for backwards integration, Rebound cannot handle
        # negative times as it is trivial to reverse time
        # TODO: later version of rebound should handle this?
        if backwards_integration:
            for p_ in self.sim.particles:
                p_.vx = -p_.vx
                p_.vy = -p_.vy
                p_.vz = -p_.vz

        massive_states = np.empty((6, len(t), self.N_massive), dtype=np.float64)

        states = np.empty((6, len(t), N_testparticle), dtype=np.float64)
        end_ind = len(t)

        if self.settings["tqdm"]:
            pbar = tqdm(total=len(t), desc="Integrating")

        for ti in range(len(t)):
            self.sim.integrate(t[ti].sec)

            if self.settings["tqdm"]:
                pbar.update(1)

            massive_states, states = self._put_simulation_state(
                massive_states, states, ti
            )

            if frames.is_geocentric(self.settings["out_frame"]):
                earth_state = self._get_earth_state()
                states[:, ti, :] -= earth_state[:, None]
                massive_states[:, ti, :] -= earth_state[:, None]
            else:
                sun_state = self._get_helio_state()
                states[:, ti, :] -= sun_state[:, None]
                massive_states[:, ti, :] -= sun_state[:, None]

            check_interval = ti % self.settings["termination_check_interval"] == 0
            if self.settings["termination_check"] and check_interval:
                if backwards_integration:
                    t__ = -t[ti]
                else:
                    t__ = t[ti]
                if self.termination_check(t__, ti, massive_states, states):
                    end_ind = ti + 1
                    break

        if self.settings["tqdm"]:
            pbar.close()

        if backwards_integration:
            states[3:, :, :] = -states[3:, :, :]
            t = -t

        t = t[0:end_ind]
        times = times[0:end_ind]
        t_restore = t_restore[0:end_ind]
        states = states[:, 0:end_ind, :]

        if frames.is_geocentric(self.settings["out_frame"]):
            int_frame_ = self.geo_internal_frame
        else:
            int_frame_ = self.internal_frame

        for ni in range(N_testparticle):
            states[:, :, ni] = frames.convert(
                times,
                states[:, :, ni],
                in_frame=int_frame_,
                out_frame=self.settings["out_frame"],
            )

        states = states[:, t_restore, :]
        if N_testparticle == 1:
            states.shape = states.shape[:2]

        if backwards_integration:
            massive_states[3:, :, :] = -massive_states[3:, :, :]
        massive_states = massive_states[:, 0:end_ind, :]

        for ni in range(self.N_massive):
            massive_states[:, :, ni] = frames.convert(
                times,
                massive_states[:, :, ni],
                in_frame=int_frame_,
                out_frame=self.settings["out_frame"],
            )

        massive_states = massive_states[:, t_restore, :]

        return states, massive_states

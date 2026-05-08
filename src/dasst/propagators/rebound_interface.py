#!/usr/bin/env python

"""Wrapper for the REBOUND propagator into SORTS format."""

import pathlib
import numpy as np
from tqdm import tqdm
from astropy.time import Time, TimeDelta
import spacecoords.celestial as cel
from ..events import ParticleEvent, write_events_jsonl

try:
    import rebound
except ImportError:
    rebound = None


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
        # New settings for the events:
        exit_max_distance=None,  # meters
        collision=None,  # direct, line, tree from Rebound docs
        # TODO is this required?
        collision_response="log",  # What to do after the collision? Maybe some other options
        massive_radii=None,  # list[float]
        default_particle_radius=0.0,  # meters
        event_log_path=None,
    )

    MASSIVE_HASH_INIT = 1
    TEST_HASH_INIT = 1_000_000

    def __init__(self, kernel, settings=None):
        self.sim: rebound.Simulation | None = None
        assert rebound is not None, (
            "Rebound python package not found, try `pip install rebound`"
        )

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

        self.events: list[ParticleEvent] = []
        self.slot_from_hash: dict[int, int] = {}
        self.massive_from_hash: dict[int, str] = {}
        self.current_epoch: Time | None = None
        self._collision_callback = None

    def _reset_tracking(self, epoch: Time) -> None:
        self.events = []
        self.slot_from_hash = {}
        self.massive_from_hash = {}
        self.current_epoch = epoch

    def _event_epoch_convert(self, sim_time_sec: float) -> str:
        if self.current_epoch is None:
            return ""
        return (self.current_epoch + TimeDelta(sim_time_sec, format="sec")).isot

    def _log_event(
        self,
        *,
        sim_time_sec: float,
        event: str,
        reason: str,
        particle_hash: int,
        other_hash: int | None = None,
        other_name: str | None = None,
        x: float | None = None,
        y: float | None = None,
        z: float | None = None,
    ) -> None:
        self.events.append(
            ParticleEvent(
                sim_time_sec=sim_time_sec,
                epoch_isot=self._event_epoch_convert(sim_time_sec),
                event=event,
                reason=reason,
                particle_hash=particle_hash,
                other_hash=other_hash,
                other_name=other_name,
                x=x,
                y=y,
                z=z,
            )
        )

    def _make_collision_callback(self):

        def collision_return_helper(remove_code: int) -> int:

            response = self.settings["collision_response"]

            if response == "log":
                return 0

            if response == "remove_test":
                return remove_code

            raise ValueError(f"Unknown collision response={response!r}")

        def collision_resolve(sim_pointer, collision):
            sim = sim_pointer.contents

            p1 = sim.particles[collision.p1]
            p2 = sim.particles[collision.p2]

            h1 = int(p1.hash.value)
            h2 = int(p2.hash.value)

            p1_is_massive = h1 in self.massive_from_hash
            p2_is_massive = h2 in self.massive_from_hash

            name1 = self.massive_from_hash.get(h1)
            name2 = self.massive_from_hash.get(h2)

            now = float(sim.t)

            # Case 1: p1 massive, p2 test particle.
            if p1_is_massive and not p2_is_massive:
                self._log_event(
                    sim_time_sec=now,
                    event="collision",
                    reason=f"collision_with_{name1}",
                    particle_hash=h2,
                    other_hash=h1,
                    other_name=name1,
                    x=p2.x,
                    y=p2.y,
                    z=p2.z,
                )
                return collision_return_helper(remove_code=2)

            # Case 2: p2 massive, p1 test particle.
            if p2_is_massive and not p1_is_massive:
                self._log_event(
                    sim_time_sec=now,
                    event="collision",
                    reason=f"collision_with_{name2}",
                    particle_hash=h1,
                    other_hash=h2,
                    other_name=name2,
                    x=p1.x,
                    y=p1.y,
                    z=p1.z,
                )
                return collision_return_helper(remove_code=1)

            # Case 3: test-test collision.
            if not p1_is_massive and not p2_is_massive:
                self._log_event(
                    sim_time_sec=now,
                    event="collision",
                    reason="test_test_collision",
                    particle_hash=h1,
                    other_hash=h2,
                    x=p1.x,
                    y=p1.y,
                    z=p1.z,
                )
                self._log_event(
                    sim_time_sec=now,
                    event="collision",
                    reason="test_test_collision",
                    particle_hash=h2,
                    other_hash=h1,
                    x=p2.x,
                    y=p2.y,
                    z=p2.z,
                )
                return 0

            # Case 4: massive-massive collision.
            self._log_event(
                sim_time_sec=now,
                event="collision",
                reason="massive_massive_collision",
                particle_hash=h1,
                other_hash=h2,
                other_name=name2,
                x=p1.x,
                y=p1.y,
                z=p1.z,
            )
            return 0

        self._collision_callback = collision_resolve
        return collision_resolve

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
        kernel_dir = pathlib.Path(self.kernel_path)
        if init_massive_states is None:
            if not kernel_dir.is_dir():
                raise NotADirectoryError(
                    f"kernel_dir must be a directory, got {kernel_dir}"
                )

        self.sim = rebound.Simulation()
        self.sim.units = ("m", "s", "kg")
        self.sim.integrator = self.settings["integrator"]

        massive_radii = self.settings.get("massive_radii")

        if init_massive_states is None:
            """# Ensure the time argument is array-like
            if isinstance(epoch, Time) and epoch.isscalar:
                t_query = epoch
            else:
                t_query = epoch
            """
            bodies = self.settings["massive_objects"]
            assert "Sun" in bodies, "Sun not included, aborting"

            # Query the state for each body individually
            states = {}
            for body in bodies:
                states[body] = cel.astropy_get_body(
                    body=body,
                    time=epoch,
                    kernel_dir=kernel_dir,
                )
            """
            states = cel.get_solarsystem_body_states(
                bodies=bodies,
                epoch=epoch,
                kernel=str(kpath),
            )
            """

            # Convert to HCRS
            for key in states:
                if key != "Sun":
                    states[key] -= states["Sun"]
            states["Sun"] -= states["Sun"]

        for i, body in enumerate(self.settings["massive_objects"]):
            if init_massive_states is None:
                state = states[body]
            else:
                state = init_massive_states[:, i]
            h = self.MASSIVE_HASH_INIT + i
            self.massive_from_hash[h] = body

            radius = None if massive_radii is None else massive_radii[i]

            self._add_state(state, self.planets_mass[body], hash_value=h, radius=radius)

        self.sim.N_active = self.N_massive
        self.sim.dt = self.settings["time_step"]

        if self.settings.get("collision"):
            self.sim.collision = self.settings["collision"]
            self.sim.collision_resolve = self._make_collision_callback()

        if self.settings.get("exit_max_distance") is not None:
            self.sim.exit_max_distance = float(self.settings["exit_max_distance"])

    def _find_escaped_hash(self) -> list[int]:

        r_max = self.sim.exit_max_distance

        if self.sim.exit_max_distance is None:
            return []

        r_max = float(r_max)
        out: list[int] = []

        for i in range(self.N_massive, len(self.sim.particles)):
            p = self.sim.particles[i]
            r = np.sqrt(p.x * p.x + p.y * p.y + p.z * p.z)
            if r > r_max:
                out.append(int(p.hash.value))
        return out

    def _add_state(self, state, m, hash_value=None, radius=None):
        x, y, z, vx, vy, vz = state.flatten()
        kwargs = dict(x=x, y=y, z=z, vx=vx, vy=vy, vz=vz, m=m)
        if hash_value is not None:
            kwargs["hash"] = int(hash_value)
        if radius is not None:
            kwargs["r"] = float(radius)
        self.sim.add(**kwargs)

        """self.sim.add(
            x=x,
            y=y,
            z=z,
            vx=vx,
            vy=vy,
            vz=vz,
            m=m,
        )
        """

    def _convert_state_at_epoch(self, state: np.ndarray, epoch: Time) -> np.ndarray:
        """
        We need to convert particle state into the current simulation
        coordinate system.

        Heliocentric should be shifted by the current Sun position
        Geocentric must be shifted by the current Earth position
        """

        if cel.is_geocentric(self.settings["in_frame"]):
            state_geo = cel.convert(
                epoch,
                state,
                in_frame=self.settings["in_frame"],
                out_frame=self.geo_internal_frame,
            )

            earth_state = self._get_earth_state()
            return state_geo + earth_state

        state_helio = cel.convert(
            epoch,
            state,
            in_frame=self.settings["in_frame"],
            out_frame=self.internal_frame,
        )

        sun_state = self._get_helio_state()
        return state_helio + sun_state

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
            for i in range(self.N_massive, len(self.sim.particles)):
                p = self.sim.particles[i]
                h = int(p.hash.value)
                slot = self.slot_from_hash[h]
                particle_states[0, ti, slot] = p.x
                particle_states[1, ti, slot] = p.y
                particle_states[2, ti, slot] = p.z
                particle_states[3, ti, slot] = p.vx
                particle_states[4, ti, slot] = p.vy
                particle_states[5, ti, slot] = p.vz
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
        self._reset_tracking(epoch)

        if np.any(t.sec < 0):
            t_order = np.argsort(-t.sec)
        else:
            t_order = np.argsort(t.sec)

        state0_cart = state0

        if len(state0_cart.shape) > 1:
            N_testparticle = state0_cart.shape[1]
        else:
            N_testparticle = 1
            state0_cart = state0_cart.reshape(6, 1)

        birth_times = kwargs.get("birth_times", None)

        # No birth times have been provided,
        # therefore all particles exist from start
        if birth_times is None:
            birth_times = np.zeros(N_testparticle, dtype=float)
        else:
            birth_times = np.asarray(birth_times, dtype=float)

        if birth_times.shape != (N_testparticle,):
            raise ValueError(
                f"Birth times must have shape ({N_testparticle},), got {birth_times.shape}"
            )

        if not np.all(np.isfinite(birth_times)):
            raise ValueError("Birth times must be finite.")

        particle_hashes = kwargs.get("particle_hashes", None)

        if particle_hashes is None:
            particle_hashes = self.TEST_HASH_INIT + np.arange(
                N_testparticle,
                dtype=np.int64,
            )
        else:
            particle_hashes = np.asarray(particle_hashes, dtype=np.int64)

        if particle_hashes.shape != (N_testparticle,):
            raise ValueError(
                f"particle_hashes must have shape ({N_testparticle},), got {particle_hashes.shape}"
            )

        if len(set(map(int, particle_hashes))) != N_testparticle:
            raise ValueError("particle_hashes must be unique.")

        stream_mode = np.any(birth_times > 0.0)

        if stream_mode:
            if np.any(birth_times < 0.0):
                raise ValueError("Stream birth_times must be >= 0.")

            if not np.all(t.sec >= 0):
                raise NotImplementedError(
                    "Stream mode needs forward propagation forwards with times t >= 0."
                )

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

        # init_massive_states = kwargs.get("massive_states", None)

        self._setup_sim(epoch, init_massive_states=kwargs.get("massive_states", None))
        assert self.sim is not None, "Simulation setup failed"

        m = kwargs.get("m", np.zeros((N_testparticle,), dtype=np.float64))
        if isinstance(m, (float, int)):
            m = np.zeros((N_testparticle,), dtype=np.float64) + float(m)

        particle_radii = kwargs.get("particle_radii")
        if particle_radii is None:
            particle_radii = np.full(
                N_testparticle,
                float(self.settings.get("default_particle_radius", 0.0)),
                dtype=float,
            )

        events = np.concat([t, birth_times])
        output_time_index = np.concat(
            [
                np.arange(len(t)),
                np.full(birth_times.shape, -1, dtype=np.int64),
            ]
        )
        event_types = np.concat(
            [
                np.full(t.shape, 0, dtype=np.int32),
                np.full(birth_times.shape, 1, dtype=np.int32),
            ]
        )
        # TODO: use string enum for this
        event_map: dict[str, int] = {
            "output": 0,
            "particle_birth": 1,
        }
        sorted_events = np.argsort(events)
        events = events[sorted_events]
        event_types = event_types[sorted_events]
        output_time_index = output_time_index[sorted_events]

        # Batch mode
        if not stream_mode:
            if cel.is_geocentric(self.settings["in_frame"]):
                earth_state = self._get_earth_state()

                state0_cart_internal = cel.convert(
                    epoch,
                    state0_cart,
                    in_frame=self.settings["in_frame"],
                    out_frame=self.geo_internal_frame,
                )

                state0_cart_internal = state0_cart + earth_state[:, None]
            else:
                state0_cart_internal = cel.convert(
                    epoch,
                    state0_cart,
                    in_frame=self.settings["in_frame"],
                    out_frame=self.internal_frame,
                )

            for ni in range(N_testparticle):
                h = int(particle_hashes[ni])
                self.slot_from_hash[h] = ni
                # h = self.TEST_HASH_INIT + ni
                # self.slot_from_hash[h] = ni

                self._add_state(
                    state0_cart_internal[:, ni],
                    m[ni],
                    hash_value=h,
                    radius=particle_radii[ni],
                )
            self.sim.move_to_com()

        # Stream mode
        else:
            # TODO
            # make sure the coordinate system of added particles are correct
            self.sim.move_to_com()

        massive_states = np.empty((6, len(t), self.N_massive), dtype=np.float64)

        states = np.full((6, len(t), N_testparticle), np.nan, dtype=np.float64)

        end_ind = len(t)

        if self.settings["tqdm"]:
            pbar = tqdm(total=len(events), desc="Integrating")

        for ind, (event_t, event_type) in enumerate(zip(events, event_types)):
            try:
                self.sim.integrate(event_t.sec)
            # rebound.Collision is handled by the callback, only escape raises
            except rebound.Escape:
                escaped_hashes = self._find_escaped_hash()

                if not escaped_hashes:
                    raise

                for h in escaped_hashes:
                    p = self.sim.particles[rebound.hash(h)]

                    self._log_event(
                        sim_time_sec=float(self.sim.t),
                        event="escape",
                        reason="exit_max_distance_exceeded",
                        particle_hash=h,
                        x=p.x,
                        y=p.y,
                        z=p.z,
                    )

                    self.sim.remove(hash=rebound.hash(h))
                self.sim.integrate(event_t.sec)
            if event_type == event_map["output"]:
                ti = output_time_index[ind]
                massive_states, states = self._put_simulation_state(
                    massive_states, states, ti
                )

                if cel.is_geocentric(self.settings["out_frame"]):
                    earth_state = self._get_earth_state()
                    states[:, ti, :] -= earth_state[:, None]
                    massive_states[:, ti, :] -= earth_state[:, None]
                else:
                    sun_state = self._get_helio_state()
                    states[:, ti, :] -= sun_state[:, None]
                    massive_states[:, ti, :] -= sun_state[:, None]
            elif event_type == event_map["particle_birth"]:
                pass
                # TODO: add state here

            if self.settings["tqdm"]:
                pbar.update(1)

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

        if cel.is_geocentric(self.settings["out_frame"]):
            int_frame_ = self.geo_internal_frame
        else:
            int_frame_ = self.internal_frame

        """
        for ni in range(N_testparticle):
            if not np.all(np.isnan(states[:,:,ni])):
                states[:, :, ni] = cel.convert(
                    times,
                    states[:, :, ni],
                    in_frame=int_frame_,
                    out_frame=self.settings["out_frame"],
                    )
        """

        # In stream mode, states before birth are NaN by design.
        for ni in range(N_testparticle):
            valid = np.all(np.isfinite(states[:, :, ni]), axis=0)

            if np.any(valid):
                states[:, valid, ni] = cel.convert(
                    times,
                    states[:, valid, ni],
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
            massive_states[:, :, ni] = cel.convert(
                times,
                massive_states[:, :, ni],
                in_frame=int_frame_,
                out_frame=self.settings["out_frame"],
            )

        massive_states = massive_states[:, t_restore, :]

        if self.settings.get("event_log_path"):
            write_events_jsonl(self.events, self.settings["event_log_path"])

        return states, massive_states

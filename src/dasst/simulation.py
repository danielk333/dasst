#!/usr/bin/env python
import tomllib
import numpy as np
from pathlib import Path
from dasst.propagators import Rebound
from astropy.time import Time, TimeDelta
from dataclasses import dataclass, field
from dasst.populations import PopulationConfig, realise_population
from dasst.types import NDArray_6xN
from typing import Dict,Any,Optional,List, Tuple


def _propagation_stuff(stuff):
    #TODO
    pass

#TODO
#_propagation_stuff(stuff)
# distribute hashes
# collect hashes into groups
# save reason for missing particles (sim exit, collision, ...)
        
        
        

@dataclass
class SimConfig:
    '''
    Simulation parameters, loaded from a TOML file.
    '''
    simulation_epoch: str
    simulation_time: float
    time_step: float
    tqdm: bool
    kernel_path: str
    integrator: str = "IAS15"
    in_frame: str = "ITRS"
    out_frame: str = "ITRS"
    seed: Optional[int] = None

    # Sub-configs
    reboundx: Dict[str, Any] = field(default_factory=dict)
    massive_objects: List[str] = field(default_factory=list)
    massive_masses: List[float] = field(default_factory=list) 
    massive_radii: List[Optional[float]] = field(default_factory=list)

    # Additional tracking logic
    tracking: Dict[str, Any] = field(default_factory=dict)
    

    @property 
    def epoch(self) -> Time:
        return Time(self.simulation_epoch, format="isot", scale="utc")
    
    def make_timeline(self) -> TimeDelta:
        n_steps = int(np.floor(self.simulation_time / self.time_step)) + 1
        t_vals = np.arange(0.0, n_steps * self.time_step, self.time_step, dtype=float)
        return TimeDelta(t_vals, format="sec")

class Simulation:
    def __init__(
        self,
        config: SimConfig,
    ) -> None:
        self.config = config
        self.rng = np.random.default_rng(config.seed)

    @classmethod
    def from_toml(cls, path: str | Path) -> "Simulation":
        '''
        Load configuration parameters from a single TOML file that contains both
        [simulation] and [bodies] sections.
        '''
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
        return cls._from_data_dict(data)

    @classmethod
    def from_tomls(cls, sim_path: str | Path, bodies_path: str | Path) -> "Simulation":
        '''
        Load configuration parameters from two TOML files:
            -sim_path which contains [simulation]
            -bodies_path which contains [bodies]
        '''

        with open(sim_path, "rb") as fh:
            sim_data = tomllib.load(fh)
        with open(bodies_path, "rb") as fh:
            bodies_data = tomllib.load(fh)
        data: Dict[str, Any] = {}

        if "simulation" not in sim_data:
            raise ValueError("sim_config TOML is missing [simulation]")
        if "bodies" not in bodies_data:
            raise ValueError("bodies_config TOML is missing [bodies]")
        
        data["simulation"] = sim_data["simulation"]
        data["bodies"] = bodies_data["bodies"]
        return cls._from_data_dict(data)
    
    @classmethod
    def _from_data_dict(cls, data: Dict[str, Any]) -> "Simulation":
        '''
        Parse the previously read parameters from TOMLs.
        '''

        sim_config = data.get("simulation", {})
        if not sim_config:
            raise ValueError("TOML file is missing [simulation] parameters!")

        config = SimConfig(
            simulation_epoch = sim_config["sim_epoch"],
            simulation_time = float(sim_config["sim_time"]),
            time_step = float(sim_config["dt"]),
            tqdm = bool(sim_config.get("tqdm", True)),
            kernel_path = sim_config["kernel_path"],
            integrator = sim_config.get("integrator", "IAS15"),
            in_frame = sim_config.get("in_frame", "ITRS"),
            out_frame = sim_config.get("out_frame", "ITRS"),
            seed = sim_config.get("seed"),
        )

        # ReboundX configuration 
        config.reboundx = sim_config.get("reboundx", {})

        # Tracking
        tracking = sim_config.get("rebound_tracking", {})
        config.tracking = tracking

        # Bodies
        bodies = data.get("bodies", {})
        bodies_massive = bodies.get("massive", {})
        bodies_collision_radius = bodies.get("collision_radius", {})

        if not bodies_massive:
            raise ValueError("TOML file is missing [bodies.massive] parameters.")
        
        if not isinstance(bodies_collision_radius, dict):
            raise ValueError("[bodies.collision_radius] must be a table if provided.")

        # Map the body to its mass.
        #TODO Remove the requirement for Earth to be included in every case.
        config.massive_objects = list(bodies_massive.keys())
        config.massive_masses = [float(bodies_massive[name]) for name in config.massive_objects]

        unknown_radius_bodies = set(bodies_collision_radius) - set(config.massive_objects)
        if unknown_radius_bodies:
            raise ValueError(
                "[bodies.collision_radius] contains bodies not listed in [bodies.massive]:" \
                f"{sorted(unknown_radius_bodies)}"
            )
        
        config.massive_radii = [
            float(bodies_collision_radius[name])
            if name in bodies_collision_radius
            else None
            for name in config.massive_objects
        ]
        return cls(config=config)

    def create_simulation(
            self, 
            use_reboundx: bool = True,
            in_frame: str | None = None
            ) -> Rebound:
        
        config = self.config
        massive_objects = config.massive_objects or Rebound.DEFAULT_MASSIVE
        massive_masses = config.massive_masses or Rebound.DEFAULT_MASSES

        settings = dict(
            massive_objects = massive_objects,
            massive_masses = massive_masses,
            massive_radii=config.massive_radii or None,
            in_frame = in_frame or config.in_frame,
            out_frame = config.out_frame,
            integrator = config.integrator,
            time_step = config.time_step,
            tqdm = config.tqdm
        )
        
        settings.update(config.tracking)

        if use_reboundx and config.reboundx:
            print("ReboundX on!")
            settings["reboundx"] = config.reboundx

        return Rebound(kernel=config.kernel_path, settings=settings)
    
    def propagate(
            self,
            states: NDArray_6xN,
            frame: str,
            use_rebound: bool,
            birth_times: Optional[np.ndarray] = None,
    ) -> Dict[str,Any]:
        
        config = self.config
        t = config.make_timeline()
        epoch = config.epoch

        n_particles = states.shape[1] if states.ndim > 1 else 1
        
        particle_hashes = (
            Rebound.TEST_HASH_INIT + np.arange(n_particles, dtype=np.int64)
        )

        if birth_times is None:
            birth_times = np.zeros(n_particles, dtype=float)
        
        else:
            birth_times = np.asarray(birth_times, dtype=float)
        
        if birth_times.shape != (n_particles,):
            raise ValueError(
                f"Birth times must have shape ({n_particles},), got {birth_times.shape}"
            )

        if not np.all(np.isfinite(birth_times)):
            raise ValueError(f"Birth times must be finite.")
        
        if np.any(birth_times < 0.0):
            raise ValueError(f"Negative birth times are not allowed.")

        reb = self.create_simulation(use_reboundx=use_rebound, in_frame=frame)

        particles_states, massive_states = reb.propagate(
            t, 
            states, 
            epoch,
            birth_times=birth_times,
            particle_hashes=particle_hashes,
            )
        
        if particles_states.ndim == 2:
            particles_states = particles_states[:,:,None]
        
        return dict(
            t=t,
            epoch=epoch,
            particles_states=particles_states, # (6,T,N)
            particle_birth_times=birth_times,
            massive_states = massive_states,
            particle_hashes=particle_hashes,
            rebound=reb,
            particle_events=reb.events,
        )
    
    def run(
        self,
        populations: Optional[List[PopulationConfig]] = None,
        states: Optional[NDArray_6xN] = None,
        frame: Optional[str] = None,
        use_rebound: bool = True,   
        birth_times: Optional[np.ndarray] = None,
    ) -> Dict[str,Any]:
        
        if populations is not None:
            all_states_list: List[NDArray_6xN] = []
            all_birth_times_list: List[np.ndarray] = []
            offsets: Dict[str, Tuple[int,int]] = {}
            start=0

            for pop_config in populations:
                pop_states, pop_birth_times, _ = realise_population(pop_config, self.rng)
                
                n = pop_states.shape[1]
                end = start + n

                offsets[pop_config.name] = (start,end)
                all_states_list.append(pop_states)
                all_birth_times_list.append(pop_birth_times)
                
                start = end

            if not all_states_list:
                raise ValueError("No populations provided.")
            
            all_states = np.concatenate(all_states_list, axis=1) # (6,N_total)
            all_birth_times = np.concatenate(all_birth_times_list, axis=0)
            
            #TODO They probably dont all have the same input frame
            #input_frame = populations[0].frame
            frames = {pop_config.frame for pop_config in populations}
            if len(frames) != 1:
                raise NotImplementedError(
                    f"Multiple population input frames not yet supported: {sorted(frames)}"
                )
            input_frame = next(iter(frames))

            ret = self.propagate(
                states=all_states,
                birth_times=all_birth_times,
                frame=input_frame,
                use_rebound=use_rebound,
            )

            particles_states = ret["particles_states"] # (6,T,N_total)
            massive_states = ret["massive_states"]
            t = ret["t"]
            epoch = ret["epoch"]

            # Split it back per population
            populations_out: Dict[str, NDArray_6xN] = {}
            populations_birth_times: Dict[str, np.ndarray] = {}
            particle_hashes = ret["particle_hashes"]
            populations_hashes: Dict[str, np.ndarray] = {}
            particle_lookup: Dict[int, Dict[str,Any]] = {}


            for pop_config in populations:
                name = pop_config.name
                start, end = offsets[name]
                populations_out[name] = particles_states[:,:, start:end]
                populations_birth_times[name] = all_birth_times[start:end]
                populations_hashes[name] = particle_hashes[start:end]

                for local_index, global_index in enumerate(range(start,end)):
                    h = int(particle_hashes[global_index])
                    particle_lookup[h] = dict(
                        population=name,
                        local_index=local_index,
                        global_index=global_index,
                    )
            
            return dict(
                t=t,
                epoch=epoch,
                massive_states=massive_states,
                populations=populations_out,
                populations_birth_times=populations_birth_times,
                particle_hashes=populations_hashes,
                particle_lookup=particle_lookup,
                particle_events=ret["particle_events"],
            )
        
        if states is None:
            raise ValueError("Either populations or states must be provided")

        if frame is None:
            frame = self.config.in_frame
        
        return self.propagate(
            states=states,
            frame=frame,
            birth_times=birth_times,
            use_rebound=use_rebound,
        )

## -- use case below 

'''
comet_init = scipy.ndnormal(mu, cov) 
comet_init = get_from_jpl("kernel.path", 10_000) 
mysim = Simulation( distributed_bodies={"comet": (0, comet_init)}, )


## -- use case 
comet_init = get_from_jpl("kernel.path") 
mysim = Simulation( distributed_bodies={"comet": (0, comet_init)}, ) 
 ... 
comet_states # result of above sim 
t, test_particles = particle_generator(comet_states, ...)
big_sim = Simulation( distributed_bodies={"meteoroids": (t, test_particles)}, )
'''

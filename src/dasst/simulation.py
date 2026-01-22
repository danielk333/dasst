#!/usr/bin/env python
import toml
import numpy as np
from pathlib import Path
from dasst.propagators import Rebound
from astropy.time import Time, TimeDelta
from dataclasses import dataclass, field
from dasst.populations import PopulationConfig, realise_population
from dasst.types import NDArray_6xN, NDArray_N
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
        data = toml.load(str(path))
        return cls._from_data_dict(data)

    @classmethod
    def from_tomls(cls, sim_path: str | Path, bodies_path: str | Path) -> "Simulation":
        '''
        Load configuration parameters from two TOML files:
            -sim_path which contains [simulation]
            -bodies_path which contains [bodies]
        '''

        sim_data = toml.load(str(sim_path))
        bodies_data = toml.load(str(bodies_path))
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

        # Bodies
        bodies = data.get("bodies", {})
        bodies_massive = bodies.get("massive", {})

        # Map the body to its mass.
        #TODO Remove the requirement for Earth to be included in every case.
        config.massive_objects = list(bodies_massive.keys())
        config.massive_masses = [float(bodies_massive[name]) for name in config.massive_objects]

        return cls(config=config)

    def create_simulation(self, use_reboundx: bool = True) -> Rebound:
        
        config = self.config
        massive_objects = config.massive_objects or Rebound.DEFAULT_MASSIVE
        massive_masses = config.massive_masses or Rebound.DEFAULT_MASSES

        settings = dict(
            massive_objects = massive_objects,
            massive_masses = massive_masses,
            in_frame = config.in_frame,
            out_frame = config.out_frame,
            integrator = config.integrator,
            time_step = config.time_step,
            tqdm = config.tqdm
        )
        
        if use_reboundx and config.reboundx:
            print("ReboundX on!")
            settings["reboundx"] = config.reboundx

        return Rebound(kernel=config.kernel_path, settings=settings)
    
    def propagate(
            self,
            states: NDArray_6xN,
            ids: NDArray_N,
            frame: str,
            use_rebound: bool,
    ) -> Dict[str,Any]:
        
        config = self.config
        t = config.make_timeline()
        epoch = config.epoch

        reb = self.create_simulation(use_reboundx=use_rebound)

        particles_states, massive_states = reb.propagate(t, states, epoch)
        if particles_states.ndim == 2:
            particles_states = particles_states[:,:,None]
        
        return dict(
            t=t,
            epoch=epoch,
            particles_states=particles_states, # (6,T,N)
            massive_states = massive_states,
            particle_ids=ids,
            rebound=reb,
        )
    
    def run(
        self,
        populations: Optional[List[PopulationConfig]] = None,
        states: Optional[NDArray_6xN] = None,
        ids: Optional[NDArray_N] = None,
        frame: Optional[str] = None,
        use_rebound: bool = True,   
    ) -> Dict[str,Any]:
        
        if populations is not None:
            all_states_list: List[NDArray_6xN] = []
            all_ids_list: List[NDArray_N] = []
            offsets: Dict[str, Tuple[int,int]] = {}
            start=0

            for pop_config in populations:
                pop_states, pop_ids, meta = realise_population(pop_config, self.rng)
                n = pop_states.shape[1]
                end = start + n

                offsets[pop_config.name] = (start,end)
                all_states_list.append(pop_states)
                all_ids_list.append(pop_ids)
                start = end
            if not all_states_list:
                raise ValueError("No populations provided.")
            
            all_states = np.concatenate(all_states_list, axis=1) # (6,N_total)
            all_ids = np.concatenate(all_ids_list,axis=0) # (N_total,)
            
            #TODO They probably dont all have the same input frame
            input_frame = populations[0].frame

            ret = self.propagate(
                states=all_states,
                ids=all_ids,
                frame=input_frame,
                use_rebound=use_rebound,
            )

            particles_states = ret["particles_states"] # (6,T,N_total)
            massive_states = ret["massive_states"]
            t = ret["t"]
            epoch = ret["epoch"]

            # Split it back per population
            populations_out: Dict[str, NDArray_6xN] = {}
            populations_ids: Dict[str, NDArray_N] = {}

            for pop_config in populations:
                name = pop_config.name
                start, end = offsets[name]
                populations_out[name] = particles_states[:,:, start:end]
                populations_ids[name] = all_ids[start:end]
            
            return dict(
                t=t,
                epoch=epoch,
                massive_states=massive_states,
                populations=populations_out,
                particles_ids=populations_ids,
            )
        
        if states is None:
            raise ValueError("Either populations or states must be provided")
        
        if ids is None:
            n=states.shape[1]
            ids = self.rng.integers(
                low=0,
                high=np.iinfo(np.uint64).max,
                size=n,
                dtype=np.uint64,
            )

        if frame is None:
            frame = self.config.in_frame
        
        return self.propagate(
            states=states,
            ids=ids,
            frame=frame,
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
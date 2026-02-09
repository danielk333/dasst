#!/usr/bin/env python

from __future__ import annotations
import tomllib
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from dasst.types import NDArray_6xN, NDArray_N
from typing import Dict, Any, Optional, Literal, Tuple


@dataclass
class PopulationConfig:
    """
    Configuration for a single particle population (e.g. comet cloud),
    loaded from a TOML file.
    """
    name: str
    frame: str
    # So far, only batch mode is implemented
    mode: Literal["batch", "stream"] 
    # Do we read from a distribution or a provided file?
    source: Literal["distribution", "file"] 

    # Distribution based
    dist_type: Optional[str] = None
    n_particles: Optional[int] = None
    mu: Optional[np.ndarray] = None # shape (6,)
    cov: Optional[np.ndarray] = None # shape (6,6)

    # File based, path to .npy 
    states_file: Optional[str] = None 

    # For future stream mode, seconds after simulation epoch
    birth_time: float = 0.0 

    @classmethod
    def from_toml(cls, path: str | Path) -> "PopulationConfig":
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
        pop_cfg = data.get("population", {})
        if not pop_cfg:
            raise ValueError("TOML is missing [population] section.")

        name   = pop_cfg["name"]
        frame  = pop_cfg.get("frame", "HCRS")
        mode   = pop_cfg.get("mode", "batch")
        source = pop_cfg.get("source", "distribution")

        cfg = cls(
            name=name,
            frame=frame,
            mode=mode,
            source=source,
        )

        # We generate the particles based on our probability function
        if source == "distribution":
            dist_cfg = pop_cfg.get("distribution", {})
            dist_type   = dist_cfg.get("type", "normal")
            n_particles = int(dist_cfg["n_particles"])

            # Normal probability distribution
            if dist_type == "normal":
                mu  = np.array(dist_cfg["mu"],  dtype=float).reshape(6)
                cov = np.array(dist_cfg["cov"], dtype=float).reshape(6, 6)
                cfg.dist_type   = "normal"
                cfg.n_particles = n_particles
                cfg.mu          = mu
                cfg.cov         = cov
            else:
                raise ValueError(f"Unsupported distribution type {dist_type!r}")

        # We are provided with a file to read from
        elif source == "file":
            cfg.states_file = pop_cfg["states_file"]
            cfg.birth_time  = float(pop_cfg.get("birth_time", 0.0))

        else:
            raise ValueError(f"Unknown source {source!r}")

        '''
        # optional birth_time at the population level
        if "birth_time" in pop_cfg:
            cfg.birth_time = float(pop_cfg["birth_time"])
        '''

        return cfg

   
def realise_population(
    pop_cfg: PopulationConfig,
    rng: np.random.Generator,
) -> Tuple[NDArray_6xN, NDArray_N, Dict[str, Any]]:
    
    '''
    Given a PopulationConfig and RNG, generate 6xN states and N IDs.
    '''
    if pop_cfg.mode != "batch":
        raise NotImplementedError("Only batch mode supported for now.")
    
    if pop_cfg.source == "distribution":
        if pop_cfg.dist_type == "normal":
            mu  = pop_cfg.mu
            cov = pop_cfg.cov
            n   = pop_cfg.n_particles
            if mu is None or cov is None or n is None:
                raise ValueError("PopulationConfig missing mu/cov/n_particles.")
            samples = rng.multivariate_normal(mean=mu, cov=cov, size=n)  # (N,6)
            states  = samples.T  # (6, N)
        else:
            raise ValueError(f"Unsupported dist_type {pop_cfg.dist_type!r}")
    elif pop_cfg.source == "file":
        if pop_cfg.states_file is None:
            raise ValueError("states_file must be set for source='file'")
        states = np.load(pop_cfg.states_file)  # expecting (6, N)
        if states.shape[0] != 6:
            raise ValueError(f"States must be (6, N), got {states.shape}")
    else:
        raise ValueError(f"Unknown source {pop_cfg.source!r}")
    
    # IDs
    n = states.shape[1]
    ids = rng.integers(
        low=0,
        high=np.iinfo(np.uint64).max,
        size=n,
        dtype=np.uint64,
    )
    meta = dict(
        name=pop_cfg.name,
        frame=pop_cfg.frame,
        birth_time=pop_cfg.birth_time,
    )
    return states, ids, meta

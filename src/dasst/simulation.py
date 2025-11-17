from typing import Callable
from abc import abstractmethod

from .types import NDArray_6xN


def _propagation_stuff(stuff):
    pass


class Simulation:

    def __init__(
        self,
        integrator,
        minimum_stepsize,
        jpl_kernels,
    ):
        pass

    @classmethod
    def from_toml(cls, path):
        pass

    def run(self):
        _propagation_stuff(stuff)
        # distribute hashes
        # collect hashes into groups
        # save reason for missing particles (sim exit, collision, ...)



## -- use case below


comet_init = scipy.ndnormal(mu, cov)
comet_init = get_from_jpl("kernel.path", 10_000)

mysim = Simulation(
    distributed_bodies={"comet": (0, comet_init)},
)


## -- use case


comet_init = get_from_jpl("kernel.path")

mysim = Simulation(
    distributed_bodies={"comet": (0, comet_init)},
)
...
comet_states  # result of above sim

t, test_particles = particle_generator(comet_states, ...)

big_sim = Simulation(
    distributed_bodies={"meteoroids": (t, test_particles)},
)

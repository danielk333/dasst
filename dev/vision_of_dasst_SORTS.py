import dasst
import SORTS

#this already contains all the distribution parameters and everything
from my_pop import my_pop, settings

#this is a child of SpaceObject that implements get_orbit from a cashed result 
# output generated by "dasst", using interpolation 
# (chebychev polynomials probably)
from my_space_object import MySpaceObject, stuff


p = dasst.propagator.Orekit(**settings);
save = dasst.persistence.BinarySet('./cache/')

#this will default to DMC
sim = dasst.Simulation(
    propagator=p,
    population=my_pop, 
    persistence={'results':save},
)

sim.sample(10000)

for res in sim.results:
    myso = MySpaceObject(res)

    sorts_sim = SORTS.Simulation(myso, **stuff)

    sorts_sim.run()

    #collect results so that statistical result can be compiled
    sorts_sim.results
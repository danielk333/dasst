#everything is test particles

#setup sim is multistep procedure
#1. compile propagator
#2. precalculate dynamics
#3. sample test particles using cached dynamics
#4. is optimal for MCMC, DMC, HMC, ect and for paralellization


#we are completly dependant on REBOUND so return a rebound wrapped class
#allows particle generators ect ect
#add particle
#optimal unit system????
#proper suite of settings
#
#
# convenience functions for linking and creating heartbeat functions
# and merger functions ect ect
# to add new propagator: pull request to rebound
# implement rebondX as well, and add option to compile custom additonal_force
# 


#output should be compatible with density calculations ect
#mcmc should do what? it is called a sampler
#two types: sequentioal and paralell (MCMC Vs DMC)
#both generate test particle initial states
#how about particle generator properties?
#sampler takes a particle generator as well?
#only physics parameters are avalible to the sampler



#some standard rebound configurations
# - meteor shower simulation (DMC, MCMC)
# - Parent body search (DMC from measurnments), output parameters are function values like d-criterions
# - backwards/forwards stabillity check
# - "zenith attraction removal"
#
# The wrapper and functions should be able to accomodate all these applicatons
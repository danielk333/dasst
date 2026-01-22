#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from dasst.simulation import Simulation
from dasst.populations import PopulationConfig
from dasst.constants import AU, YEAR

SIM_CONFIG = Path("/home/matej/Desktop/dasst/src/dasst/sim_config.toml")
BODIES_CONFIG = Path("/home/matej/Desktop/dasst/src/dasst/bodies_config.toml")
POP_COMET = Path("/home/matej/Desktop/dasst/src/dasst/pop_comet.toml")
NPZ_PATH = Path("/home/matej/Desktop/dasst/comet_run1.npz")

def plot_full_system(result: dict, sim: Simulation):
    """
    Plot Sun + all massive bodies + comet population, with reference circles.
    """

    massive = result["massive_states"] # (6, T, N_massive)
    populations = result.get("populations", {})
    massive_names = sim.config.massive_objects  # ["Sun","Earth","Mars",...]

    # Extract data for massive bodies
    xM = massive[0] / AU   # (T, N_massive)
    yM = massive[1] / AU    # (T, N_massive)

    # Comet data
    comets = populations.get("comet", None) # (6, T, N_comet) or None

    fig, ax = plt.subplots(figsize=(8, 8))

    # Plot massive bodies
    for j, name in enumerate(massive_names):
        ax.plot(xM[:, j], yM[:, j], label=name)
        ax.scatter(xM[0, j], yM[0, j], s=30)  # initial position

    # Plot comets if present
    if comets is not None:
        T, N = comets.shape[1], comets.shape[2]
        rng = np.random.default_rng(sim.config.seed)
        idx = rng.choice(N, size=min(200, N), replace=False)

        # trajectories
        for i in idx:
            x = comets[0, :, i] / AU
            y = comets[1, :, i] / AU
            ax.plot(x, y, alpha=0.15, color="gray")

        # initial positions
        x0 = comets[0, 0, idx] / AU
        y0 = comets[1, 0, idx] / AU
        ax.scatter(x0, y0, s=10, color="C3", alpha=0.8, label="Comet start")

        # final positions
        xF = comets[0, -1, idx] / AU
        yF = comets[1, -1, idx] / AU
        ax.scatter(xF, yF, s=10, color="C4", alpha=0.8, label="Comet end")

    # Sun at origin
    ax.scatter([0.0], [0.0], s=60, color="k", label="Sun")

    # Radii of massive bodies
    rM = np.sqrt(xM**2 + yM**2).max()

    # Radii of comets
    if comets is not None:
        xC = comets[0] / AU
        yC = comets[1] / AU
        rC = np.sqrt(xC**2 + yC**2).max()
    else:
        rC = 0.0

    r_data_max = max(rM, rC, 1e-3)  
    r_pad      = 0.2 * r_data_max   
    r_lim      = r_data_max + r_pad

    # Set symmetric limits around Sun
    ax.set_xlim(-r_lim, r_lim)
    ax.set_ylim(-r_lim, r_lim)

    # Draw reference circles only up to r_lim
    candidate_radii = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]  # AU
    for r_au in candidate_radii:
        if r_au <= r_lim * 1.01:  # only if circle is within plotted region
            circle = plt.Circle((0.0, 0.0), r_au, fill=False,
                                linestyle=":", alpha=0.3)
            ax.add_artist(circle)
            ax.text(r_au, 0.0, f"{r_au} AU", fontsize=8, alpha=0.7)

    ax.set_aspect("equal", "box")
    ax.set_xlabel("x [AU]")
    ax.set_ylabel("y [AU]")
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.show()

# Run from TOML configs (sim + bodies + population) and then save
def run_and_save() -> dict:
    print("=== Running from TOMLs ===")

    # Build Simulation from sim_config + bodies_config
    sim = Simulation.from_tomls(SIM_CONFIG, BODIES_CONFIG)

    # Load comet population config
    comet_cfg = PopulationConfig.from_toml(POP_COMET)

    result = sim.run(populations=[comet_cfg], use_rebound=False)

    plot_full_system(result, sim)

    t = result["t"]  # astropy TimeDelta (T,)
    epoch = result["epoch"] # astropy Time
    massive = result["massive_states"] # (6, T, N_massive)
    populations = result["populations"] # dict[name -> (6, T, N)]
    particles_ids = result["particles_ids"]  # dict[name -> (N,)]
    comets = populations["comet"] # (6, T, N_comet)
    comet_ids = particles_ids["comet"] # (N_comet,)

    print("t shape:", t.shape)
    print("comets shape:", comets.shape)
    print("massive shape:", massive.shape)

    N = comets.shape[2]
    idx = np.random.default_rng(sim.config.seed).choice(N, size=min(50, N), replace=False)

    plt.figure(figsize=(7, 6))
    for i in idx:
        x = comets[0, :, i] / AU
        y = comets[1, :, i] / AU
        plt.plot(x, y, alpha=0.5)

    # Sun at origin
    plt.scatter([0.0], [0.0], s=40, color="k", label="Sun")

    xE = massive[0, :, 1] / AU
    yE = massive[1, :, 1] / AU
    plt.plot(xE, yE, "--", label="Earth")

    plt.gca().set_aspect("equal", "box")
    plt.xlabel("x [AU]")
    plt.ylabel("y [AU]")
    plt.title("Comet trajectories from TOMLs")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Save as npz
    t_sec = t.sec  # TimeDelta to seconds array

    np.savez(
        NPZ_PATH,
        t_sec=t_sec,
        epoch=epoch.isot,
        states=comets, # (6, T, N)
        massive=massive,# (6, T, N_massive)
        ids=comet_ids, # (N,)
        frame_out=sim.config.out_frame,
        population_name=comet_cfg.name,
    )

    print(f"Saved NPZ to: {NPZ_PATH}")

# Load the NPZ, rerun from t=0 states and compare
def run_and_verify():
    print("=== Running from NPZ ===")

    # Rebuild Simulation from the same sim_config + bodies_config
    sim2 = Simulation.from_tomls(SIM_CONFIG, BODIES_CONFIG)

    # Load the shared NPZ file
    data = np.load(NPZ_PATH, allow_pickle=True)
    t_sec_saved = data["t_sec"] # (T,)
    epoch_str = data["epoch"].item() # string
    states_saved = data["states"] # (6, T, N)
    massive_saved = data["massive"] # (6, T, N_massive)
    ids_saved = data["ids"] # (N,)
    frame_out = data["frame_out"].item()
    population_name = data["population_name"].item()

    print("Loaded NPZ:")
    print("  epoch_str:", epoch_str)
    print("  frame_out:", frame_out)
    print("  states_saved shape:", states_saved.shape)
    print("  massive_saved shape:", massive_saved.shape)
    print("  ids_saved shape:", ids_saved.shape)

    # t=0 of comets as initial states for the verification run
    states0 = states_saved[:, 0, :] # (6, N)
    ids0 = ids_saved # (N,)

    # Assuming the input frame for the states is the same as frame_out 
    input_frame = frame_out

    # Rerun
    result2 = sim2.run(
        states=states0,
        ids=ids0,
        frame=input_frame,
        use_rebound=False,
    )

    t2 = result2["t"] # astropy TimeDelta (T2,)
    epoch2 = result2["epoch"] # astropy Time
    states2 = result2["particles_states"] # (6, T2, N)
    massive2 = result2["massive_states"]  # (6, T2, N_massive)

    print("Verification run:")
    print("t2 shape:", t2.shape)
    print("states2 shape:", states2.shape)
    print("massive2 shape:", massive2.shape)
    print("epoch2:", epoch2.isot)

    # Check that time grids match 
    same_time_grid = np.allclose(t_sec_saved, t2.sec)
    print("Time grids match?", same_time_grid)

    # Compare the full trajectories: original vs rerun
    if states_saved.shape == states2.shape and massive_saved.shape == massive2.shape:
        diff_particles = np.max(np.abs(states_saved - states2))
        diff_massive   = np.max(np.abs(massive_saved - massive2))
        print("max |states_saved - states2|:", diff_particles)
        print("max |massive_saved - massive2|:", diff_massive)
    else:
        print("shapes differ")

    # Overlay a single comet orbit: original vs rerun
    i_example = 0  # First comet

    x1 = states_saved[0, :, i_example] / AU
    y1 = states_saved[1, :, i_example] / AU

    x2 = states2[0, :, i_example] / AU
    y2 = states2[1, :, i_example] / AU

    plt.figure(figsize=(7, 6))
    plt.plot(x1, y1, label="Original", alpha=0.7)
    plt.plot(x2, y2, "--", label="Rerun", alpha=0.7)

    xE2 = massive2[0, :, 1] / AU
    yE2 = massive2[1, :, 1] / AU
    plt.plot(xE2, yE2, "k--", label="Earth (verification run)")

    plt.scatter([0.0], [0.0], s=40, color="k", label="Sun")

    plt.gca().set_aspect("equal", "box")
    plt.xlabel("x [AU]")
    plt.ylabel("y [AU]")
    plt.title(f"Orbit comparison for comet index {i_example} ({population_name})")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Radial difference over time for that comet
    r1 = np.sqrt(x1**2 + y1**2)
    r2 = np.sqrt(x2**2 + y2**2)
    dr = r2 - r1

    t_years = t2.sec / YEAR

    plt.figure(figsize=(8, 4))
    plt.plot(t_years, dr)
    plt.axhline(0.0, color="k", linewidth=0.8)
    plt.xlabel("Time [years]")
    plt.ylabel("Δr (rerun - original) [AU]")
    plt.title("Radial difference")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Firs run using TOMLs and save to NPZ
    run_and_save()

    # Secondly verify based on the NPZ
    run_and_verify()

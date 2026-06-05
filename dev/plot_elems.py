import pathlib
import json
import numpy as np
import matplotlib.pyplot as plt

filename = "mpcorb_extended.json"

# Parameters to save
params = ["a", "e", "i", "Peri", "Node"]

if not pathlib.Path("mpcorb_extended.npy").exists():
    with open(filename, "rb") as fh:
        mpc = json.load(fh)
    bodies = np.empty((6, len(mpc)), dtype=np.float64)
    for ind in range(len(mpc)):
        for k_ind, key in enumerate(params):
            bodies[k_ind, ind] = mpc[ind][key]
    np.save("mpcorb_extended.npy", bodies)
else:
    bodies = np.load("mpcorb_extended.npy")

bodies[0, :] = 1.0 / bodies[0, :]
params[0] = "1/a"

# All unique pairings
pairs = [
    (0, 1),
    (0, 2),
    (0, 3),
    (0, 4),
    (1, 2),
    (1, 3),
    (1, 4),
    (2, 3),
    (2, 4),
]

nrows, ncols = 3, 3
fig, axes = plt.subplots(nrows, ncols, figsize=(12, 16), layout="tight")
axes = axes.flatten()

for ax, (xpar, ypar) in zip(axes, pairs):
    ax.scatter(
        bodies[xpar, :],
        bodies[ypar, :],
        s=1,
        alpha=0.3,
        rasterized=True,
    )

    ax.set_xlabel(params[xpar])
    ax.set_ylabel(params[ypar])

fig.suptitle("MPCORB Orbital Element Pairwise Scatter Plots", fontsize=16)
plt.show()

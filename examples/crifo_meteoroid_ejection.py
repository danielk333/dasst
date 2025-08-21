
def t_vs_z_plot(T, z, rh):
    valid = np.isfinite(T)
    fig = plt.figure()
    plt.scatter(z[valid], T[valid], s=20, alpha=0.8)
    plt.xlabel(r"Solar zenith angle $z$ (deg)", fontsize=18)
    plt.ylabel(r"Gas temperature $T$ (K)", fontsize=18)
    plt.title(rf"$T$ vs $z$ ($r_h$ = {rh})", fontsize=20)
    return fig


def vt_vs_z_plot(terminal_velocities, z, a_d, rh):
    valid = np.isfinite(terminal_velocities)
    fig = plt.figure()
    plt.scatter(z[valid], terminal_velocities[valid], s=20, alpha=0.8)
    plt.xlabel(r"Solar zenith angle $z$ (deg)", fontsize=18)
    plt.ylabel(r"Terminal velocity $V_\infty$ (m/s)", fontsize=18)
    plt.title(rf"$V_\infty$ vs $z$ (for dust size = {a_d} and $r_h$ = {rh})", fontsize=20)
    return fig


def vt_hist_plot(terminal_velocities, z, a_d, rh):
    valid = np.isfinite(terminal_velocities)
    fig = plt.figure()
    plt.hist(terminal_velocities[valid], bins=int(np.sqrt(len(terminal_velocities))))
    plt.xlabel(r"Terminal velocity $V_\infty$ (m/s)", fontsize=18)
    plt.title(rf"$V_\infty$ distribtuion (for dust size = {a_d} and $r_h$ = {rh})", fontsize=20)
    return fig
def terminal_velocity_histogram(terminal_velocity, comet_name):
    fig = plt.figure()
    plt.hist(terminal_velocity, bins="fd", color="white", edgecolor="black")
    plt.xlabel("Terminal velocity (m/s)")
    plt.ylabel("Number of particles")
    plt.title(f"Terminal velocity histogram of {comet_name}")
    return fig

import argparse
from astropy.time import Time
from pathlib import Path
import dasst

parser = argparse.ArgumentParser()
parser.add_argument("kernel_path", type=Path, help="Path to the spice kernel")
args = parser.parse_args()

epoch = Time("2024-01-01T00:00:00", format="isot", scale="utc")
states = dasst.frames.get_solarsystem_body_states(["Sun", "Earth"], epoch, args.kernel_path)

print(states)

state_hcrs = dasst.frames.convert(
    epoch,
    states["Earth"],
    in_frame="ICRS",
    out_frame="BarycentricTrueEcliptic",
)

print(f"{state_hcrs}")

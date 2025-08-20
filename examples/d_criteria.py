"""
D criterion example
=========================

Docstring for this example
"""
from numpy import radians as rad
import dasst.similarity.d_criteria as dlib
import pyorb

G_au = pyorb.get_G(length="AU", mass="kg", time="s")

kw = dict(
    M0=pyorb.M_sol,
    G=G_au,
    direct_update=True,
    auto_update=True,
    degrees=False,
)

orb_a = pyorb.Orbit(
    a=1.11, e=0.6, i=rad(68), omega=rad(11), Omega=rad(5), anom=rad(10.01), **kw
)
print("Orbit A:")
print(orb_a)

orb_b = pyorb.Orbit(
    a=1.1, e=0.5, i=rad(67), omega=rad(12), Omega=rad(5), anom=rad(10), **kw
)
print("Orbit b:")
print(orb_b)

print("D_SH(A,B)")
print(dlib.D_SH(orb_a, orb_b))

print("D_V(A,B)")
print(dlib.D_V(orb_a, orb_b))

print("D_SH(A,A)")
print(dlib.D_SH(orb_a, orb_a))

print("D_V(A,A)")
print(dlib.D_V(orb_a, orb_a))

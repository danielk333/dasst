import mpcorbfile
import configparser
from tqdm import tqdm
import numpy as np
from scipy.optimize import minimize
from astropy.constants import GM_sun, au
from astroquery.jplhorizons import Horizons
from scipy.optimize import minimize
import sys


def SouthworthHawkins_criterion(q1,q2,e1,e2,i1,i2,O1,O2,o1,o2):

    half_piece_1 = 2.*(np.sin(.5*i1)*np.cos(.5*i2)-np.cos(.5*i1)*np.sin(.5*i2))
    half_piece_1 = half_piece_1**2

    two_sim_O = 2.*(np.sin(.5*O1)*np.cos(.5*O2)-np.cos(.5*O1)*np.sin(.5*O2))
    quarter_piece_1 = np.sin(i1)*np.sin(i2)*two_sim_O**2

    vp1 = O1 + o1
    vp2 = O1 + o2
    two_sim_vp = 2.*(np.sin(.5*vp1)*np.cos(.5*vp2)-np.cos(.5*vp1)*np.sin(.5*vp2))
    quarter_piece_2 = (((e1+e2)*.5)*two_sim_vp)**2

    half_piece_2 = quarter_piece_1 + quarter_piece_2

    piece = half_piece_1 + half_piece_2
    D2 = ((q1 - q2)/(au.value*1.e-3))**2 + (e1 - e2)**2 + piece

    D = np.sqrt(D2)

    return D


def Nesvorny_criterion(a2,a1,e2,e1,i2,i1,O2,O1,vp2,vp1):
    a1 = a1*au.value
    a2 = a2*au.value
    # O1 = np.degrees(O1)
    # O2 = np.degrees(O2)
    # vp1 = np.degrees(vp1)
    # vp2 = np.degrees(vp2)

    ka = 5./4.
    ke = 2.
    ki = 2.
    kO = 1.e-6
    kvp = 1.e-6

    DA2 = ((a1-a2)/a1)**2
    De2 = (e1-e2)**2
    Di2 = (np.sin(i1)-np.sin(i2))**2

    DO = np.arccos(np.cos(O1)*np.cos(O2)+np.sin(O1)*np.sin(O2))
    DO2 = np.degrees(DO)**2

    Dvp = np.arccos(np.cos(vp1)*np.cos(vp2)+np.sin(vp1)*np.sin(vp2))
    Dvp2 = np.degrees(Dvp)**2



    n = np.sqrt(GM_sun.value/a1**3)
    D2  = ka*DA2 + ke*De2 + ki*Di2 + kO*DO2 + kvp*Dvp2
    D = np.sqrt(D2)*n*a1
    return D

def Drummond_criterion(q1,q2,e1,e2,i1,i2,O1,O2,o1,o2):

    def comp_beta(i,omega):
        return np.arcsin(np.sin(i)*np.sin(omega))

    def comp_lambda(i,Omega,omega):
        lamb = Omega + np.arctan(np.cos(i)*np.tan(omega))
        if np.cos(omega) < 0:
            lamb = lamb + np.pi

        return lamb

    beta_1 = comp_beta(i1,o1)
    beta_2 = comp_beta(i2,o2)

    lamb_1 = comp_lambda(i1,O1,o1)
    lamb_2 = comp_lambda(i2,O2,o2)

    I = np.arccos(np.cos(i1)*np.cos(i2) \
        + np.sin(i1)*np.sin(i2)*np.cos(O1-O2))

    cos_lamb_12 = np.cos(lamb_1)*np.cos(lamb_2) + np.sin(lamb_1)*np.sin(lamb_2)

    THETA = np.arccos(
        np.sin(beta_1)*np.sin(beta_2) +
        np.cos(beta_1)*np.cos(beta_2)*cos_lamb_12
    )


    D2 = ((e1 - e2)/(e1 + e2))**2 + ((q1 - q2)/(q1 + q2))**2 \
        + (I/np.pi)**2 + (((e1 + e2)/2.)*(THETA/np.pi))**2

    D = np.sqrt(D2)

    return D


def func_Drummond(x):
    POO = OE_2_position(a, e, i, Omega, omega, f)
    dist = np.sqrt((POO[0] - EP[0]) ** 2 + (POO[1] - EP[1]) ** 2 + (POO[2] - EP[2]) ** 2)
    d = Drummond_criterion(q1,q2,e1,e2,i1,i2,O1,O2,o1,o2)
    return dist





# READ FILE
#mpc = mpcorbfile.mpcorb_file('input/MPCORB-c.DAT')
#mpc = mpcorbfile.mpcorb_file('input/MPCORB.DAT')
mpc = mpcorbfile.mpcorb_file('input/MPCORB-11-MAY-2025.DAT')


N = len(mpc.bodies)


data = np.zeros((4,N))
id_ast = ['' for _ in range(N)]



config = configparser.ConfigParser()
config.read("input/fireball_sweden.ini")
#config.read("input/kappa_cygnid.ini")

a2 = config["orbit"].getfloat("semi-major_axis")
e2 = config["orbit"].getfloat("eccentricity")
q2 = a2*(1.-e2)
i2 = config["orbit"].getfloat("inclination")
i2 = np.radians(i2)%(2.*np.pi)
O2 = config["orbit"].getfloat("longitude_of_the_ascending_node")
O2 = np.radians(O2)%(2.*np.pi)
vp2 = config["orbit"].getfloat("longitude_of_periapsis")
vp2 = np.radians(vp2)%(2.*np.pi)
o2 = (vp2-O2)%(2.*np.pi)

da2 = config["error"].getfloat("semi-major_axis")
de2 = config["error"].getfloat("eccentricity")
di2 = config["error"].getfloat("inclination")
di2 = np.radians(di2)%(2.*np.pi)
dO2 = config["error"].getfloat("longitude_of_the_ascending_node")
dO2 = np.radians(dO2)%(2.*np.pi)
dvp2 = config["error"].getfloat("longitude_of_periapsis")
dvp2 = np.radians(dvp2)%(2.*np.pi)

for i in tqdm(range(N)):
    a1 = mpc.bodies[i]['a']
    e1 = mpc.bodies[i]['e']
    q1 = a1*(1.-e1)
    i1 = np.radians(mpc.bodies[i]['i'])%(2.*np.pi)
    O1 = np.radians(mpc.bodies[i]['Node'])%(2.*np.pi)
    o1 = np.radians(mpc.bodies[i]['Peri'])%(2.*np.pi)
    vp1 = (O1 + o1)%(2.*np.pi)

    if i < 793066:
        id_ast[i] = mpc.bodies[i]['packed_designation']
    else:
        id_ast[i] = mpc.bodies[i]['designation']

    data[0, i] = i

    data[1,i] = Drummond_criterion(q1,q2,e1,e2,i1,i2,O1,O2,o1,o2)
    data[2,i] = Nesvorny_criterion(a1,a2,e1,e2,i1,i2,O1,O2,vp1,vp2)
    data[3,i] = SouthworthHawkins_criterion(q1,q2,e1,e2,i1,i2,O1,O2,o1,o2)








sort_D = np.argsort(data[1, :])
sort_N = np.argsort(data[2, :])
sort_SH = np.argsort(data[3, :])
Dru = data[:, sort_D]
Ner = data[:, sort_N]
SH = data[:, sort_SH]

redo_N = 500

rd_Dru = np.zeros((4,redo_N))
rd_Ner = np.zeros((4,redo_N))
rd_SH = np.zeros((4,redo_N))



bounds = [
    (a2 - da2, a2 + da2),
    (e2 - de2, e2 + de2),
    (i2 - di2, i2 + di2),
    (O2 - dO2, O2 + dO2),
    (vp2 - dvp2, vp2 + dvp2)
]

x0 = [a2, e2, i2, O2, vp2]


jd_date = 2460003.2604167
for i in tqdm(range(redo_N)):
    rd_Dru[0,i] = Dru[0,i]
    rd_Dru[1,i] = Dru[1,i]

    rd_Ner[0,i] = Ner[0,i]
    rd_Ner[1,i] = Ner[2,i]

    rd_SH[0,i] = SH[0,i]
    rd_SH[1,i] = SH[3,i]

    ########################################
    obj = Horizons(id=f'{id_ast[int(rd_Dru[0,i])]}', id_type='smallbody', location='@sun', epochs=jd_date)
    try:
        elements = obj.elements()
    except ValueError:
        obj = Horizons(id=f'{int(rd_Dru[0,i]+1)}', id_type='smallbody', location='@sun', epochs=jd_date)
        elements = obj.elements()

    a1 = elements["a"].value[0]
    e1 = elements["e"].value[0]
    q1 = a1*(1.-e1)
    i1 = np.radians(elements["incl"].value[0])%(2.*np.pi)
    O1 = np.radians(elements["Omega"].value[0])%(2.*np.pi)
    o1 = np.radians(elements["w"].value[0])%(2.*np.pi)
    vp1 = (O1 + o1)%(2.*np.pi)

    rd_Dru[2,i] = Drummond_criterion(q1,q2,e1,e2,i1,i2,O1,O2,o1,o2)

    def objectiveD(x, q1=q1, e1=e1, i1=i1, O1=O1, o1=o1):
        a2, e2, i2, O2, vp2 = x

        q2 = a2*(1.-e2)
        o2 = vp2 - O2
        d = Drummond_criterion(q1,q2,e1,e2,i1,i2,O1,O2,o1,o2)
        return d

    resultd = minimize(objectiveD, x0, bounds=bounds, method='L-BFGS-B')
    rd_Dru[3,i] = resultd.fun
    ########################################
    obj = Horizons(id=f'{id_ast[int(rd_Ner[0,i])]}', id_type='smallbody', location='@sun', epochs=jd_date)
    try:
        elements = obj.elements()
    except ValueError:
        obj = Horizons(id=f'{int(rd_Ner[0,i]+1)}', id_type='smallbody', location='@sun', epochs=jd_date)
        elements = obj.elements()

    a1 = elements["a"].value[0]
    e1 = elements["e"].value[0]
    q1 = a1*(1.-e1)
    i1 = np.radians(elements["incl"].value[0])%(2.*np.pi)
    O1 = np.radians(elements["Omega"].value[0])%(2.*np.pi)
    o1 = np.radians(elements["w"].value[0])%(2.*np.pi)
    vp1 = (O1 + o1)%(2.*np.pi)

    rd_Ner[2,i] = Nesvorny_criterion(a1,a2,e1,e2,i1,i2,O1,O2,vp1,vp2)

    def objectiveN(x, a1=a1, e1=e1, i1=i1, O1=O1, vp1=vp1):
        a2, e2, i2, O2, vp2 = x

        d = Nesvorny_criterion(a1,a2,e1,e2,i1,i2,O1,O2,vp1,vp2)
        return d

    resultn = minimize(objectiveN, x0, bounds=bounds, method='L-BFGS-B')
    rd_Ner[3,i] = resultn.fun
    ########################################
    obj = Horizons(id=f'{id_ast[int(rd_SH[0,i])]}', id_type='smallbody', location='@sun', epochs=jd_date)
    try:
        elements = obj.elements()
    except ValueError:
        obj = Horizons(id=f'{int(rd_SH[0,i]+1)}', id_type='smallbody', location='@sun', epochs=jd_date)
        elements = obj.elements()

    a1 = elements["a"].value[0]
    e1 = elements["e"].value[0]
    q1 = a1*(1.-e1)
    i1 = np.radians(elements["incl"].value[0])%(2.*np.pi)
    O1 = np.radians(elements["Omega"].value[0])%(2.*np.pi)
    o1 = np.radians(elements["w"].value[0])%(2.*np.pi)
    vp1 = (O1 + o1)%(2.*np.pi)

    rd_SH[2,i] = SouthworthHawkins_criterion(q1,q2,e1,e2,i1,i2,O1,O2,o1,o2)

    def objectiveSH(x, q1=q1, e1=e1, i1=i1, O1=O1, o1=o1):
        a2, e2, i2, O2, vp2 = x

        q2 = a2*(1.-e2)
        o2 = vp2 - O2
        d = SouthworthHawkins_criterion(q1,q2,e1,e2,i1,i2,O1,O2,o1,o2)
        return d

    resultsh = minimize(objectiveSH, x0, bounds=bounds, method='L-BFGS-B')
    rd_SH[3,i] = resultsh.fun


sort_D = np.argsort(rd_Dru[2, :])
sort_N = np.argsort(rd_Ner[2, :])
sort_SH = np.argsort(rd_SH[2, :])

Dru_N = rd_Dru[:, sort_D]
Ner_N = rd_Ner[:, sort_N]
SH_N = rd_SH[:, sort_SH]


sort_D = np.argsort(rd_Dru[3, :])
sort_N = np.argsort(rd_Ner[3, :])
sort_SH = np.argsort(rd_SH[3, :])
Dru_NN = rd_Dru[:, sort_D]
Ner_NN = rd_Ner[:, sort_N]
SH_NN = rd_SH[:, sort_SH]


list_T = 50

file_name = f"compare.txt"









with open(file_name,'w') as f:
    f.write('--------   FILE DATE -------------\n')
    f.write('--------   Southworth Hawkins -------------\n')


for i in range(list_T):
    with open(file_name,'a') as f:
        f.write(f'{mpc.bodies[int(SH[0,i])]['Name']}   {SH[3,i]}  \n')

with open(file_name,'a') as f:
    f.write('--------  Drummond -------------------\n')

for i in range(list_T):
    with open(file_name,'a') as f:
        f.write(f'{mpc.bodies[int(Dru[0,i])]['Name']}   {Dru[1,i]}  \n')



with open(file_name,'a') as f:
    f.write('--------  Nersvony -------------------\n')
for i in range(list_T):
    with open(file_name,'a') as f:
        f.write(f'{mpc.bodies[int(Ner[0,i])]['Name']}   {Ner[2,i]}   \n')




with open(file_name,'a') as f:
    f.write('--------   Fall Date -------------\n')
    f.write('--------   Southworth Hawkins -------------\n')


for i in range(list_T):
    with open(file_name,'a') as f:
        f.write(f'{mpc.bodies[int(SH_N[0,i])]['Name']}   {SH_N[2,i]}   \n')

with open(file_name,'a') as f:
    f.write('--------  Drummond -------------------\n')

for i in range(list_T):
    with open(file_name,'a') as f:
        f.write(f'{mpc.bodies[int(Dru_N[0,i])]['Name']}   {Dru_N[2,i]}   \n')



with open(file_name,'a') as f:
    f.write('--------  Nersvony -------------------\n')
for i in range(list_T):
    with open(file_name,'a') as f:
        f.write(f'{mpc.bodies[int(Ner_N[0,i])]['Name']}   {Ner_N[2,i]}  \n')


with open(file_name,'a') as f:
    f.write('--------   ERROR -------------\n')
    f.write('--------   Southworth Hawkins -------------\n')


for i in range(list_T):
    with open(file_name,'a') as f:
        f.write(f'{mpc.bodies[int(SH_NN[0,i])]['Name']}  {SH_NN[3,i]}  \n')

with open(file_name,'a') as f:
    f.write('--------  Drummond -------------------\n')

for i in range(list_T):
    with open(file_name,'a') as f:
        f.write(f'{mpc.bodies[int(Dru_NN[0,i])]['Name']}   {Dru_NN[3,i]}   \n')



with open(file_name,'a') as f:
    f.write('--------  Nersvony -------------------\n')
for i in range(list_T):
    with open(file_name,'a') as f:
        f.write(f'{mpc.bodies[int(Ner_NN[0,i])]['Name']}   {Ner_NN[3,i]}   \n')


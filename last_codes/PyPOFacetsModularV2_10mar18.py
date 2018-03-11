# PyPOFacetsModular - Monostatic version
# Inspired by the software POFacets noGUI v2.2 in MATLAB - http://faculty.nps.edu/jenn/


import sys
import math
import numpy as np

from datetime import datetime
from timeit import default_timer as timer
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


# ***function 1***
def calculate_wavelength(freq):
    c = 3e8
    # print("speed of light: ", c)
    waveL = c / freq
    return waveL


# ***function 2***
def calculate_incident_wave_polarization(ipol):
    if ipol == 0:
        Et = 1 + 0j
        Ep = 0 + 0j
    elif ipol == 1:
        Et = 0 + 0j
        Ep = 1 + 0j
    else:
        print("error")
    return (Et, Ep)


# ***function 3***
def read_model_coordinates(name):
    fname = name + "/coordinates.m"
    print "Path and file model coordinates: ", fname
    coordinates = np.around(np.loadtxt(fname)).astype(int)
    print "Model points coordinates: ", coordinates
    return np.transpose(coordinates)


# ***function 4***
def read_facets_model(name):
    fname2 = name + "/facets.m"
    print "Path and file facets model: ", fname2
    facets = np.around(np.loadtxt(fname2)).astype(int)
    return facets


# ***function 5***
def generate_transpose_matrix(facets):
    nfcv, node1, node2, node3, ilum, Rs = np.transpose(facets)
    return nfcv, node1, node2, node3, ilum, Rs


# ***function 6***
def generate_coordinates_points(xpts, ypts, zpts):
    r = list(zip(xpts, ypts, zpts))
    return r


# ***function 7***
def plot_3d_graph_model(node1, node2, node3, r):
    fig1 = plt.figure()
    ax = Axes3D(fig1)
    for point in zip(node1, node2, node3):
        Xa = [r[(point[0]) - 1][0], r[(point[1]) - 1][0], r[(point[2]) - 1][0], r[(point[0]) - 1][0]]
        Ya = [r[point[0] - 1][1], r[point[1] - 1][1], r[point[2] - 1][1], r[point[0] - 1][1]]
        Za = [r[point[0] - 1][2], r[point[1] - 1][2], r[point[2] - 1][2], r[point[0] - 1][2]]
        # ax.plot_wireframe(Xa, Ya, Za) # one color
        ax.plot(Xa, Ya, Za)
        ax.set_xlabel("X Axis")
    ax.set_title("3D Model: " + input_model)
    plt.show()
    plt.close()


# ***function 8***
def calculate_refs_geometry_model(pstart, pstop, delp, tstart, tstop, delt, rad):
    if delp == 0:
        delp = 1
    if pstart == pstop:
        phr0 = pstart*rad

    if delt == 0:
        delt = 1
    if tstart == tstop:
        thr0 = tstart*rad

    it = math.floor((tstop-tstart)/delt)+1
    print("Number of horizontal rotations in the simulation: ", it)
    ip = math.floor((pstop-pstart)/delp)+1
    print("Number of vertical rotations in the simulation: ", ip)

    return it, ip, delp, delt


# ***function 9***
def calculate_edges_and_normal_triangles(node1, node2, node3, r):
    areai = []
    beta = []
    alpha = []
    for point in zip(node1, node2, node3):
        A0 = ((r[point[1] - 1][0]) - (r[point[0] - 1][0]))
        A1 = ((r[point[1] - 1][1]) - (r[point[0] - 1][1]))
        A2 = ((r[point[1] - 1][2]) - (r[point[0] - 1][2]))
        A = [A0, A1, A2]
        B0 = ((r[point[2] - 1][0]) - (r[point[1] - 1][0]))
        B1 = ((r[point[2] - 1][1]) - (r[point[1] - 1][1]))
        B2 = ((r[point[2] - 1][2]) - (r[point[1] - 1][2]))
        B = [B0, B1, B2]
        C0 = ((r[point[0] - 1][0]) - (r[point[2] - 1][0]))
        C1 = ((r[point[0] - 1][1]) - (r[point[2] - 1][1]))
        C2 = ((r[point[0] - 1][2]) - (r[point[2] - 1][2]))
        C = [C0, C1, C2]

        N = -(np.cross(B,A))
        # print("Refs. normal (bidim.): ", point, N)

        # OctT 184 - Edge lengths for triangle "i"
        d = [np.linalg.norm(A), np.linalg.norm(B), np.linalg.norm(C)]
        ss = 0.5*sum(d)
        areai.append(math.sqrt(ss*(ss-np.linalg.norm(A))*(ss-np.linalg.norm(B))*(ss-np.linalg.norm(C))))
        Nn = np.linalg.norm(N)
        # unit normals
        N = N/Nn
        # 0 < beta < 180
        beta.append(math.acos(N[2]))
        # -180 < phi < 180
        alpha.append(math.atan2(N[1],N[0]))
    return areai, beta, alpha


# ***function 10***
def calculate_global_angles_and_directions(i1, i2, ip, it, pstart, delp, rad, tstart, delt, phi, theta, D0):
    phi.append(pstart + i1 * delp)
    phr = phi[i2] * rad
    # Global angles and direction cosines
    theta.append(tstart + i2 * delt)
    thr = theta[i2] * rad
    st = math.sin(thr)
    ct = math.cos(thr)
    cp = math.cos(phr)
    sp = math.sin(phr)
    u = st * cp
    v = st * sp
    w = ct
    D0.append([u, v, w])
    U = u
    V = v
    W = w
    uu = ct * cp
    vv = ct * sp
    ww = -st
    return u, v, w, uu, vv, ww, sp, cp, D0


# ***function 11***
def calculate_spherical_coordinate_system_radial_unit_vector(fileR, i2, u, v, w, R):
    fileR.write(str(i2))
    fileR.write(" ")
    fileR.write(str([u, v, w]))
    fileR.write("\n")
    R.append([u, v, w])
    return R


# ***function 12***
def calculate_incident_field_in_global_cartesian_coordinates(fileE0, i2, uu, vv, ww, Et, Ep, sp, cp, e0):
    fileE0.write(str(i2))
    fileE0.write(" ")
    fileE0.write(str([(uu * Et - sp * Ep), (vv * Et + cp * Ep), (ww * Et)]))
    fileE0.write("\n")
    e0.append([(uu * Et - sp * Ep), (vv * Et + cp * Ep), (ww * Et)])
    return e0


# ***function 13***
def calculate_ilum_faces(m, D0, i1, alpha, beta):
    ca = math.cos(alpha[m])
    sa = math.sin(alpha[m])
    cb = math.cos(beta[m])
    sb = math.sin(beta[m])
    T1 = []
    T1 = [[ca, sa, 0], [-sa, ca, 0], [0, 0, 1]]
    # print(m, T1)
    T2 = []
    T2 = [[cb, 0, -sb], [0, 1, 0], [sb, 0, cb]]
    Dzero = np.array(D0[i1])
    D1 = T1 * Dzero.transpose()
    D2 = T2 * D1

def main_all_in_one(Ep, Et, corr, delp, delstd, delt, freq, ip, ipol, it, pstart, pstop, rad, tstart, tstop):
    phi = []
    theta = []
    D0 = []
    R = []
    e0 = []
    filename_R = "R_PyPOFacetsModular_" + sys.argv[1] + "_" + sys.argv[2] + "_" + now + ".dat"
    print filename_R
    filename_E0 = "E0_PyPOFacetsModular_" + sys.argv[1] + "_" + sys.argv[2] + "_" + now + ".dat"
    print filename_E0
    fileR = open(filename_R, 'w')
    fileE0 = open(filename_E0, 'w')
    fileR.write(now)
    fileR.write("\n")
    fileR.write(sys.argv[0])
    fileR.write("\n")
    fileR.write(sys.argv[1])
    fileR.write("\n")
    fileR.write(sys.argv[2])
    fileR.write("\n")
    fileR.write(str(freq))
    fileR.write("\n")
    fileR.write(str(corr))
    fileR.write("\n")
    fileR.write(str(delstd))
    fileR.write("\n")
    fileR.write(str(ipol))
    fileR.write("\n")
    fileR.write(str(pstart))
    fileR.write("\n")
    fileR.write(str(pstop))
    fileR.write("\n")
    fileR.write(str(delp))
    fileR.write("\n")
    fileR.write(str(tstart))
    fileR.write("\n")
    fileR.write(str(tstop))
    fileR.write("\n")
    fileR.write(str(delt))
    fileR.write("\n")
    fileE0.write(now)
    fileE0.write("\n")
    fileE0.write(sys.argv[0])
    fileE0.write("\n")
    fileE0.write(sys.argv[1])
    fileE0.write("\n")
    fileE0.write(sys.argv[2])
    fileE0.write("\n")
    fileE0.write(str(freq))
    fileE0.write("\n")
    fileE0.write(str(corr))
    fileE0.write("\n")
    fileE0.write(str(delstd))
    fileE0.write("\n")
    fileE0.write(str(ipol))
    fileE0.write("\n")
    fileE0.write(str(pstart))
    fileE0.write("\n")
    fileE0.write(str(pstop))
    fileE0.write("\n")
    fileE0.write(str(delp))
    fileE0.write("\n")
    fileE0.write(str(tstart))
    fileE0.write("\n")
    fileE0.write(str(tstop))
    fileE0.write("\n")
    fileE0.write(str(delt))
    fileE0.write("\n")
    for i1 in range(0, int(ip)):
        for i2 in range(0, int(it)):
            # ***function 10***
            u, v, w, uu, vv, ww, sp, cp, D0 = calculate_global_angles_and_directions(i1, i2, ip, it, pstart, delp, rad,
                                                                                     tstart, delt, phi, theta, D0)

            # ***function 11***
            R = calculate_spherical_coordinate_system_radial_unit_vector(fileR, i2, u, v, w, R)

            # ***function 12***
            e0 = calculate_incident_field_in_global_cartesian_coordinates(fileE0, i2, uu, vv, ww, Et, Ep, sp, cp, e0)

            # Begin loop over triangles
            sumt = 0
            sump = 0
            sumdt = 0
            sumdp = 0
            # for m in range(ntria):
            # OctT 236
            # Test to see if front face is illuminated: FUT
            # Local direction cosines
            # ***function 13***
            # calculate_ilum_faces(m, D0, i1, alpha, beta)
    fileR.close()
    fileE0.close()


# function main
def main(name):
    # Read and print input data file: pattern -> input_data_file_xxx.dat
    input_data_file = sys.argv[2]
    print "\nInput data file:", input_data_file
    # Open input data file and gather parameters
    params = open(input_data_file, 'r')
    # 1: radar frequency
    params.readline()
    freq = int(params.readline())
    print "\nThe radar frequency in Hz:", freq, "Hz"

    # ***function 1***
    waveL = calculate_wavelength(freq)
    print "\nWavelength in meters:", waveL, "m"

    # 2: correlation distance in meters
    params.readline()
    corr = int(params.readline())
    print "\nCorrelation distance in meters:", corr, "m"
    corel = corr / waveL
    # 3: standard deviation in meters
    params.readline()
    delstd = int(params.readline())
    print "\nStandard deviation in meters:", delstd, "m"
    delsq = delstd ** 2
    bk = 2 * math.pi / waveL
    cfact1 = math.exp(-4 * bk ** 2 * delsq)
    cfact2 = 4 * math.pi * (bk * corel) ** delsq
    rad = math.pi / 180
    Lt = 0.05
    Nt = 5
    # 4: incident wave polarization
    params.readline()
    ipol = int(params.readline())
    print "\nIncident wave polarization:", ipol

    # ***function 2***
    Et, Ep = calculate_incident_wave_polarization(ipol)
    Co = 1

    # Processing 3D model
    print "\nProcessing 3D model..."
    # ***function 3***
    xpts, ypts, zpts = read_model_coordinates(name)
    print "Coordinates x (model points): ", xpts
    print "Coordinates y (model points): ", ypts
    print "Coordinates z (model points): ", zpts
    nverts = len(xpts)
    print "Number of model vertices: ", nverts

    # ***function 4***
    facets = read_facets_model(name)
    print("Model faces information: ", facets)

    # ***function 5***
    nfcv, node1, node2, node3, ilum, Rs = generate_transpose_matrix(facets)
    print("Numbering of the model faces in the file: ", nfcv)
    print("First component of each face: ", node1)
    print("Second component of each face: ", node2)
    print("Third component of each face: ", node3)
    ntria = len(node3)
    print("Number of model faces: ", ntria)

    # ***function 6***
    r = generate_coordinates_points(xpts, ypts, zpts)

    # start plot
    # ***function 7***
    # plot_3d_graph_model(node1, node2, node3, r)

    # Oct 138 - Pattern Loop
    # 5: start phi angle in degrees
    params.readline()
    pstart = int(params.readline())
    print "\nStart phi angle in degrees:", pstart

    # 6: stop phi angle in degrees
    params.readline()
    pstop = int(params.readline())
    print "\nStop phi angle in degrees:", pstop

    # 7: phi increment (step) in degrees
    params.readline()
    delp = int(params.readline())
    print "\nPhi increment (step) in degrees:", delp

    # 8: start theta angle in degrees
    params.readline()
    tstart = int(params.readline())
    print "\nStart theta angle in degrees:", tstart

    # 9: stop theta angle in degrees
    params.readline()
    tstop = int(params.readline())
    print "\nStop theta angle in degrees:", tstop

    # 10: theta increment (step) in degrees
    params.readline()
    delt = int(params.readline())
    print "\nTheta increment (step) in degrees:", delt

    params.close()

    # ***function 8***
    it, ip, delp, delt = calculate_refs_geometry_model(pstart, pstop, delp, tstart, tstop, delt, rad)

    print("last step")
    # OctT 168 - Get edge vectors and normal from edge cross products

    # ***function 9***
    areai, beta, alpha = calculate_edges_and_normal_triangles(node1, node2, node3, r)

    main_all_in_one(Ep, Et, corr, delp, delstd, delt, freq, ip, ipol, it, pstart, pstop, rad, tstart, tstop)

    end = timer()
    print end - start, "seg"


if __name__ == '__main__':
    start = timer()
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    print now
    print "PyPOFacets - v0.1"
    print "================="
    print "\nScript:", sys.argv[0]
    # Read and print 3D model package
    input_model = sys.argv[1]
    print "\n3D Model:", input_model
    name = input_model
    main(name)
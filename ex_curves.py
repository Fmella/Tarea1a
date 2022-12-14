# coding=utf-8
"""
Daniel Calderon
Universidad de Chile, CC3501, 2018-2
Hermite and Bezier curves using python, numpy and matplotlib
"""

import numpy as np
import matplotlib.pyplot as mpl
from mpl_toolkits.mplot3d import Axes3D


def generateT(t):
    return np.array([[1, t, t ** 2, t ** 3]]).T


def hermiteMatrix(P1, P2, T1, T2):
    # Generate a matrix concatenating the columns
    G = np.concatenate((P1, P2, T1, T2), axis=1)

    # Hermite base matrix is a constant
    Mh = np.array([[1, 0, -3, 2], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])

    return np.matmul(G, Mh)


def bezierMatrix(P0, P1, P2, P3):
    # Generate a matrix concatenating the columns
    G = np.concatenate((P0, P1, P2, P3), axis=1)

    # Bezier base matrix is a constant
    Mb = np.array([[1, -3, 3, -1], [0, 3, -6, 3], [0, 0, 3, -3], [0, 0, 0, 1]])

    return np.matmul(G, Mb)


def plotCurve(ax, curve, label, color=(0, 0, 1)):
    xs = curve[:, 0]
    ys = curve[:, 1]
    zs = curve[:, 2]

    ax.plot(xs, ys, zs, label=label, color=color)


# M is the cubic curve matrix, N is the number of samples between 0 and 1
def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)

    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)

    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
    return curve


if __name__ == "__main__":
    """
    Example for Hermite curve
    """

    P1 = np.array([[1, 4, 0]]).T
    P2 = np.array([[1, 3, 0]]).T
    T1 = np.array([[1, 0, 0]]).T
    T2 = np.array([[1, 0, 0]]).T

    GMh = hermiteMatrix(P1, P2, T1, T2)

    # Number of samples to plot
    N = 4

    hermiteCurve = evalCurve(GMh, N)

    # Setting up the matplotlib display for 3D
    fig = mpl.figure()
    ax = fig.gca(projection='3d')

    plotCurve(ax, hermiteCurve, "Hermite curve", (1,0,0))

    """
    Example for Bezier curve
    """

    R0 = np.array([[0, 0, 1]]).T
    R1 = np.array([[1, 0, 0]]).T
    R2 = np.array([[2, 0, 1]]).T
    R3 = np.array([[3, 0, 0]]).T

    GMb0 = bezierMatrix(R0, R1, R2, R3)
    bezierCurve0 = evalCurve(GMb0, N)

    S0 = np.array([[3, 0, 0]]).T
    S1 = np.array([[2, 0, -1]]).T
    S2 = np.array([[1, 0, 0]]).T
    S3 = np.array([[0, 0, -1]]).T

    GMb1 = bezierMatrix(S0, S1, S2, S3)
    bezierCurve1 = evalCurve(GMb1, N)

#    plotCurve(ax, bezierCurve0, "Bezier curve 0")
#    plotCurve(ax, bezierCurve1, "Bezier curve 1")

    # Adding a visualization of the control points
#    controlPoints0 = np.concatenate((R0, R1, R2, R3), axis=1)
#    ax.scatter(controlPoints0[0, :], controlPoints0[1, :], controlPoints0[2, :], color=(1, 0, 0))

#    controlPoints1 = np.concatenate((S0, S1, S2, S3), axis=1)
#    ax.scatter(controlPoints1[0, :], controlPoints1[1, :], controlPoints1[2, :], color=(1, 0, 0))

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.legend()
    mpl.show()

import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

angle_value = 0.399

x = np.array(
    [0, 0, -1 / 4, -1 / 4, -1 / 4, 0, 1 / 4, 1 / 4, 1 / 4, 1 / 2, 1 / 2, 1 / 2, 1 / 2, 1 / 4, 0, -1 / 4, -1 / 2,
     -1 / 2, -1 / 2, -1 / 2, -1 / 2, -1 / 4, 0, 1 / 4, 1 / 2, 1 / 2, 1 / 4, 0, 0,
     1 / 4, 1 / 2, 3 / 4, 1, 1, 1, 1, 1, 3 / 4, 3 / 4, 3 / 4, 3 / 4, 1 / 2, 1 / 4, 0, -1 / 4, -1 / 4, -1 / 4, -1 / 4]) \
    * angle_value
y = np.array(
    [0, -1 / 4, -1 / 4, 0, 1 / 4, 1 / 4, 1 / 4, 0, -1 / 4, -1 / 4, 0, 1 / 4, 1 / 2, 1 / 2, 1 / 2, 1 / 2, 1 / 2, 1 / 4,
     0, -1 / 4, -1 / 2,
     -1 / 2, -1 / 2, -1 / 2, -1 / 2, -3 / 4, -3 / 4, -3 / 4, -1, -1, -1, -1, -1, -3 / 4, -1 / 2,
     -1 / 4, 0, 0, -1 / 4, -1 / 2, -3 / 4, -5 / 4, -5 / 4, -5 / 4, -5 / 4, -1, -3 / 4, -1 / 2]) * angle_value

V_over_H = np.array([7.60E+00,
                     3.30E+00,
                     3.39E+00,
                     7.90E+00,
                     2.63E+01,
                     2.43E+01,
                     1.88E+01,
                     6.44E+00,
                     2.90E+00,
                     2.05E+00,
                     4.77E+00,
                     1.48E+01,
                     3.38E+01,
                     4.83E+01,
                     5.69E+01,
                     6.58E+01,
                     5.69E+01,
                     2.50E+01,
                     9.38E+00,
                     3.62E+00,
                     1.97E+00,
                     2.08E+00,
                     2.06E+00,
                     1.68E+00,
                     1.16E+00,
                     7.45E-01,
                     1.04E+00,
                     1.26E+00,
                     1.03E+00,
                     8.24E-01,
                     5.81E-01,
                     3.84E-01,
                     1.87E-01,
                     2.41E-01,
                     3.25E-01,
                     6.19E-01,
                     1.43E+00,
                     2.84E+00,
                     1.27E+00,
                     7.50E-01,
                     4.74E-01,
                     4.64E-01,
                     6.60E-01,
                     8.00E-01,
                     9.33E-01,
                     1.00E+00,
                     1.30E+00,
                     1.94E+00])

mask_1 = np.abs(V_over_H - 1) < 0.2
mask_niet1 = ~mask_1

grid = np.vstack((x, y)).T
fig = plt.figure(figsize=(6, 6))
ax = plt.subplot(111)
# sc = plt.scatter(x, y, s=200, c=V_over_H, cmap=plt.cm.jet, norm=LogNorm())
sc = plt.scatter(grid.T[0], grid.T[1], c=V_over_H, cmap=plt.cm.viridis, norm=LogNorm())
plt.scatter(grid.T[0][mask_1], grid.T[1][mask_1], s=150, facecolors='none', edgecolors='crimson', linewidths=2,
            label='S/P $\\sim$ 1')
plt.xlabel('Horizontal tilt [°]')
plt.ylabel('Vertical tilt  [°]')
plt.title('Tip-tilt dependence of coincidence S/P polarisation ratio')
cbar = fig.colorbar(sc, orientation='horizontal', ticks=[1, 10])
cbar.set_label('Ratio of S/P coincidences')
cbar.ax.set_xticklabels(['1', '10'])
plt.grid(alpha=.4)
plt.legend()
plt.savefig('tip_tilt_coincidences.pdf')
plt.show()


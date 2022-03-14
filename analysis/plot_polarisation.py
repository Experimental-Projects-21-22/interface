"""
Written by:
    Douwe Remmelts <remmeltsdouwe@gmail.com>
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ANGLE_VALUE = 0.399


def compute_fraction(max, min):
    return (max - min) / (max + min)


def compute_angle(max1, max2, min1, min2):
    max2 = (max2 + np.pi) % (2 * np.pi)
    min1 = (min1 + 3 / 2 * np.pi) % (2 * np.pi)
    min2 = (min2 + 1 / 2 * np.pi) % (2 * np.pi)
    angle = np.mean((max1, max2, min1, min2))

    if angle > np.pi:
        angle -= np.pi
    return angle


def create_label(ticks):
    labels = []
    for i in ticks:
        if round(i, 1) == round(i, 2):
            labels.append(str(round(i, 1)))
        else:
            labels.append('')
    return labels


pd.set_option('display.max_columns', 1000)

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

data = pd.read_csv('../tip_pol.csv')
data.drop(1)
coords = data['BBO tip-tilt (hor turns, vert turns)']

x = np.zeros(len(coords))
y = np.zeros(len(coords))

for i, coord_tuple in enumerate(coords):
    x[i], y[i] = eval(coord_tuple)

x *= ANGLE_VALUE
y *= ANGLE_VALUE

angle_min1 = np.deg2rad(data['angle minimum 1'] - 86)
angle_min2 = np.deg2rad(data['angle minimum 2'] - 86)
angle_max1 = np.deg2rad(data['angle maximum 1'] - 86)
angle_max2 = np.deg2rad(data['angle maximum 2'] - 86)

angle_min1_watt = data['minvalue 1 (mW)'].str.replace(',', '.').astype(float)
angle_min2_watt = data['minvalue 2 (mW)'].str.replace(',', '.').astype(float)
angle_max1_watt = data['maxvalue 1 (mW)'].str.replace(',', '.').astype(float)
angle_max2_watt = data['maxvalue 2 (mW)'].str.replace(',', '.').astype(float)

polarisation_fraction = np.zeros(len(angle_min2_watt))
polarisation_angle = np.zeros(len(angle_max2))

for i in range(len(x)):
    polarisation_fraction[i] = compute_fraction(np.mean((angle_max1_watt[i], angle_max2_watt[i])),
                                                np.mean((angle_min1_watt[i], angle_min2_watt[i])))

    polarisation_angle[i] = compute_angle(angle_max1[i], angle_max2[i], angle_min1[i], angle_min2[i])

dx = np.zeros(len(polarisation_angle))
dy = np.zeros(len(polarisation_angle))

for i in range(len(x)):
    dx[i] = polarisation_fraction[i] * np.cos(polarisation_angle[i])
    dy[i] = polarisation_fraction[i] * np.sin(polarisation_angle[i])

fig = plt.figure()
ax = fig.add_subplot(111)

plt.quiver(x, y, dx, dy, polarisation_fraction, scale=1.6)

x_ticks = np.arange(-0.15, 0.3, 0.05)
y_ticks = np.arange(-0.55, -0.05, 0.05)

x_labels = create_label(x_ticks)
y_labels = create_label(y_ticks)

create_label(x_ticks)

cbar = plt.colorbar()
cbar.set_label('Degree of polarisation')
plt.xlabel('Horizontal tilt [°]')
plt.ylabel('Vertical tilt [°]')
plt.title('Tip-tilt dependence of pump polarisation')
plt.xticks(x_ticks, x_labels)
plt.yticks(y_ticks, y_labels)
plt.grid(alpha=.4)

ax.set_aspect('equal')

plt.savefig('4d gekloot.pdf', bbox_inches='tight')
plt.show()

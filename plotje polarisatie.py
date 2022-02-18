import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Ellipse
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.lines as mlines
from numpy.linalg import eig, inv


prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

data = pd.read_csv('tip_pol.csv')
coords = data['BBO tip-tilt (hor turns, vert turns)']

x = np.zeros(len(coords))
y = np.zeros(len(coords))

for i, coord_tuple in enumerate(coords):
    x[i], y[i] = eval(coord_tuple)

fig = plt.figure(figsize=(6, 6))
ax = plt.subplot(111)

angle_min1 = np.deg2rad(data['angle minimum 1'] - 86)
angle_min2 = np.deg2rad(data['angle minimum 2'] - 86)
angle_max1 = np.deg2rad(data['angle maximum 1'] - 86)
angle_max2 = np.deg2rad(data['angle maximum 2'] - 86)

angle_min1_watt = data['minvalue 1 (mW)'].str.replace(',', '.')
angle_min2_watt = data['minvalue 2 (mW)'].str.replace(',', '.')
angle_max1_watt = data['maxvalue 1 (mW)'].str.replace(',', '.')
angle_max2_watt = data['maxvalue 2 (mW)'].str.replace(',', '.')

print(np.min(y))
print(np.max(y))

fig = plt.figure(figsize=(12, 12))
ax = plt.subplot(111)
ax.axis('off')
ax.set_xlim(-0.25, 0.5)
ax.set_ylim(-1.25, -0.25)
x_min1 = angle_min1_watt.astype(float) * np.cos(angle_min1)
y_min1 = angle_min1_watt.astype(float) * np.sin(angle_min1)
x_min2 = angle_min2_watt.astype(float) * np.cos(angle_min2)
y_min2 = angle_min2_watt.astype(float) * np.sin(angle_min2)
x_max1 = angle_max1_watt.astype(float) * np.cos(angle_max1)
y_max1 = angle_max1_watt.astype(float) * np.sin(angle_max1)
x_max2 = angle_max2_watt.astype(float) * np.cos(angle_max2)
y_max2 = angle_max2_watt.astype(float) * np.sin(angle_max2)

x_coord = np.linspace(-5,5,300)
y_coord = np.linspace(-5,5,300)
X_coord, Y_coord = np.meshgrid(x_coord, y_coord)

for i in range(len(x)):
    sub_ax = fig.add_axes([0.3 + x[i], 1.28 + y[i], 0.15, 0.20])

    # sub_ax.scatter(angle_min1[i], angle_min1_watt[i])
    # sub_ax.scatter(angle_min2[i], angle_min2_watt[i])
    # sub_ax.scatter(angle_max1[i], angle_max1_watt[i])
    # sub_ax.scatter(angle_max2[i], angle_max2_watt[i])
    sub_ax.scatter(x_min1[i], y_min1[i])
    sub_ax.scatter(x_min2[i], y_min2[i])
    sub_ax.scatter(x_max1[i], y_max1[i])
    sub_ax.scatter(x_max2[i], y_max2[i])
    sub_ax.hlines(0, -0.63, 0.63, colors='black', linestyle='--')
    sub_ax.vlines(0, -0.63, 0.63, colors='black', linestyle='--')
    sub_ax.set_aspect('equal', adjustable='box')
    sub_ax.set_xlim(-0.63, 0.63)
    sub_ax.set_ylim(-0.63, 0.63)
    sub_ax.set_xticks([-0.5, -0.25, 0, 0.25, 0.5])
    sub_ax.set_yticks([-0.5, -0.25, 0, 0.25, 0.5])
    sub_ax.set_xticklabels(['-0.5', '-0.25', '0', '0.25', '0.5'])
    sub_ax.set_yticklabels(['-0.5', '-0.25', '0', '0.25', '0.5'])
    sub_ax.set_title(f'x = {x[i]}, y={y[i]}')
    sub_ax.set_xlabel('$I_x$ (mW)')
    sub_ax.set_ylabel('$I_y$ (mW)')
    sub_ax.grid(alpha=.4)

    x_coords = np.array([x_min1[i], x_min2[i], x_max1[i], x_max2[i]])
    y_coords = np.array([y_min1[i], y_min2[i], y_max1[i], y_max2[i]])

handles = []
labels = ['First minimum', 'Second minimum', 'First maximum', 'Second maximum']

for i in range(4):
    handles.append(mlines.Line2D([], [], color=colors[i], marker='o', markersize=5, label=labels[i]))

ax.legend1(handles=handles, bbox_to_anchor=(1.10, 1.10), loc='upper left')
plt.savefig('4d gekloot.png', bbox_inches='tight')
plt.show()

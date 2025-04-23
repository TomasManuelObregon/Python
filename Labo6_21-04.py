#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 10:14:58 2025

@author: tomas
"""

"""
@author: Tomás Obregón
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy import optimize as op
import os

# font_path = '/Users/tomas/Documents/venv/tw-cen-mt.ttf'  # Ruta completa al archivo de fuente
# font_prop = font_manager.FontProperties(fname=font_path)

c_texto='#2D2A21'


def true_gaussian(dom, amp, ux, uy, a, b, c, offs):
    x,y = dom
    return amp * np.exp(a*((x-ux)**2) + b*(x-ux)*(y-uy) + c*((y-uy)**2)) + offs


#%%
file_name = 'eje_Y_autocorrelacion.csv'
path = os.path.expanduser("~/Downloads/"+file_name)

datos = np.loadtxt(path, skiprows=1, delimiter=',')

# se ve que solo importa el eje z
z = datos[:, 2].reshape(1080,1920)

# Coordenadas X e Y
x = np.arange(0, z.shape[1])
y = np.arange(0, z.shape[0])
X, Y = np.meshgrid(x, y)

# Maximos
y_max, x_max = np.unravel_index(np.argmax(z), z.shape)

# Mascara
mask=10
x_mask = X[y_max-mask:y_max+mask+1, x_max-mask:x_max+mask+1] 
y_mask = Y[y_max-mask:y_max+mask+1, x_max-mask:x_max+mask+1] 
z_mask = z[y_max-mask:y_max+mask+1, x_max-mask:x_max+mask+1] 
# x_mask = X[x_max-mask:x_max+mask+1, y_max-mask:y_max+mask+1] 
# y_mask = Y[x_max-mask:x_max+mask+1, y_max-mask:y_max+mask+1] 
# z_mask = z[x_max-mask:x_max+mask+1, y_max-mask:y_max+mask+1] 


plt.close('all')
# Definir figura con gridspec
fig = plt.figure(figsize=(10, 5))
gs = fig.add_gridspec(2, 2, width_ratios=[2, 1])  # gráfico izquierdo más ancho
# Gráfico IZQUIERDO - ocupa dos filas
ax1 = fig.add_subplot(gs[:, 0], projection='3d')
ax1.plot_surface(x_mask, y_mask, z_mask, color='r', linewidth=0, antialiased=True, alpha=.8)

ax1.set_xlabel('$\hat{x}$ [px]')
ax1.set_ylabel('$\hat{y}$ [px]')
ax1.set_zticks([])
ax1.tick_params(axis='both', labelsize=10)
# ax1.set_box_aspect([mask*2, mask*2, 1])
ax1.set_box_aspect([z.shape[1]/z.shape[0], 1, 1])
ax1.view_init(40, -75)

# Gráfico SUPERIOR DERECHO
ax2 = fig.add_subplot(gs[0, 1], projection='3d')
ax2.plot_surface(X, Y, z, cmap='viridis', linewidth=0, antialiased=False, alpha=.15)
ax2.plot_surface(x_mask, y_mask, z_mask, color='r', linewidth=0, antialiased=False)

ax2.set_xlabel('$\hat{x}$ [px]')
ax2.set_ylabel('$\hat{y}$ [px]')
ax2.set_zticks([])
ax2.tick_params(axis='both', labelsize=10)
ax2.set_box_aspect([z.shape[1]/z.shape[0], 1, 1])
ax2.view_init(40, -75)

# Gráfico INFERIOR DERECHO
ax3 = fig.add_subplot(gs[1, 1], projection='3d')
ax3.plot_surface(X, Y, z, cmap='viridis', linewidth=0, antialiased=False, alpha=.15)
ax3.plot_surface(x_mask, y_mask, z_mask, color='r', linewidth=0, antialiased=False)

ax3.set_xticks([])
ax3.set_yticks([])
ax3.set_zticks([])
ax3.tick_params(axis='both', labelsize=10)
ax3.set_box_aspect([z.shape[1]/z.shape[0], 1, 1])
ax3.view_init(90, -90)

plt.tight_layout()
plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
plt.show()

#%%

# Aplanamos para el ajuste
x_flat = x_mask.ravel()
y_flat = y_mask.ravel()
z_flat = z_mask.ravel()

# creo el meshgrid
x_dense = np.linspace(min(x_flat), max(x_flat), 100)
y_dense = np.linspace(min(y_flat), max(y_flat), 100)
x_dense, y_dense = np.meshgrid(x_dense, y_dense)

# AJUSTE
low = [0,      x_max-mask//2, y_max-1, -np.inf, -np.inf, -np.inf, -np.inf]
up  = [np.inf, x_max+mask//2, y_max+1,  np.inf,  np.inf,  np.inf, np.mean(z)]

popt, pcov = op.curve_fit(true_gaussian, (x_flat, y_flat), z_flat,
                          p0=[np.max(z)-np.min(z), x_max, y_max, 0,0,0, np.min(z)])

amp, ux, uy, a, b, c, offs = popt
err_ux = np.sqrt(pcov[1,1])
err_uy = np.sqrt(pcov[2,2])

z_dense = true_gaussian((x_dense, y_dense), *popt)


# Residuos
z_dense_para_residuos =  true_gaussian((x_mask, y_mask), *popt)
res = z_mask - z_dense_para_residuos


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Grafico - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

plt.close('all')
fig = plt.figure(figsize=(8, 8))

# AX1 - - - - 
ax1 = fig.add_subplot(2,2,1, projection='3d')

# Rojo
ax1.plot_surface(x_mask, y_mask, z_mask, color='r', alpha=.3)
ax1.errorbar([x_max], [y_max], [max(z_flat)], xerr=2, yerr=2,
              capsize=3, elinewidth=1, marker='x', color='red', markersize=5)

# Verde
ax1.errorbar([ux], [uy], [np.max(z_dense)], xerr=err_ux, yerr=err_uy,
              capsize=3, elinewidth=1, marker='x', color='g', markersize=5)
ax1.plot_surface(x_dense, y_dense, z_dense, color='g', alpha=.3)


ax1.set_xlabel('$\hat{x}$ [px]')
ax1.set_ylabel('$\hat{y}$ [px]')
ax1.set_zticks([])
ax1.set_box_aspect([z_mask.shape[1]/z_mask.shape[0], 1, 1])
ax1.view_init(90, -90)


# AX2 - - - - 
ax2 = fig.add_subplot(2,2,2, projection='3d')

# Rojo
ax2.plot_surface(x_mask, y_mask, z_mask, color='r', alpha=.3)
ax2.errorbar([x_max], [y_max], [max(z_flat)], xerr=2,
              capsize=3, elinewidth=1, marker='x', color='red', markersize=5)

# Verde
ax2.errorbar([ux], [uy], [np.max(z_dense)], xerr=err_ux, 
              capsize=3, elinewidth=1, marker='x', color='g', markersize=5)
ax2.plot_surface(x_dense, y_dense, z_dense, color='g', alpha=.3)

ax2.set_xlabel('$\hat{x}$ [px]')
ax2.set_zlabel('Intensidad')
ax2.set_yticks([])
ax2.set_box_aspect([z_mask.shape[1]/z_mask.shape[0], 1, 1])
ax2.view_init(0, -90)


# AX3 - - - - 
ax3 = fig.add_subplot(2,2,3, projection='3d')

# Rojo
ax3.plot_surface(x_mask, y_mask, z_mask, color='r', alpha=.3)
ax3.errorbar([x_max], [y_max], [max(z_flat)], yerr=2,
              capsize=3, elinewidth=1, marker='x', color='red', markersize=5)

# Verde
ax3.errorbar([ux], [uy], [np.max(z_dense)], yerr=err_uy,
              capsize=3, elinewidth=1, marker='x', color='g', markersize=5)
ax3.plot_surface(x_dense, y_dense, z_dense, color='g', alpha=.3)

ax3.set_zlabel('Intensidad')
ax3.set_ylabel('$\hat{y}$ [px]')
ax3.set_xticks([])
ax3.set_box_aspect([z_mask.shape[1]/z_mask.shape[0], 1, 1])
ax3.view_init(0,0)

# AX4 - - - - 
ax4 = fig.add_subplot(2,2,4, projection='3d')
ax4.plot_surface(x_mask, y_mask, res/1e5, color='g', alpha=.3)

ax4.set_zlabel('Residuos (1e6)')
ax4.set_ylabel('$\hat{y}$ [px]')
ax4.set_xlabel('$\hat{x}$ [px]')
# ax4.set_zticks([-6e5, -4e5, -2e5, 0, 2e5, 4e5, 6e5, 8e5])
ax4.set_box_aspect([z_mask.shape[1]/z_mask.shape[0], 1, 1])
ax4.view_init(10, -10)

plt.tight_layout()
plt.show()

#%%
x_nm = (1920 - ux)*19.7 
err_x_nm = err_ux * 19.7

y_nm = (1080 - uy)*19.7 
err_y_nm = err_uy * 19.7













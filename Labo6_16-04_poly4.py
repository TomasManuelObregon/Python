"""
@author: Tomás Obregón
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy import optimize as op
import os

font_path = '/Users/tomas/Documents/venv/tw-cen-mt.ttf'  # Ruta completa al archivo de fuente
font_prop = font_manager.FontProperties(fname=font_path)

c_texto='#2D2A21'

def poly4(dom, a, b, c, d, e, f, g, h, i, j):
    x,y = dom
    return a*x**4 + b*x**3 + c*x**2 + d*x + e*y**4 + f*y**3 + g*y**2 + h*y + i*x*y + j



mask=20


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
x_max, y_max = np.unravel_index(np.argmax(z), z.shape)

# Mascara
x_mask = X[x_max-mask:x_max+mask+1, y_max-mask:y_max+mask+1] 
y_mask = Y[x_max-mask:x_max+mask+1, y_max-mask:y_max+mask+1] 
z_mask = z[x_max-mask:x_max+mask+1, y_max-mask:y_max+mask+1] 

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




# DEFINO ESTA FUNCION ACA PARA TENER MAS ESPACIO PARA PENSAR
def graficar(x_dense, y_dense, z_dense, x_dense_max, y_dense_max):
    plt.close('all')
    fig = plt.figure(figsize=(12, 4))
    
    # AX1 - - - - 
    ax1 = fig.add_subplot(1,3,1, projection='3d')
    
    # Rojo
    ax1.plot_surface(x_mask, y_mask, z_mask, color='r', alpha=.3)
    ax1.errorbar([y_max], [x_max], [max(z_flat)], xerr=2, yerr=2,
                  capsize=3, elinewidth=1, marker='x', color='red', markersize=5)
    
    # Azul
    ax1.plot_surface(x_dense, y_dense, z_dense, color='b', alpha=.3)
    ax1.errorbar([x_dense_max], [y_dense_max], [np.max(z_dense)], xerr=1/100, yerr=1/100,
                  capsize=3, elinewidth=1, marker='x', color='b', markersize=5)
    
    ax1.set_xlabel('$\hat{x}$ [px]')
    ax1.set_ylabel('$\hat{y}$ [px]')
    ax1.set_zticks([])
    ax1.set_box_aspect([z_mask.shape[1]/z_mask.shape[0], 1, 1])
    ax1.view_init(90, -90)
    
    # AX2 - - - - 
    ax2 = fig.add_subplot(1,3,2, projection='3d')
    
    # Rojo
    ax2.plot_surface(x_mask, y_mask, z_mask, color='r', alpha=.3)
    ax2.errorbar([y_max], [x_max], [max(z_flat)], xerr=2,
                  capsize=3, elinewidth=1, marker='x', color='red', markersize=5)
    
    # Azul
    ax2.plot_surface(x_dense, y_dense, z_dense, color='b', alpha=.3)
    ax2.errorbar([x_dense_max], [y_dense_max], [np.max(z_dense)], xerr=1/100,
                  capsize=3, elinewidth=1, marker='x', color='b', markersize=5)
    
    ax2.set_xlabel('$\hat{x}$ [px]')
    ax2.set_zlabel('Intensidad')
    ax2.set_yticks([])
    ax2.set_box_aspect([z_mask.shape[1]/z_mask.shape[0], 1, 1])
    ax2.view_init(0, -90)
    
    # AX3 - - - - 
    ax3 = fig.add_subplot(1,3,3, projection='3d')
    
    # Rojo
    ax3.plot_surface(x_mask, y_mask, z_mask, color='r', alpha=.3)
    ax3.errorbar([y_max], [x_max], [max(z_flat)], yerr=2,
                  capsize=3, elinewidth=1, marker='x', color='red', markersize=5)
    
    # 
    ax3.plot_surface(x_dense, y_dense, z_dense, color='b', alpha=.3)
    ax3.errorbar([x_dense_max], [y_dense_max], [np.max(z_dense)], yerr=1/100,
                  capsize=3, elinewidth=1, marker='x', color='b', markersize=5)
    
    
    ax3.set_zlabel('Intensidad')
    ax3.set_ylabel('$\hat{y}$ [px]')
    ax3.set_xticks([])
    ax3.set_box_aspect([z_mask.shape[1]/z_mask.shape[0], 1, 1])
    ax3.view_init(0,0)
    
    plt.tight_layout()
    plt.show()





#%%

# Aplanamos para el ajuste
x_flat = x_mask.ravel()
y_flat = y_mask.ravel()
z_flat = z_mask.ravel()

popt, pcov = op.curve_fit(poly4, (x_flat, y_flat), z_flat,
                          p0=[0, 0, 0, 0, 0, 0, 0, 0, 0, np.mean(z)])

x_dense = np.linspace(min(x_flat), max(x_flat), 100)
y_dense = np.linspace(min(y_flat), max(y_flat), 100)
x_dense, y_dense = np.meshgrid(x_dense, y_dense)

z_dense = poly4((x_dense, y_dense), *popt)

x_dense_max_idx, y_dense_max_idx = np.unravel_index(np.argmax(z_dense), z_dense.shape)

x_dense_max = x_dense[x_dense_max_idx, y_dense_max_idx] 
y_dense_max = y_dense[x_dense_max_idx, y_dense_max_idx]
    
graficar(x_dense, y_dense, z_dense, x_dense_max, y_dense_max)

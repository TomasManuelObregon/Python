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


def paraboloide(dom, a, b, c, d, e, f):
    x,y = dom
    return a*x**2 + b*y**2 + c*x*y + d*x + e*y + f

def gaussian(dom, amp, sx, ux, sy, uy, offs):
    x,y = dom
    
    f = np.exp(-(((x-ux)/sx)**2)/2)/sx
    g = np.exp(-(((y-uy)/sy)**2)/2)/sy

    return amp*f*g + offs

def lorentz(dom, amp, x0, gx, y0, gy, offs):
    x,y = dom
    
    f = (((x-x0)**2) + gx**2)/gx**2    
    g = (((y-y0)**2) + gy**2)/gy**2

    return amp/(1+f+g)+ offs

def poly4(x, y, a, b, c, d, e, f, g, h, i, j):
    return a*x**4 + b*x**3 + c*x**2 + d*x + e*y**4 + f*y**3 + g*y**2 + h*y + i*x*y + j


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
mask=20
x_mask = X[x_max-mask:x_max+mask, y_max-mask:y_max+mask] 
y_mask = Y[x_max-mask:x_max+mask, y_max-mask:y_max+mask] 
z_mask = z[x_max-mask:x_max+mask, y_max-mask:y_max+mask] 


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

# plt.savefig('/Users/tomas/Desktop/figura3d.png', bbox_inches='tight')


#%%

# Aplanamos para el ajuste
x_flat = x_mask.ravel()
y_flat = y_mask.ravel()
z_flat = z_mask.ravel()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Curve_fit - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
popt_p, pcov_p = op.curve_fit(paraboloide, (x_flat, y_flat), z_flat, p0 = [0,0,0,0,0,np.mean(z)])
a = popt_p[0]
b = popt_p[1]
c = popt_p[2]
d = popt_p[3]
e = popt_p[4]
f = popt_p[5]
err_a = np.sqrt(pcov_p[0][0])
err_b = np.sqrt(pcov_p[1][1])
err_c = np.sqrt(pcov_p[2][2])
err_d = np.sqrt(pcov_p[3][3])
err_e = np.sqrt(pcov_p[4][4])
err_f = np.sqrt(pcov_p[5][5])
# print("Parámetros ajustados:", popt_p)

x_dense = np.linspace(min(x_flat), max(x_flat), 100)
y_dense = np.linspace(min(y_flat), max(y_flat), 100)
x_dense, y_dense = np.meshgrid(x_dense, y_dense)

z_dense = paraboloide((x_dense, y_dense), *popt_p)

den = (4*a*b-c**2)
x_max_fit = (c*e - 2*b*d)/den
y_max_fit = (c*d - 2*a*e)/den

# derivadas de x_max_fit
dax = 4*b*(c*e - 2*b*d)/(den**2)
dbx = (2*d*(c**2) - 4*a*c*e)/(den**2)
dcx = (4*a*b*e + e*(c**2) - 4*c*b*d)/(den**2)
ddx = 2*b/den
dex = c/den

err_x_max_fit = np.sqrt((dax*err_a)**2+
                        (dbx*err_b)**2+
                        (dcx*err_c)**2+
                        (ddx*err_d)**2+
                        (dex*err_e)**2)


# err_x_max_fit = 0
err_y_max_fit = 0


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# gaussian  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
lower_bounds = [0,      0.1,    x_max-mask,     0.1,     y_max-mask,   np.mean(z)-np.mean(z)/2]
upper_bounds = [np.inf, 10,     x_max+mask,     10,      y_max+mask,   np.mean(z)+np.mean(z)/2]


popt_g, pcov_g = op.curve_fit(gaussian, (x_flat, y_flat), z_flat, 
                              p0=[0, 0.1, x_max, 0.1, y_max, np.mean(z)],
                              bounds=(lower_bounds, upper_bounds))

amp_g, sx, ux, sy, uy, offs = popt_g
err_ux = np.sqrt(pcov_g[2,2])
err_uy = np.sqrt(pcov_g[4,4])
             
z_dense_g = gaussian((x_dense, y_dense), *popt_g)



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Lorentz - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
lower_bounds = [0     ,    x_max-mask,     0.1,  y_max-mask,  0.1,   np.mean(z)-np.mean(z)/2]
upper_bounds = [np.inf,    x_max+mask,     np.inf,    y_max+mask,  np.inf,     np.mean(z)+np.mean(z)/2]

popt_l, pcov_l = op.curve_fit(lorentz, (x_flat, y_flat), z_flat,
                              p0=[0, x_max, 0.1, y_max, 0.1, np.mean(z)],
                              bounds=(lower_bounds, upper_bounds))

amp_f, x0, gx, y0, gy, offs_l = popt_l
err_x0 = np.sqrt(pcov_g[1,1])
err_y0 = np.sqrt(pcov_g[3,3])

z_dense_l = lorentz((x_dense, y_dense), *popt_l)



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Grafico - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

plt.close('all')
fig = plt.figure(figsize=(12, 4))

# AX1 - - - - 
ax1 = fig.add_subplot(1,3,1, projection='3d')

# Rojo
ax1.plot_surface(x_mask, y_mask, z_mask, color='r', alpha=.3)
ax1.errorbar([y_max], [x_max], [max(z_flat)], xerr=2, yerr=2,
              capsize=3, elinewidth=1, marker='x', color='red', markersize=5)

# Azul
ax1.errorbar([x_max_fit], [y_max_fit], [np.max(z_dense)], xerr=err_x_max_fit, yerr=err_y_max_fit,
              capsize=3, elinewidth=1, marker='x', color='b', markersize=5)
ax1.plot_surface(x_dense, y_dense, z_dense, color='b', alpha=.3)

# Verde
ax1.plot_surface(x_dense, y_dense, z_dense_g, color='g', alpha=.3)
ax1.errorbar([uy], [ux], [np.max(z_dense_g)], xerr=err_ux, yerr=err_uy,
              capsize=3, elinewidth=1, marker='x', color='g', markersize=5)

# Naranja
ax1.plot_surface(x_dense, y_dense, z_dense_l, color='orange', alpha=.3)
ax1.errorbar([y0], [x0], [np.max(z_dense_l)], xerr=err_x0, yerr=err_y0,
              capsize=3, elinewidth=1, marker='x', color='orange', markersize=5)

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
ax2.errorbar([x_max_fit], [y_max_fit], [np.max(z_dense)], xerr=err_x_max_fit,
              capsize=3, elinewidth=1, marker='x', color='b', markersize=5)
ax2.plot_surface(x_dense, y_dense, z_dense, color='b', alpha=.3)

# Verde
ax2.plot_surface(x_dense, y_dense, z_dense_g, color='g', alpha=.3)
ax2.errorbar([uy], [ux], [np.max(z_dense_g)] , xerr=err_ux, 
              capsize=3, elinewidth=1, marker='x', color='g', markersize=5)

# Naranja
ax2.plot_surface(x_dense, y_dense, z_dense_l, color='orange', alpha=.3)
ax2.errorbar([y0], [x0], [np.max(z_dense_l)], xerr=err_x0, yerr=err_y0,
              capsize=3, elinewidth=1, marker='x', color='orange', markersize=5)

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

# Azul
ax3.errorbar([x_max_fit], [y_max_fit], [np.max(z_dense)], yerr=err_y_max_fit,
              capsize=3, elinewidth=1, marker='x', color='b', markersize=5)
ax3.plot_surface(x_dense, y_dense, z_dense, color='b', alpha=.3)

# Verde
ax3.plot_surface(x_dense, y_dense, z_dense_g, color='g', alpha=.3)
ax3.errorbar([uy], [ux], [np.max(z_dense_g)], yerr=err_uy,
              capsize=3, elinewidth=1, marker='x', color='g', markersize=5)

# Naranja
ax3.plot_surface(x_dense, y_dense, z_dense_l, color='orange', alpha=.3)
ax3.errorbar([y0], [x0], [np.max(z_dense_l)], xerr=err_x0, yerr=err_y0,
              capsize=3, elinewidth=1, marker='x', color='orange', markersize=5)

ax3.set_zlabel('Intensidad')
ax3.set_ylabel('$\hat{y}$ [px]')
ax3.set_xticks([])
ax3.set_box_aspect([z_mask.shape[1]/z_mask.shape[0], 1, 1])
ax3.view_init(0,0)

plt.tight_layout()
plt.show()




#%%



# plt.close('all')
# # Definir figura con gridspec
# fig = plt.figure(figsize=(10, 5))
# # Gráfico IZQUIERDO - ocupa dos filas
# ax1 = fig.add_subplot(111, projection='3d')
# ax1.plot_surface(X, Y, z, cmap='viridis', linewidth=0, antialiased=False, alpha=.15)
# ax1.plot_surface(x_dense, y_dense, z_dense_g, color='g', alpha=.6)
# ax1.errorbar([uy], [ux], [np.max(z_dense_g)], xerr=err_ux, yerr=err_uy,
#               capsize=3, elinewidth=1, marker='x', color='g', markersize=5)

# ax1.set_xlabel('$\hat{x}$ [px]')
# ax1.set_ylabel('$\hat{y}$ [px]')
# ax1.set_zticks([])
# ax1.tick_params(axis='both', labelsize=10)
# # ax1.set_box_aspect([mask*2, mask*2, 1])
# ax1.set_box_aspect([z.shape[1]/z.shape[0], 1, 1])
# ax1.view_init(40, -75)
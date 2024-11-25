"""
@author: Tomás Obregón
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy import optimize as op
import os

font_path = '/Users/tomas/ev/tw-cen-mt.ttf'  # Ruta completa al archivo de fuente
font_prop = font_manager.FontProperties(fname=font_path)

c_texto='#2D2A21'

def wavelength_to_hex(wavelength):
    # Esta función convierte una longitud de onda (lambda) a un color HEX.
    if 380 <= wavelength < 440:
        r = -(wavelength - 440) / (440 - 380)
        g = 0.0
        b = 1.0
    elif 440 <= wavelength < 490:
        r = 0.0
        g = (wavelength - 440) / (490 - 440)
        b = 1.0
    elif 490 <= wavelength < 510:
        r = 0.0
        g = 1.0
        b = -(wavelength - 510) / (510 - 490)
    elif 510 <= wavelength < 580:
        r = (wavelength - 510) / (580 - 510)
        g = 1.0
        b = 0.0
    elif 580 <= wavelength < 645:
        r = 1.0
        g = -(wavelength - 645) / (645 - 580)
        b = 0.0
    elif 645 <= wavelength <= 750:
        r = 1.0
        g = 0.0
        b = 0.0
    else:
        r = g = b = 0.0  # Fuera del espectro visible

    # Ajuste de intensidad (aproximado) para los extremos del espectro visible
    if 380 <= wavelength < 420:
        factor = 0.3 + 0.7 * (wavelength - 380) / (420 - 380)
    elif 645 <= wavelength <= 750:
        factor = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
    else:
        factor = 1.0

    r = int(r * factor * 255)
    g = int(g * factor * 255)
    b = int(b * factor * 255)

    return "#{:02x}{:02x}{:02x}".format(r, g, b)

lineal = lambda x,m,b: x*m + b

lorentz = lambda x,x0,amp,sigma: amp * np.exp((-(x-x0)**2)/(2*(sigma**2))) 

def saca_v0(x, y):    
    idx_min = min(range(len(x)), key=lambda i: abs(x[i] - 2))
    idx_max = min(range(len(x)), key=lambda i: abs(x[i] - 4))

    # Dividir datos en dos conjuntos
    x1, x2 = x[1:60], x[idx_min:idx_max]
    y1, y2 = y[1:60], y[idx_min:idx_max]
    y1err, y2err = y1 * .03, y2 * .03

    # Ajuste para la primera sección
    p0_1 = [0, 0.05]
    popt1, pcov1 = op.curve_fit(lineal, x1, y1, sigma=y1err, absolute_sigma=True, p0=p0_1)

    # Ajuste para la segunda sección
    p0_2 = [0.3, -0.6]
    popt2, pcov2 = op.curve_fit(lineal, x2, y2, sigma=y2err, absolute_sigma=True, p0=p0_2)
    

    # Calcular el punto de intersección
    m = (popt1[0] - popt2[0])
    b = (popt2[1] - popt1[1])
    v0 = b / m
    # y_interseccion = popt1[0] * v0 + popt1[1]
    
    return v0

#%%
path = os.path.expanduser("~/Desktop/Dia 4/laser rojo")
archivos = sorted(os.listdir(path))[:-1]

markers= ["o", "s", "x"]
markers_size= [5,6,7]

plt.close('all')
plt.figure(figsize=[10,6])
plt.subplots_adjust(left=0.09,   # Posición del límite izquierdo
                    bottom=0.13,  # Posición del límite inferior
                    right=0.97,    # Posición del límite derecho
                    top=0.95)     # Posición del límite superior

for idx, i in enumerate(archivos):
    data = np.loadtxt(path+'/'+i, delimiter='\t')
    
    plt.errorbar(data[1:,0], data[1:,1], yerr=data[1:,1]*.03,
                 c=wavelength_to_hex(650),
                 linewidth=1, elinewidth=2, capsize=2,
                 label=f'{int(i[10:12])}°', marker=markers[idx], markersize=markers_size[idx])


plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.xlabel('Voltaje [V]', fontsize=25, fontproperties=font_prop)
plt.ylabel('Corriente [A]', fontsize=25, fontproperties=font_prop)
plt.legend(loc='upper left', prop={'size': 18, 'fname': font_path})
plt.yticks(fontsize=18)  
plt.xticks(fontsize=18)#, ticks=[1,2,3,4,5]) 
plt.xlim(-4.5,4.5)

# plt.gca().set_facecolor('none')
# plt.gcf().patch.set_alpha(0)  
plt.show()
plt.savefig('votl_corr_laser.png', dpi=1000, bbox_inches='tight')

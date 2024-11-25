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
    m1, b1 = popt1
    err_m1 = np.sqrt(pcov1[0][0])
    err_b1 = np.sqrt(pcov1[1][1])

    # Ajuste para la segunda sección
    p0_2 = [0.3, -0.6]
    popt2, pcov2 = op.curve_fit(lineal, x2, y2, sigma=y2err, absolute_sigma=True, p0=p0_2)
    m2, b2 = popt2
    err_m2 = np.sqrt(pcov2[0][0])
    err_b2 = np.sqrt(pcov2[1][1])

    # Calcular el punto de intersección
    m = (m1 - m2)
    b = (b2 - b1)
    
    v0 = b / m
    err_v0 = np.sqrt(
        ((err_b1/m)**2)+
        ((err_b2/m)**2)+
        (((err_m1*b)/(m**2))**2)+
        (((err_m2*b)/(m**2))**2)
        )
    
    return v0, err_v0

#%%
path = os.path.expanduser("~/Desktop/Dia 4/barrido_volt LED")
archivos = sorted(os.listdir(path))[2::1]

# wl = [float(i[10:13]) for i in archivos]
# wl[0]=420.0

wl, err_wl = np.loadtxt('/Users/tomas/Desktop/Dia 4/true_wl')
wl=list(wl[1::1])
err_wl=list(err_wl[1::1])


c  = 299792458e9
nus = [c/i for i in wl]
err_nus = [(c*i)/(wl[idx]**2) for idx, i in enumerate(err_wl)]


peaks=[]
err_peaks=[]
vceros=[]
err_vceros=[]

plt.close('all')
plt.figure(figsize=[10,6])
plt.subplots_adjust(left=0.09,   # Posición del límite izquierdo
                    bottom=0.13,  # Posición del límite inferior
                    right=0.97,    # Posición del límite derecho
                    top=0.95)     # Posición del límite superior

for idx, i in enumerate(wl):
    data = np.loadtxt(path+'/'+archivos[idx], delimiter='\t')

    v0, err_v0 = saca_v0(data[:,0], data[:,1])
    vceros.append(v0)
    err_vceros.append(err_v0)
    
    idx_prueba = min(range(len(data[1:,0])), key=lambda i: abs(data[i,0] - 4))
    peaks.append(data[idx_prueba,1])
    err_peaks.append(data[idx_prueba,1]*.03)
    
    plt.errorbar(data[1:,0], data[1:,1], yerr=data[1:,1]*.03,
                 linewidth=1, elinewidth=2, capsize=2,
                 label=f'{round(i)} nm', marker='.', c=wavelength_to_hex(i), alpha=.4)
    
plt.axvspan(2, 4, color=c_texto, alpha=0.15, linewidth=2, zorder=0)

plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.xlabel('Voltaje [V]', fontsize=25, fontproperties=font_prop)
plt.ylabel('Corriente [A]', fontsize=25, fontproperties=font_prop)
plt.legend(loc='center left', prop={'size': 12, 'fname': font_path})
plt.yticks(fontsize=18, ticks=[0, 1e-9, 2e-9,3e-9,4e-9])  
plt.xticks(fontsize=18)
plt.xlim(-4.5,8.5)

# plt.gca().set_facecolor('none')
# plt.gcf().patch.set_alpha(0)  
plt.show()
# plt.savefig('votl_corr.png', dpi=1000, bbox_inches='tight')


# %%
plt.close('all')
plt.figure(figsize=[10,6]) 
plt.subplots_adjust(left=0.12,           # Posición del límite izquierdo
                    bottom=0.13,          # Posición del límite inferior
                    right=0.97,           # Posición del límite derecho
                    top=0.95)             # Posición del límite superior

for idx, i in enumerate(wl):
    plt.errorbar(nus[idx], peaks[idx], yerr=err_peaks[idx], xerr=err_nus[idx],
                 capsize=3.5, linewidth=0, elinewidth=1.5,
                 c=wavelength_to_hex(i), marker='d', label=f'{round(i)} nm', zorder=2)
    
plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.xlabel(r'$\nu$ [Hz]', fontsize=25, fontproperties=font_prop)
plt.ylabel('Corriente [A]', fontsize=25, fontproperties=font_prop)
plt.legend(loc='upper left', prop={'size': 12, 'fname': font_path})
plt.yticks(fontsize=18, ticks=[0, .5e-9, 1e-9, 1.5e-9, 2e-9, 2.5e-9, 3e-9])  
plt.xticks(fontsize=18) 
plt.ylim(-.15e-9, 3.15e-9)
plt.xlim(3.9e14, 7.1e14)
    
# plt.gca().set_facecolor('none')
# plt.gcf().patch.set_alpha(0)  
plt.show()
plt.savefig('nu_corr_voltajefijo.png', dpi=1000, bbox_inches='tight')


    
#%%
popt_v0, pcov_v0 = op.curve_fit(lineal, nus, vceros, absolute_sigma=True, sigma=err_vceros)#, p0=[-6.6e-34/1.602e-19,0.5]) 
m_v0, b_v0 = popt_v0
err_m_v0 = np.sqrt(pcov_v0[0][0])
err_b_v0 = np.sqrt(pcov_v0[1][1])

dom_v0 = np.linspace(min(nus), max(nus), 1000)
im_v0  = lineal(dom_v0, m_v0, b_v0)

plt.close('all')
plt.figure(figsize=[10,6]) 
plt.subplots_adjust(left=0.125,           # Posición del límite izquierdo
                    bottom=0.13,          # Posición del límite inferior
                    right=0.97,           # Posición del límite derecho
                    top=0.95)             # Posición del límite superior

for idx, i in enumerate(wl):
    
    plt.errorbar(nus[idx], vceros[idx], yerr= err_vceros[idx], xerr=err_nus[idx],
                 capsize=3, elinewidth=2,linewidth=0
                 ,c=wavelength_to_hex(i), marker='d', label=f'{round(i)} nm', zorder=2)

plt.plot(dom_v0, im_v0, linewidth=2.5, c='black', alpha=.5, label='Ajuste',zorder=0)

plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.xlabel(r'$\nu$ [Hz]', fontsize=25, fontproperties=font_prop)
plt.ylabel('Voltaje de frenado [V]', fontsize=25, fontproperties=font_prop)
plt.legend(loc='center right', prop={'size': 12, 'fname': font_path})
plt.yticks(fontsize=18)  
plt.xticks(fontsize=18, ticks=[4e14, 4.5e14, 5e14, 5.5e14, 6e14, 6.5e14, 7e14]) 
plt.xlim(3.9e14, 7.6e14)
 
# plt.gca().set_facecolor('none')
# plt.gcf().patch.set_alpha(0)  
plt.show()
plt.savefig('nu_corr.png', dpi=1000, bbox_inches='tight')


print(f'h: {abs(m_v0*1.602e-19)*1e34} ± {abs(err_m_v0*1.602e-19)*1e34}')
# print(f'phi: {abs(b_v0*1.602e-19)} ± {abs(err_b_v0*1.602e-19)}')

#%%

nu_min = 4.775613754882419e14
err_nu_min = 0.12190280488657677e14

h = abs(m_v0*1.602e-19)
err_h = abs(err_m_v0*1.602e-19)

phi = h*nu_min
err_phi = np.sqrt((err_h*nu_min)**2 + (h*err_nu_min)**2)


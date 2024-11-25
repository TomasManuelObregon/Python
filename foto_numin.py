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


#%%
path = os.path.expanduser("~/Desktop/Dia 4/barrido_volt LED")
archivos = sorted(os.listdir(path))[1:] 

wl, err_wl = np.loadtxt('/Users/tomas/Desktop/Dia 4/true_wl')

c  = 299792458e9
nus = [c/i for i in wl]
err_nus = [(c*i)/(wl[idx]**2) for idx, i in enumerate(err_wl)]

nu_min = []        
err_nu_min = []        

idx_vf = 93 # Es el indice con el que empiezo a usar los voltajes fijos, corresponde a 2V

for j in range(19): # Hago 19 pasadas porque el indice 93+19=112 corresponde a 4V
    cvf_j = []        # cvf = Corriente para un Voltaje Fijo
    
    for idx, i in enumerate(wl):
        data = np.loadtxt(path+'/'+archivos[idx], delimiter='\t')
        corr = data[1:,1]
        cvf_j.append(corr[idx_vf])

        # plt.scatter(data[1:,0], corr)
        # plt.axhline(corr[idx_vf])
        
    
    mean = np.mean(cvf_j[-3:])
    std  = np.std(cvf_j[-3:])
    
    for idx, i in enumerate(cvf_j):
            if i - mean < std*10:
                nu_min.append(nus[idx-1])
                err_nu_min.append(err_nus[idx-1])
                break
    
    idx_vf +=1

print(f'nu_min: ({round((np.mean(nu_min))*1e-14,2)} ± {round((np.mean(err_nu_min))*1e-14,2)}) e14 Hz')
print(f'nu_min: ({(np.mean(nu_min))*1e-14} ± {(np.mean(err_nu_min))*1e-14}) e14 Hz')
    

    

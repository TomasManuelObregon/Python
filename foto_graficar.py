"""
@author: Tomás Obregón
"""
import matplotlib.pyplot as plt
import numpy as np
import glob 
import os

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

# files = sorted(glob.glob("*.txt"), key=os.path.getctime)
# archivo = files[-1]

plt.close("all")
plt.figure(figsize=[20,10])

while True:
    files = glob.glob("*.txt")
    archivo = files[-1]
    
    # color = wavelength_to_hex(float(archivo[10:13]))
    
    data = np.loadtxt(archivo, delimiter="\t")
    volt, corr = data[:,0],data[:,1]
    
    # plt.plot(volt, corr, c=color, marker=".")
    plt.plot(volt, corr, marker=".")
    plt.pause(2)        

plt.grid(linestyle=(0,(5, 3)), linewidth=1, alpha=.5)
plt.xlabel('Voltaje [V]', fontsize=25)
plt.ylabel('Corriente [A]', fontsize=25)
plt.show()

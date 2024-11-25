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

gauss = lambda x,x0,amp,sigma: amp * np.exp((-(x-x0)**2)/(2*(sigma**2))) 


#%%
path = os.path.expanduser("~/Desktop/Dia 4/espectro")
archivos = sorted(os.listdir(path))[1:-1]

wl = [float(i[:3]) for i in archivos]


peaks=[]
err_peaks=[]
err_sigmas=[]


plt.close('all')
plt.figure(figsize=[10,6])
plt.subplots_adjust(left=0.12,             # Posición del límite izquierdo
                    bottom=0.13,            # Posición del límite inferior
                    right=0.97,             # Posición del límite derecho
                    top=0.98)               # Posición del límite superior


for idx, i in enumerate(wl):
    data = np.loadtxt(path+'/'+archivos[idx], skiprows=53, max_rows=3648, delimiter=',')
    
    popt_g, pcov_g = op.curve_fit(gauss, data[:,0], data[:,1], p0=[i,.1,10])
    x0, amp, sigma = popt_g
    err_sigma = np.sqrt(pcov_g[2][2])
    
    peaks.append(x0)
    err_peaks.append(sigma)
    err_sigmas.append(err_sigma)
    # err_peak = np.sqrt(2 * np.log(2)) * sigma # FWHM
                      
    dom_g = np.linspace(x0 - 5*sigma, x0 + 5*sigma, 1000)
    im_g = gauss(dom_g, x0, amp, sigma) 
    
    peak = gauss(x0, x0, amp, sigma)
    
    volt = data[:,0]
    corr = data[:,1]
    
    # grafico - - - - - - - -- - - - - - - - - 
    plt.plot(volt, corr, label=f'{round(i)} nm', c=wavelength_to_hex(i), alpha=.3)
    
    plt.plot(dom_g, im_g, linestyle='--', linewidth=2.5, c=wavelength_to_hex(i), alpha=.6, zorder=0)
    
    plt.errorbar(x0, peak, xerr=abs(sigma), capsize=3.5,
                 c=wavelength_to_hex(i), marker='d')

    

plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.xlabel('Long. de onda [nm]', fontsize=25, fontproperties=font_prop)
plt.ylabel('Intensidad [u.a.]', fontsize=25, fontproperties=font_prop)
plt.legend(loc='upper right', prop={'size': 12, 'fname': font_path})

plt.yticks(fontsize=18)  
plt.xticks(fontsize=18, ticks=[400, 450, 500, 550, 600, 650, 700]) 
plt.xlim(401, 760) 
plt.ylim(-.03, 0.53) 

# plt.gca().set_facecolor('none')
# plt.gcf().patch.set_alpha(0)  
plt.show()
# plt.savefig('espectro.png', dpi=1000, bbox_inches='tight')



#%%
popt, pcov = op.curve_fit(lineal, wl, peaks, sigma=err_peaks)
m,b = popt
err_m = np.sqrt(pcov[0][0])
err_b = np.sqrt(pcov[1][1])

dom = np.linspace(min(wl), max(wl), 1000)
im  = lineal(dom,m,b)

plt.close('all')
plt.figure(figsize=[10,6])
plt.tick_params(colors=c_texto)           # Cambia el color de los ticks
plt.gca().xaxis.label.set_color(c_texto)  # Cambiar el color del texto de los ejes
plt.gca().yaxis.label.set_color(c_texto)
for spine in plt.gca().spines.values():
    spine.set_edgecolor(c_texto)          # Cambia el color del marco
    
for tick in plt.gca().get_xticklabels():    # Aplica la fuente deseada a los ticks
    tick.set_fontproperties(font_prop)
for tick in plt.gca().get_yticklabels():
    tick.set_fontproperties(font_prop)
plt.subplots_adjust(left=0.115,   # Posición del límite izquierdo
                    bottom=0.13,  # Posición del límite inferior
                    right=0.97,    # Posición del límite derecho
                    top=0.98)     # Posición del límite superior

for idx, i in enumerate(wl):
    plt.errorbar(i, peaks[idx], yerr=err_peaks[idx], capsize=3.5, linewidth=0, elinewidth=1.5,
                c=wavelength_to_hex(i), marker='d', label=f'{i} nm', zorder=2)
    
plt.plot(dom, im, linewidth=2.5, c='black', alpha=.5, label='Ajuste',zorder=0)
plt.plot(dom, lineal(dom, 1,0), linewidth=2.5, linestyle='--', c='black', alpha=.5, label='0 offset', zorder=0)
plt.text(425,660, f'Pendiente: {round(m,2)} ± {round(err_m,2)}\nOrdenada: ({round(b)} ± {round(err_b)}) nm', fontsize=18, color=c_texto)
    

plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.xlabel('Long. de onda enviada [nm]', fontsize=25, fontproperties=font_prop)
plt.ylabel('Long. de onda medida [nm]', fontsize=25, fontproperties=font_prop)
# plt.legend(loc='lower right', prop={'size': 16, 'fname': font_path})

plt.yticks(fontsize=20, ticks=[400, 450, 500, 550, 600, 650, 700]) 
plt.xticks(fontsize=20, ticks=[400, 450, 500, 550, 600, 650, 700])  
plt.xlim(401, 755) 
plt.ylim(401,755) 
 

# plt.gca().set_facecolor('none')
# plt.gcf().patch.set_alpha(0)  
plt.show()
plt.savefig('espectro_desfase.png', dpi=1000, bbox_inches='tight')

# np.savetxt('true_wl', [peaks, err_peaks])


#%%

plt.close('all')
plt.figure(figsize=[10,6])
plt.tick_params(colors=c_texto)           # Cambia el color de los ticks
plt.gca().xaxis.label.set_color(c_texto)  # Cambiar el color del texto de los ejes
plt.gca().yaxis.label.set_color(c_texto)
for spine in plt.gca().spines.values():
    spine.set_edgecolor(c_texto)          # Cambia el color del marco
    
for tick in plt.gca().get_xticklabels():    # Aplica la fuente deseada a los ticks
    tick.set_fontproperties(font_prop)
for tick in plt.gca().get_yticklabels():
    tick.set_fontproperties(font_prop)
plt.subplots_adjust(left=0.115,   # Posición del límite izquierdo
                    bottom=0.13,  # Posición del límite inferior
                    right=0.97,    # Posición del límite derecho
                    top=0.98)     # Posición del límite superior

for idx, i in enumerate(wl):
    plt.errorbar(i, err_peaks[idx], yerr=err_sigmas[idx], capsize=3.5, linewidth=0, elinewidth=1.5,
                c=wavelength_to_hex(i), marker='d', label=f'{i} nm', zorder=2)
        

plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.xlabel('Long. de onda enviada [nm]', fontsize=25, fontproperties=font_prop)
plt.ylabel('Error del pico [nm]', fontsize=25, fontproperties=font_prop)
plt.yticks(fontsize=20)  
plt.xticks(fontsize=20) 

plt.gca().set_facecolor('none')
plt.gcf().patch.set_alpha(0)  
plt.show()
# plt.savefig('espectro_error.png')





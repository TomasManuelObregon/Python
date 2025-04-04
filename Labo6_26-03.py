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
colores = ["#6D4C41", "#A0522D", "#D2691E", "#FF4500"]

# - - - -

lin = lambda x,m,b: x*m+b

def delete_txt(path):
    archivos = sorted(os.listdir(path))
    nuevos_archivos=[]
    for i in archivos:
        if not 'txt' in i.split(sep='.'):
            nuevos_archivos.append(i)
    return sorted(nuevos_archivos, key=lambda x: int("".join(c for c in x if c.isdigit())))

path = os.path.expanduser("~/Desktop/NewFolder1") 
archivos = delete_txt(path)



#%%
plt.close('all')
plt.figure(figsize=[10,6])
plt.subplots_adjust(left=0.09,   # Posición del límite izquierdo
                    bottom=0.13,  # Posición del límite inferior
                    right=0.97,    # Posición del límite derecho
                    top=0.95)     # Posición del límite superior

for idx, arc in enumerate(archivos[:4]):
    data = np.loadtxt(path+'/' + arc , delimiter=",", skiprows=2, usecols=(0, 1))
    plt.plot(data[1:,0]*1e-5, data[1:,1]/10 + idx * 6.6, c= colores[idx])
    
    # plt.text(data[-1,0]+10, idx*6.6 + 1.5, f'DutyCycle:\n{(idx+1)*25}%  ', fontsize=15, color=colores[idx])
    plt.text(1302.5*1e-5, idx * 6.6 + 1.5,  
         f'DutyCycle:\n{(idx+1)*25}%',  
         fontsize=15, color=colores[idx],  
         ha='center', va='center')
    
    plt.axhline(idx * 6.6, alpha=0.25, linestyle= '--', linewidth=3, c= colores[idx])
    plt.axhline(idx * 6.6 +3.3, alpha=0.25, linestyle= '--', linewidth=3, c= colores[idx])

plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.ylabel('Voltaje [V]', fontsize=25, fontproperties=font_prop)
plt.xlabel('Tiempo [s]', fontsize=25, fontproperties=font_prop)
plt.yticks([0, 3.3, 6.6, 9.9, 13.2, 16.5, 19.8, 23.1], [0, 3.3,0, 3.3,0, 3.3,0, 3.3,] ,fontsize=18)  
plt.xticks(fontsize=18)
plt.xlim(-50*1e-5,1450*1e-5)

plt.gca().set_facecolor('none')
plt.gcf().patch.set_alpha(0)  
plt.show()
# plt.savefig('/Users/tomas/Desktop/PWM.png', bbox_inches='tight')

#%%


plt.close('all')
plt.figure(figsize=[10,6])
plt.subplots_adjust(left=0.09,   # Posición del límite izquierdo
                    bottom=0.13,  # Posición del límite inferior
                    right=0.97,    # Posición del límite derecho
                    top=0.95)     # Posición del límite superior

valores_rectificados= []
valores_rectificados_std =[]

for idx, arc in enumerate(archivos[4:8]):
    PWM = np.loadtxt(path+'/' + arc , delimiter=",", skiprows=2, usecols=(0, 1))
    FILTRO = np.loadtxt(path+'/' + arc , delimiter=",", skiprows=2, usecols=(0, 2))
    
    plt.plot(PWM[1:,0]*5e-07,
              PWM[1:,1]/10 + idx * 6.6, c= colores[idx])
    
    plt.plot(FILTRO[1:,0]*5e-07,
             FILTRO[1:,1] + idx * 6.6, c= 'green')
    
    plt.text(1302.5 * 5e-7, idx * 6.6 + 2.5,  
         f'D-C:{(idx+1)*25}%',  
         fontsize=15, color=colores[idx],  
         ha='center', va='center')
    
    mean=np.mean(FILTRO[1:,1])
    std =np.std(FILTRO[1:,1])
   
    valores_rectificados.append(mean)
    valores_rectificados_std.append(std)
    
    plt.text(1302.5 * 5e-7, idx * 6.6 + 1,  
         f'Mean: {round(mean,2)} V',  
         fontsize=15, color='green',  
         ha='center', va='center')
    
    plt.axhline(idx * 6.6, alpha=0.25, linestyle= '--', linewidth=3, c= colores[idx])
    plt.axhline(idx * 6.6 +3.3, alpha=0.25, linestyle= '--', linewidth=3, c= colores[idx])

plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.ylabel('Voltaje [V]', fontsize=25, fontproperties=font_prop)
plt.xlabel('Tiempo [s]', fontsize=25, fontproperties=font_prop)
plt.yticks([0, 3.3, 6.6, 9.9, 13.2, 16.5, 19.8, 23.1], [0, 3.3,0, 3.3,0, 3.3,0, 3.3,] ,fontsize=18)  
plt.xticks(fontsize=18)  
plt.xlim(400*5e-07, 1450*5e-07)

plt.gca().set_facecolor('none')
plt.gcf().patch.set_alpha(0)  
plt.show()

# plt.savefig('/Users/tomas/Desktop/PWM_FILTRO.png', bbox_inches='tight')

#%% 
porcentajes = [(i+1)*25 for i in range(4)]

popt, pcov = op.curve_fit(lin, porcentajes, valores_rectificados, sigma=valores_rectificados_std)
m,b = popt
err_m = np.sqrt(pcov[0][0])
err_b = np.sqrt(pcov[1][1])

dom = np.linspace(0, max(porcentajes), 1000)
im  = lin(dom,m,b)


plt.close('all')
plt.figure(figsize=[10,4])
plt.subplots_adjust(left=0.09,   # Posición del límite izquierdo
                    bottom=0.18,  # Posición del límite inferior
                    right=0.97,    # Posición del límite derecho
                    top=0.95)     # Posición del límite superior

for idx, i in enumerate(valores_rectificados):
    plt.errorbar(porcentajes[idx], i, yerr= valores_rectificados_std[idx],
                  capsize=3.5, marker='.', elinewidth=2,
                  c= colores[idx], label=f'D-C: {(idx+1)*25}%' )
    
plt.plot(dom, im, linewidth=3, alpha=0.4, label='Ajuste', c='green')

plt.text(1, 2.75,  
     f'Pendiente: {round(m,4)} ± {round(err_m,4)} \nOrdenada al origen: {round(b,3)} ± {round(err_b,3)}',  
     fontsize=15, color='black',  
     ha='left', va='center')


plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.legend(loc='lower right', prop={'size': 16, 'fname': font_path})
plt.ylabel('Voltaje rectificado [V]', fontsize=25, fontproperties=font_prop)
plt.xlabel('Duty Cycle [%]', fontsize=25, fontproperties=font_prop)
plt.yticks(fontsize=18)  
plt.xticks(fontsize=18)  

plt.xlim(-10,110)
plt.ylim(-0.2,3.5)

plt.gca().set_facecolor('none')
plt.gcf().patch.set_alpha(0)  
plt.show()

plt.savefig('/Users/tomas/Desktop/DC_V_2.png', bbox_inches='tight')



"""
@author: tomas
"""
 
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import optimize as op

from matplotlib import font_manager
font_path = '/Users/tomas/ev/tw-cen-mt.ttf'  # Ruta completa al archivo de fuente
font_prop = font_manager.FontProperties(fname=font_path)

c_texto='#2F1D27'
c_enfasis='#783991'
c_enfasis2='#55B1BC'

lineal = lambda x,m,b: x*m + b


       
def error_df(x, y, xerr, yerr, N):
    
    dferr_array = []
    
    for i in range(1, len(y) - 1):
    
        f = y[i+1] - y[i-1]
        h = N * (x[i+1] - x[i-1])
        
        if h != 0:  # Evitar división por cero
            dferr = (N/2) * (yerr[i+1]/h + yerr[i-1]/h + (f * xerr[i+1]) / (h**2) + (f * xerr[i-1]) / (h**2))
            dferr_array.append(dferr)  # Agregar el error calculado al array
        else:
            dferr_array.append(float('nan'))  # Si hay división por cero, agregamos un NaN (Not a Number)
    
    return dferr_array
               


#%%
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# BOMBEO  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

bombeo = pd.read_csv('/Users/tomas/Desktop/pi_bombeo.csv')

bombeo['err_i'] = np.full(len(bombeo['corriente']), 0.01)
bombeo['err_pot'] = bombeo['potencia'] * .03

bombeo.rename(columns={"corriente": "i",
                      "potencia": "pot"}, inplace=True)


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
    
plt.subplots_adjust(left=0.1,   # Posición del límite izquierdo
                    bottom=0.13,  # Posición del límite inferior
                    right=0.97,    # Posición del límite derecho
                    top=0.99)     # Posición del límite superior

plt.errorbar(bombeo['i'], bombeo['pot']/1000, 
              xerr= bombeo['err_i'], yerr=bombeo['err_pot']/1000, 
              capsize=4, marker='.', markersize=10, elinewidth=1.5,
              linewidth=0, c=c_enfasis, label='Bombeo')

plt.plot(bombeo['i'], bombeo['pot']/1000, alpha=.7, linewidth=2, linestyle='--', c=c_enfasis)

plt.axvspan(0.65, 0.69, color=c_texto, alpha=0.3, linestyle='--', linewidth=2, zorder=0)
plt.text(.56, .12, 'Corriente umbral: (0.45 ± 0.25) A', fontsize=18, color=c_texto, rotation=90)


plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.xlabel('Corriente [A]', fontsize=25, fontproperties=font_prop)
plt.ylabel('Potencia [W]', fontsize=25, fontproperties=font_prop)
plt.legend(loc='lower right', prop={'size': 25, 'fname': font_path})

plt.yticks(fontsize=20, ticks=[0, .3, .6, .9, 1.2])  
plt.ylim(min(bombeo['pot'])-.1, max(bombeo['pot'])/1000+.1)

plt.xticks(fontsize=20, ticks=[0.05, .4, .8, 1.2, 1.6, 2]) 
plt.xlim(min(bombeo['i']) -.08, max(bombeo['i'])+.08) 

plt.gca().set_facecolor('none')
plt.gcf().patch.set_alpha(0)  
plt.show()

# plt.savefig('pi_bombeo.png')


#%%
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# CAV LINEAL  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

lin45 = pd.read_csv('/Users/tomas/Desktop/pi_lin_45mm.csv')

lin45['err_i'] = np.full(len(lin45['corriente']), 0.01)
lin45['err_pot'] = lin45['potencia'] * .03

lin45.rename(columns={"corriente": "i",
                      "potencia": "pot"}, inplace=True)


lin60 = pd.read_csv('/Users/tomas/Desktop/pi_lin_60mm.csv')

lin60['err_i'] = np.full(len(lin60['corriente']), 0.01)
lin60['err_pot'] = lin60['potencia'] * .03

lin60.rename(columns={"corriente": "i",
                      "potencia": "pot"}, inplace=True)

# # - - - - - - - - - - - - - - - - - -
# # AJUSTES 
popt_lin45, pcov_lin45 = op.curve_fit(lineal,  lin45['i'][29:], lin45['pot'][29:])
m_lin45 = popt_lin45[0]
b_lin45 = popt_lin45[1]
err_m_lin45 = np.sqrt(pcov_lin45[0][0]) 

dom_lin45 = np.linspace(min(lin45['i'][29:]), max(lin45['i'][29:]))
im_lin45  = lineal(dom_lin45, m_lin45, b_lin45) 

popt_lin60, pcov_lin60 = op.curve_fit(lineal,  lin60['i'][5:], lin60['pot'][5:])
m_lin60 = popt_lin60[0]
b_lin60 = popt_lin60[1]
err_m_lin60 = np.sqrt(pcov_lin60[0][0]) 

dom_lin60 = np.linspace(min(lin60['i'][5:]), max(lin60['i'][5:]))
im_lin60  = lineal(dom_lin60, m_lin60, b_lin60) 



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
    
plt.subplots_adjust(left=0.1,   # Posición del límite izquierdo
                    bottom=0.13,  # Posición del límite inferior
                    right=0.97,    # Posición del límite derecho
                    top=0.99)     # Posición del límite superior

plt.errorbar(lin45['i'][25:], lin45['pot'][25:], 
              xerr= lin45['err_i'][25:], yerr=lin45['err_pot'][25:], 
              capsize=4, marker='.', markersize=10, elinewidth=1.5,
              linewidth=0, c=c_enfasis, label='45 mm')

plt.plot(dom_lin45, im_lin45 , linewidth=2, linestyle='--', alpha=.7, c=c_enfasis, label='Ajuste - 45 mm')

plt.errorbar(lin60['i'], lin60['pot'], 
              xerr= lin60['err_i'], yerr=lin60['err_pot'], 
              capsize=4, marker='.', markersize=10, elinewidth=1.5,
              linewidth=0, c=c_enfasis2, label='60 mm')

plt.plot(dom_lin60, im_lin60 , linewidth=2, linestyle='--', alpha=.7, c=c_enfasis2, label='Ajuste - 60 mm')

# plt.plot(lin45['i'][25:], lin45['pot'][25:], alpha=.7, linewidth=2, linestyle='--', c=c_enfasis)
# plt.plot(lin60['i'], lin60['pot'], alpha=.7, linewidth=2, linestyle='--', c=c_enfasis2)

# plt.axvline(1.4, linestyle='--', alpha=.3, linewidth=2, c=c_texto)
plt.axvspan(1.39, 1.46, color=c_texto, alpha=0.3, linestyle='--', linewidth=2, zorder=0)
plt.text(1.41, 10, 'Corriente umbral: (1.42 ± 0.07) A', fontsize=18, color=c_texto, rotation=90)


plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.xlabel('Corriente [A]', fontsize=25, fontproperties=font_prop)
plt.ylabel('Potencia [mW]', fontsize=25, fontproperties=font_prop)
plt.legend(loc='lower right', prop={'size': 25, 'fname': font_path})

plt.yticks(fontsize=20, ticks=[0,15,30,45,60,75,90])  
plt.ylim(min(lin60['pot'])-8, max(lin45['pot'])+8) 

plt.xticks(fontsize=20, ticks=[1.25, 1.4, 1.6, 1.8, 2, 2.2, 2.38]) 
plt.xlim(1.2, 2.43)

plt.gca().set_facecolor('none')
plt.gcf().patch.set_alpha(0)  
plt.show()

# plt.savefig('pi_lin.png')


#%%
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PERFIL CAV LINEAL - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

perfil = pd.read_csv('/Users/tomas/Desktop/perfil_lineal.csv')

perfil['err_Potencia'] = perfil['Potencia'] * .03
perfil['err_Longitud'] = np.full(len(perfil['Longitud']), 0.025)

perfil.rename(columns={"Longitud": "dist",
                       "err_Longitud": "err_dist",
                       "Potencia": "pot", 
                       "err_Potencia": "err_pot"}, inplace=True)


# Encuentro los parametros que caracterizan el perfil de potencia
def sigmoid(x,a,b,c):
    return (a/(1 + np.exp((b-x)/c))) 

popt, pcov = op.curve_fit(sigmoid, perfil['dist'], perfil['pot'], p0=[80,6.5,.5])
a = popt[0]
b = popt[1]
c = popt[2]
err_a = np.sqrt(pcov[0][0])
err_b = np.sqrt(pcov[1][1])
err_c = np.sqrt(pcov[2][2])

dom = np.linspace(min(perfil['dist']), max(perfil['dist']), 1000)
im  = sigmoid(dom, a, b, c)

 
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
    
plt.subplots_adjust(left=0.1,   # Posición del límite izquierdo
                    bottom=0.13,  # Posición del límite inferior
                    right=0.97,    # Posición del límite derecho
                    top=0.99)     # Posición del límite superior


plt.errorbar(perfil['dist'][::3], perfil['pot'][::3], 
              xerr= perfil['err_dist'][::3], yerr=perfil['err_pot'][::3], alpha=.7,
              capsize=4, marker='.', markersize=10, linewidth=0, elinewidth=2, label='Potencia', c=c_enfasis)


plt.errorbar(perfil['dist'][:6], perfil['pot'][:6],
              xerr= perfil['err_dist'][:6], yerr=perfil['err_pot'][:6], alpha=.7,
              capsize=4, marker='.', markersize=10, linewidth=0, elinewidth=2, c=c_enfasis)


plt.errorbar(perfil['dist'][27:], perfil['pot'][27:], 
              xerr= perfil['err_dist'][27:], yerr=perfil['err_pot'][27:], alpha=.7,
              capsize=4, marker='.', markersize=10, linewidth=0, elinewidth=2, c=c_enfasis)

plt.plot(perfil['dist'], perfil['pot'], alpha=.7, linestyle='--', linewidth=2, c=c_enfasis)
# plt.plot(dom, im, alpha=.7, linestyle='--', linewidth=3, c=c_enfasis2, label='Ajuste')


plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.xlabel('Corrimiento [mm]', fontsize=25, fontproperties=font_prop)
plt.ylabel('Potencia [mW]', fontsize=25, fontproperties=font_prop)
plt.legend(loc='upper left', prop={'size': 25, 'fname': font_path})

plt.yticks(fontsize=20, ticks=[0,20,40,60,80])  
plt.xticks(fontsize=20, ticks=[i*2 for i in range(8)]) 
plt.xlim(min(perfil['dist'])-.7, max(perfil['dist'])+.7)
plt.ylim(min(perfil['pot'])-5, max(perfil['pot'])+5) 

plt.gca().set_facecolor('none')
plt.gcf().patch.set_alpha(0)  
plt.show()

plt.savefig('perfil_lineal.png')

#%%
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PERFIL REAL - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# def gaussiana(x,a,b,c):
#     e = np.exp((b-x)/c)
#     y = e/(2*e + e**2 + 1)
#     return (a*y)/c

def gaussiana(x, a,b,c):
    return a * np.exp(-((x - b) ** 2) / (2 * c ** 2))

dom_g2 = np.linspace(min(perfil['dist']), max(perfil['dist']), 1000)
im_g2 = gaussiana(dom_g2, a, b, c)


dfdx = np.gradient(perfil['pot'], perfil['dist'])

# err_dfdx = error_df(x, y, xerr, yerr, N)
err_dfdx = error_df(perfil['dist'], perfil['pot'], perfil['err_dist'], perfil['err_pot'], len(perfil['pot']))


popt_g, pcov_g = op.curve_fit(gaussiana, perfil['dist'][1:-1], dfdx[1:-1])#, sigma= err_dfdx, absolute_sigma=True)
a_g, b_g, c_g = popt_g
err_c_g = np.sqrt(pcov_g[2][2])

fwhm = np.sqrt(2 * np.log(2)) * c_g

dom_g = np.linspace(min(perfil['dist']), max(perfil['dist']), 1000)
im_g  = gaussiana(dom_g, a_g, b_g, c_g)


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
    
plt.subplots_adjust(left=0.1,   # Posición del límite izquierdo
                    bottom=0.13,  # Posición del límite inferior
                    right=0.97,    # Posición del límite derecho
                    top=0.99)     # Posición del límite superior


# plt.plot(dom_g2, im_g2, alpha=.7, linestyle='--', linewidth=3, c=c_enfasis2, label=r'$\partial$ del ajuste')

plt.plot(dom_g, im_g, alpha=.7, linestyle='--', linewidth=3, c=c_enfasis2, label=r'Ajuste', zorder=0)
plt.errorbar(perfil['dist'][1:-1], dfdx[1:-1], 
              yerr= err_dfdx, xerr=perfil['err_dist'][1:-1], 
              capsize=4, marker='.', markersize=10, linewidth=0, elinewidth=2,
              alpha=.5, label=r'$\partial$ discreta', c=c_enfasis, zorder=0)

# plt.plot(perfil['dist'], dfdx, alpha=.4, linestyle='--', linewidth=2, c=c_enfasis)

plt.text(b_g + fwhm + .12, 0, 'FWHM', fontsize=20, color=c_texto, alpha=.7)

plt.axvline(b_g - fwhm, ymin=0, ymax=.1, color=c_texto, alpha=0.5, linewidth=4, zorder=0)
plt.axvline(b_g + fwhm, ymin=0, ymax=.1, color=c_texto, alpha=0.5, linewidth=4, zorder=0)





plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.xlabel('Corrimiento [mm]', fontsize=25, fontproperties=font_prop)
plt.ylabel(r'Intensidad $\left[mW/mm\right]$', fontsize=25, fontproperties=font_prop)
plt.legend(loc='upper left', prop={'size': 25, 'fname': font_path})

plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.xlim(3.5,9.5)
plt.ylim(-5,max(dfdx)+15)

plt.gca().set_facecolor('none')
plt.gcf().patch.set_alpha(0)  
plt.show()
plt.show()


# plt.savefig('perfil_lineal_derivada.png')




#%%
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# CAV V - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

cavv = pd.read_csv('/Users/tomas/Desktop/pi_v.csv')

cavv['err_i'] = np.full(len(cavv['corriente']), 0.01)
cavv['err_pot'] = cavv['potencia'] * .03

cavv.rename(columns={"corriente": "i",
                      "potencia": "pot"}, inplace=True)

popt_cavv, pcov_cavv = op.curve_fit(lineal,  cavv['i'][5:], cavv['pot'][5:])
m_cavv = popt_cavv[0]
b_cavv = popt_cavv[1]
err_m_cavv = np.sqrt(pcov_cavv[0][0]) 

dom_cavv = np.linspace(min(cavv['i'][6:]), max(cavv['i'][6:]))
im_cavv  = lineal(dom_cavv, m_cavv, b_cavv)
                  
                  
                  
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
    
plt.subplots_adjust(left=0.1,   # Posición del límite izquierdo
                    bottom=0.13,  # Posición del límite inferior
                    right=0.97,    # Posición del límite derecho
                    top=0.99)     # Posición del límite superior


# plt.errorbar(cavv['i'][6:], cavv['pot'][6:], alpha=.7,
#               xerr= cavv['err_i'][6:], yerr=cavv['err_pot'][6:], 
#               capsize=4, marker='.', markersize=10, elinewidth=1.5,
#               linewidth=0, c=c_enfasis, label='Cav. en "V"')

plt.plot(dom_cavv, im_cavv , linewidth=2, linestyle='--', alpha=.7, c=c_enfasis, label='Ajuste')


plt.errorbar(cavv['i'], cavv['pot'], 
              xerr= cavv['err_i'], yerr=cavv['err_pot'], 
              capsize=4, marker='.', markersize=10, elinewidth=1.5,
              linewidth=0, c=c_enfasis, label='Cav. en "V"')

# plt.plot(cavv['i'], cavv['pot'], alpha=.7, linewidth=2, linestyle='--', c=c_enfasis)

plt.axvspan(.99, 1.06, color=c_texto, alpha=0.3, linestyle='--', linewidth=2, zorder=0)
plt.text(.92, 8, 'Corriente umbral: (1.03 ± 0.04) A', fontsize=18, color=c_texto, rotation=90)


plt.grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
plt.xlabel('Corriente [A]', fontsize=25, fontproperties=font_prop)
plt.ylabel('Potencia [mW]', fontsize=25, fontproperties=font_prop)
plt.legend(loc='lower right', prop={'size': 25, 'fname': font_path})

plt.yticks(fontsize=20, ticks=[0,20,40,60,80])  
plt.ylim(min(cavv['pot'])-5, max(cavv['pot'])+5) 

plt.xticks(fontsize=20, ticks=[.8, 1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.38]) 
plt.xlim(.8-.08, 2.38+.08)

plt.gca().set_facecolor('none')
plt.gcf().patch.set_alpha(0)  
plt.show()

# plt.savefig('pi_ajuste_cavv.png')












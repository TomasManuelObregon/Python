"""
@author: tomas obregon
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import optimize as op

plt.close('all')

#%% DEFINO COSAS QUE SE VAN A USAR DESPUES
# - - - - - - - Def colores - - - - - - - - - - - -
colores = ['#F6F07D', '#FBA20F', '#DC5337', '#B83856', '#66176D', '#160A37']
 

# - - - - - - - Def etiquetas - - - - - - - - - - - 
labels = ["81.4 mm K", "123.1 mm K", "164 mm J", "211.9 mm J", "249.6 mm J", "410.5 mm J"]


# - - - - - - - Def error de cada term. - - - - - - 
ruido = np.loadtxt('/Users/tomas/Desktop/ruido.txt')
err = [np.std(ruido[:80, 0]), np.std(ruido[:80, 1]), np.std(ruido[:80, 2]),
       np.std(ruido[:80, 3]), np.std(ruido[:80, 4]), np.std(ruido[:80, 5])]

# Grafico la medicion con todo apagado para medir el ruido
# plt.close('all')
plt.figure(figsize=[10,5.5], facecolor='none')
plt.xlabel('Tiempo [s]', fontsize=18)
plt.ylabel('Temperatura [°C]', fontsize=18) 
plt.xticks(fontsize=18)  
plt.yticks(fontsize=18) 
plt.grid(linestyle='--')

plt.scatter(ruido[:80,-1], ruido[:80, 0], c='#F6F07D', marker='.', label="81.4 mm K")
plt.scatter(ruido[:80,-1], ruido[:80, 1], c='#FBA20F', marker='.', label="123.1 mm K")
plt.scatter(ruido[:80,-1], ruido[:80,2], c='#DC5337', marker='.', label="164 mm J")
plt.scatter(ruido[:80,-1], ruido[:80,3], c='#B83856', marker='.', label="211.9 mm J")
plt.scatter(ruido[:80,-1], ruido[:80,4], c='#66176D', marker='.', label="249.6 mm J")
plt.scatter(ruido[:80,-1], ruido[:80,5], c='#160A37', marker='.', label="410.5 mm J")

plt.legend(fontsize=18, loc='center right')
plt.savefig('/Users/tomas/Desktop/Ruido.png', format='png', dpi=100)


#%% DEFINO FUCNIONES
# Como los datos tienen tendencia defino una función para sacarla y quedarme solo con la oscilacion
def sacar_tendencia(term):
    df[f'MM{term}'] = df[f'T{term}'].rolling(window=78, center=True).mean().shift(39)
    df[f'osc{term}'] = df[f'T{term}'] - df[f'MM{term}']

# Ajustes - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def lin(x, m, b):
    return m*x + b

def exp(x, a, b, c):
    return a * np.exp(b*x) + c

def cos(t, a, f, phi, c):
    return a * np.cos((2*np.pi*f)*t + phi) + c

def ajuste(X, Y, err_Y, color, label, p0):
    X = X[78:].to_numpy()[:,0]
    Y = Y[78:].to_numpy()[:,0]
    err_Y = np.full(len(X), err_Y)

    bounds = ([0, 0, -2*np.pi, -np.inf], [np.inf, np.inf, 2*np.pi, np.inf])
    popt, pcov = op.curve_fit(cos, X, Y,
                              p0=p0, bounds=bounds,
                              absolute_sigma=True, sigma=err_Y)
    
    a   = popt[0]
    f   = popt[1]
    phi = popt[2]    
    c   = popt[3]
    err_a   = np.sqrt(pcov[0][0])
    err_phi = np.sqrt(pcov[2][2])
    
    dom = np.linspace(min(X), max(X), 1000)
    im  = cos(dom, a, f, phi, c)
    
    
    plt.figure(figsize=[10,3.5], facecolor='none')
    plt.xlabel('Tiempo [h]', fontsize=18)
    plt.ylabel('Temperatura [°C]', fontsize=18)
    plt.xticks(fontsize=18)  
    plt.yticks(fontsize=18) 
    plt.grid(linestyle='--')
        
    plt.errorbar(X/3600, Y*100, yerr=err_Y,
                 linewidth=0, marker='.',
                 elinewidth=2, capsize=3,
                 color=color, label=label, zorder=0)

    plt.plot(dom/3600, im*100, color='#B83856', label='Ajuste')

    plt.legend(fontsize=18, loc='upper right')
    
    plt.savefig(f'{label}.png', format='png', dpi=100)

    return a, f, phi, err_a, err_phi


    
#%% PROCESO LOS DATOS
# importo los datos (descarto las primeras 3500 mediciones)
df = pd.read_csv('/Users/tomas/Desktop/medicion_13-6.txt', 
                   names=['T1', 'T2', 'T3', 'T4', 'T5','T6', 't'],
                   delimiter=' ').drop(range(3500), axis=0)


# Le quito la tendencia a la oscilacion - - - - - -  
for i in range(1,7):
    sacar_tendencia(i)

# Grafico los datos sin tendencia - - - - - - - - -  
#plt.close('all')
plt.figure(figsize=[10,5.5], facecolor='none')
plt.xlabel('Tiempo [h]', fontsize=18)
plt.ylabel('Temperatura [°C]', fontsize=18)
plt.xticks(fontsize=18)  
plt.yticks(fontsize=18) 
plt.grid(linestyle='--')

for i in range(1,7):
    plt.plot(df[['t']]/3600, df[[f'T{i}']], linewidth=2.5, c=colores[i-1], label=labels[i-1])
    
plt.axvline(df.at[3500, 't']/3600, linestyle='--', c='black')
# Agregar texto rotado
plt.text(2.5, 69, 'Estacionario', color='black', 
          ha='center', va='center', fontsize=18, bbox=dict(facecolor='none', edgecolor='none'))
plt.legend(fontsize=16, loc='lower center')

plt.savefig('/Users/tomas/Desktop/serie.png', format='png', dpi=100)


#%% ANALISIS DE LOS DATOS
A = []
F = []
PHI_unwrapped = []
err_A   = []
err_PHI = []

# Defino un array de amplitudes para poder poner el p0 eficientemente
amps_p0 = [4.6, 2.6, 1.5, 0.8, 0.5, 1]

#plt.close('all')
for i in range(1,7):
  a, f, phi, err_a, err_phi = ajuste(df[['t']], df[[f'osc{i}']], err[i-1],
                                            colores[i-1], labels[i-1], [amps_p0[i-1], .006 ,0, 0])
  
  A.append(a)
  err_A.append(err_a)
  F.append(f)
  PHI_unwrapped.append(phi)
  err_PHI.append(err_phi)

# paso de frecuencia a w
W_mean = np.mean(F)*2*np.pi
W_std  = np.std(F)*2*np.pi

#%%
distancias = [81.4, 123.1, 164, 211.9, 249.6, 410]

# hay un dato de PHI que esta desfazado 2pi asi que lo resto para que respete la recta
PHI = np.array(PHI_unwrapped) - np.array([0,0,0,0,0, 5*np.pi/2])


# #plt.close('all')
# plt.figure(figsize=[10,5])
# plt.xlabel('Distancias [mm]', fontsize=15)
# plt.ylabel('Desfasaje [rad]', fontsize=15) 
# plt.grid(linestyle='--')

# plt.errorbar(distancias, PHI, yerr= np.full(len(distancias), err_PHI),
#               c=colores[3], marker='.',
#               linewidth=0, elinewidth=2, capsize=5)
# plt.axhline(-2*np.pi)

# #plt.close('all')
# plt.figure(figsize=[10,5])
# plt.xlabel('Distancias [mm]', fontsize=15)
# plt.ylabel('Amplitud de oscilación [°C]', fontsize=15) 
# plt.grid(linestyle='--')

# plt.errorbar(distancias, A, yerr= np.full(len(distancias), err_A),
#              c=colores[3], marker='.',
#              linewidth=0, elinewidth=2, capsize=5)


#%%
# AJUSTE DEL DESFASAJE - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
popt_lin, pcov_lin = op.curve_fit(lin, distancias, PHI, sigma=err_PHI, absolute_sigma=True)
m_lin = popt_lin[0]
b_lin = popt_lin[1]
err_m_lin = np.sqrt(pcov_lin[0][0])

dom_lin = np.linspace(min(distancias), max(distancias), 1000)
im_lin  = lin(dom_lin, m_lin, b_lin)

#plt.close('all')
plt.figure(figsize=[10,5.5],facecolor='none')
plt.xlabel('Distancias [mm]', fontsize=18)
plt.ylabel('Desfasaje [rad]', fontsize=18) 
plt.xticks(fontsize=18)  
plt.yticks(fontsize=18) 
plt.grid(linestyle='--')

plt.errorbar(distancias, PHI, yerr= np.full(len(distancias), err_PHI),
             c=colores[3], marker='.', label='Datos',
             linewidth=0, elinewidth=2, capsize=5)
plt.plot(dom_lin, im_lin, c=colores[0], linewidth=2.5, label='Ajuste', zorder=0)

plt.legend(fontsize=20, loc='upper right')

ldp_lin = (-1/m_lin)
err_ldp_lin = (err_m_lin/(m_lin**2))

print(f'L.D.P. lineal: ({round(ldp_lin)} ± {round(err_ldp_lin)}) mm')
print(f'L.D.P. lineal: ({ldp_lin} ± {err_ldp_lin}) mm')
plt.savefig('phi(d).png', format='png', dpi=100)


# AJUSTE DE LA AMPLITUD - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
popt_exp, pcov_exp = op.curve_fit(exp, distancias, A, 
                                  sigma=err_A, absolute_sigma=True,
                                  p0=[1, -0.02, 0])
a_exp = popt_exp[0]
b_exp = popt_exp[1]
c_exp = popt_exp[2]
err_b_exp = np.sqrt(pcov_exp[1][1])

dom_exp = np.linspace(min(distancias), max(distancias), 1000)
im_exp  = exp(dom_exp, a_exp, b_exp, c_exp)



plt.grid(linestyle='--')
plt.figure(figsize=[10, 5.5], facecolor='none')
plt.xlabel('Distancias [mm]', fontsize=18)
plt.ylabel('Amplitud de oscilación [°C]', fontsize=18)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.grid(linestyle='--')

plt.errorbar(distancias, A, yerr= np.full(len(distancias), err_A),
             c=colores[3], marker='.', label='Datos',
             linewidth=0, elinewidth=2, capsize=5)
plt.plot(dom_exp, im_exp, c=colores[0], linewidth=2.5, label='Ajuste', zorder=0)

plt.legend(fontsize=20, loc='upper right')
plt.savefig('amp(d).png', format='png', dpi=100)

ldp_exp = (-1/b_exp)
err_ldp_exp = (err_b_exp/(b_exp**2))

print(f'L.D.P. exponencial: ({round(ldp_exp)} ± {round(err_ldp_exp)}) mm')
print(f'L.D.P. exponencial: ({ldp_exp} ± {err_ldp_exp}) mm')


#%% 
'''
TEORIA:
    lpd: sqrt(2 k/ w) --->
   
    k = (lpd^2 * w)/2 
    
    err_k = np.sqrt(sigma_lpd**2 + sigma_w**2)
'''

def k(ldp, err_ldp):
    k     = (ldp**2 * W_mean)/2
    err_k = np.sqrt((ldp * W_mean * err_ldp)**2 + ((ldp**2 * W_std)/2)**2)
    
    print(f'k: ({round(k,1)} ± {round(err_k,1)}) mm^2/s')
    print(f'k: ({k} ± {err_k}) mm^2/s')
    


k(ldp_lin, err_ldp_lin)
k(ldp_exp, err_ldp_exp)




#%% GRAFICO TODA LA SERIE PARA EL POSTER

# df_todo = pd.read_csv('/Users/tomas/Desktop/mediciones_feas.txt', 
#                       names=['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 't'],
#                       delimiter=' ')

# labels_lol = ['10 cm', '20 cm', '30 cm', '40 cm', '50 cm', '60 cm', '70 cm', '80 cm', '90 cm']

# # Eliminar las primeras 400 filas
# df_todo = df_todo.iloc[400:]

# # Crear los colores a partir del colormap inferno
# colormap = plt.cm.inferno
# normalize = plt.Normalize(vmin=1, vmax=9)  # Ajustar para tener en cuenta los 9 colores
# colors = [colormap(normalize(i)) for i in range(10, 0, -1)]  # Invertir el orden de los colores

# # Graficar los datos
# plt.figure(figsize=[10, 5.5], facecolor='none')
# plt.xlabel('Tiempo [h]', fontsize=18)
# plt.ylabel('Temperatura [°C]', fontsize=18)
# plt.xticks(fontsize=18)
# plt.yticks(fontsize=18)
# plt.grid(linestyle='--')

# for i in range(1, 10):
#     plt.plot(df_todo[['t']] / 3600, df_todo[[f'T{i}']], linewidth=2.5, color=colors[i-1], label=f'{labels_lol[i-1]}')

# plt.legend(fontsize=16, loc='center right')
# plt.savefig('lol.png', format='png', dpi=100)
# plt.show()

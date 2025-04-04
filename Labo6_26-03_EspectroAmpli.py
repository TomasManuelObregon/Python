import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os
import pandas as pd

font_path = '/Users/tomas/ev/tw-cen-mt.ttf'          # Ruta completa al archivo de fuente
font_prop = font_manager.FontProperties(fname=font_path)

path = os.path.expanduser("~/Desktop/NewFolder1")    # Ruta a la carpeta de los datos

c_texto='#2D2A21'
colores = ["#6D4C41", "#A0522D", "#D2691E", "#FF4500", 'green'][::-1]

# - - - - - - - - - - - - - - - - - - - - 
def delete_txt(path):
    archivos = sorted(os.listdir(path))
    nuevos_archivos=[]
    nuevos_archivos_txt=[]
    
    for i in archivos:
        if not 'txt' in i.split(sep='.'):
            nuevos_archivos.append(i)
        elif 'txt' in i.split(sep='.'):
            nuevos_archivos_txt.append(i)
           
    nuevos_archivos= sorted(nuevos_archivos, key=lambda x: int("".join(c for c in x if c.isdigit())))
    nuevos_archivos_txt=sorted(nuevos_archivos_txt, key=lambda x: int("".join(c for c in x if c.isdigit())))
           
    return nuevos_archivos, nuevos_archivos_txt

def calcular_FFT(time, signal, time_scale):

    N  = len(signal)

    freq = np.fft.fftfreq(N, time_scale)
    fft  = np.fft.fft(signal)

    # Nos quedamos solo con la mitad positiva
    freq = freq[np.where(freq >= 0)] 
    fft  = np.abs(fft[np.where(freq >= 0)]) * 2 / N  # Normalización de amplitud

    return freq, fft


archivos, archivos_txt  = delete_txt(path)
archivos, archivos_txt = archivos[8:13][::-1]  , archivos_txt[8:13][::-1]  # Seleccionar archivos e invertir el orden 


#%%
plt.close('all')
fig, axs = plt.subplots(len(archivos), 2, figsize=(12, 10))
fig.subplots_adjust(left=0.06,
                   right=0.97,
                   bottom=0.08,
                   top=0.99,
                   hspace=0.25,
                   wspace=0.19)

for idx in range(len(archivos)):
    data = np.loadtxt(path+'/' + archivos[idx] , delimiter=",", skiprows=2, usecols=(0, 1))     # Señal 
    siganl_md = pd.read_csv(path+'/' + archivos_txt[idx], sep=":", header=None).set_index(0).T  # Macro Data

    time_scale = float(siganl_md["Time Scale"].iloc[0].replace("s", "").strip())                # Escala temporal

    # Amp. Output
    time = data[:, 0] * time_scale                      # Ajuste de tiempo con escala correcta
    signal  = (data[:, 1] - np.mean(data[:, 1]))*1000   # Señal centrada en mV
    
    freq, fft = calcular_FFT(time, signal, time_scale)
    freq =freq/1000 #kHz

    # Signal
    axs[idx, 0].plot(time, signal, c=colores[idx])

    axs[idx, 0].grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
    axs[idx, 0].set_yticks([-5,np.mean(signal), 5])  
    # axs[idx, 0].tick_params(axis='y', fontsize=15) 
    
    # Spectre
    axs[idx, 1].plot(freq, fft, c=colores[idx])
    axs[idx, 1].grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
    
    
    
    if idx ==2:
        axs[idx, 0].set_ylabel('Ruido de la salida del amp. [mV]', fontsize=25, fontproperties=font_prop)
        axs[idx, 1].set_ylabel('Amplitud', fontsize=25, fontproperties=font_prop)
        
    if idx ==4:
        axs[idx, 0].set_xlabel('Tiempo [s]', fontsize=25, fontproperties=font_prop)
        axs[idx, 1].set_xlabel('Frecuencia [kHz]', fontsize=25, fontproperties=font_prop)
    
    
plt.gca().set_facecolor('none')
plt.gcf().patch.set_alpha(0)  
plt.show()

plt.savefig('/Users/tomas/Desktop/señales_y_espectros.png', bbox_inches='tight')    
        
        
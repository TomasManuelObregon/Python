"""
@author: tomas
"""
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

c_texto='#2D2A21'
colores = ["green", "#6D4C41", "#A0522D", "#D2691E", "#FF4500"]

# - - - - - - - - - - - - - - - - - - - - 
def delete_txt(path):
    archivos = sorted(os.listdir(path))
    nuevos_archivos=[]
    
    for i in archivos:
        if not 'txt' in i.split(sep='.'):
            if i != '.DS_Store':
                nuevos_archivos.append(i)

    return sorted(nuevos_archivos, key=lambda x: int("".join(c for c in x if c.isdigit())))
           

# - - - - - - - - - - - - - - - - - - - - 
def calcular_FFT(time, signal, time_scale):

    N  = len(signal)

    freq = np.fft.fftfreq(N, time_scale)
    fft  = np.fft.fft(signal)

    # Nos quedamos solo con la mitad positiva
    freq = freq[np.where(freq >= 0)] 
    fft  = np.abs(fft[np.where(freq >= 0)]) * 2 / N  # Normalización de amplitud

    return freq, fft



path = os.path.expanduser("~/Desktop/AC") 
archivos = delete_txt(path)

archivos_x = archivos[0:5]
archivos_y = archivos[5:10]
archivos_z = archivos[10:15]


def graficar(archivo):
    fig, axs = plt.subplots(len(archivo), 3, figsize=(12, 10))
    fig.subplots_adjust(left=0.07,
                       right=0.98,
                       bottom=0.08,
                       top=0.9,
                       hspace=0.3,
                       wspace=0.29)
    
    for idx in range(len(archivo)):
        data = np.loadtxt(path+'/' + archivo[idx] , delimiter=",", skiprows=2, usecols=(1))
        data = (data - np.mean(data))*1000 # centro la señal
        time_data = np.loadtxt(path+'/' + archivo[idx] , delimiter=",", skiprows=1, max_rows=1, usecols=(2,3))
        time = np.arange(time_data[0], time_data[0] + time_data[1]*len(data), time_data[1]) 
    
        freq, fft = calcular_FFT(time, data, time_data[1])
        freq =freq/1000 #kHz
    
        # Signal
        axs[idx, 0].plot(time, data, c=colores[idx])
    
        axs[idx, 0].grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
        axs[idx, 0].set_yticks([-5,np.mean(data), 5])  
        
        # Spectre
        axs[idx, 1].plot(freq/1000, fft, c=colores[idx])
        axs[idx, 1].axvline(1, linestyle='--', alpha=.6, c='r')
        axs[idx, 1].grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
        
        # Zoom Spectre
        axs[idx, 2].plot(freq, fft, c=colores[idx])
        axs[idx, 2].grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
        axs[idx, 2].axvline(1000, linestyle='--', alpha=.6, c='r')
        axs[idx, 2].set_xlim([0,1100])
    
        
        fig.text(0.02, 0.5, 'Ruido de la salida del amp. [mV]', va='center', rotation='vertical', fontsize=20)
        fig.text(0.34, 0.5, 'Amplitud [mV]',                    va='center', rotation='vertical', fontsize=20)
           
        if idx ==len(archivo):
            axs[idx, 0].set_xlabel('Tiempo [s]', fontsize=20)
            axs[idx, 1].set_xlabel('Frecuencia [kHz]', fontsize=20)
            axs[idx, 2].set_xlabel('Frecuencia [Hz]', fontsize=20)
    
        
    plt.show()

graficar(archivos_x)
graficar(archivos_y)
graficar(archivos_z)

# #%%
# plt.close('all')
# fig, axs = plt.subplots(len(archivos), 3, figsize=(12, 10))
# fig.subplots_adjust(left=0.06,
#                    right=0.97,
#                    bottom=0.08,
#                    top=0.99,
#                    hspace=0.25,
#                    wspace=0.26)

# for idx in range(len(archivos)):
#     data = np.loadtxt(path+'/' + archivos[idx] , delimiter=",", skiprows=2, usecols=(0, 2))     # Señal 
#     siganl_md = pd.read_csv(path+'/' + archivos_txt[idx], sep=":", header=None).set_index(0).T  # Macro Data

#     time_scale = float(siganl_md["Time Scale"].iloc[0].replace("s", "").strip())                # Escala temporal

#     # Amp. Output
#     time = data[:, 0] * time_scale                      # Ajuste de tiempo con escala correcta
#     signal  = (data[:, 1] - np.mean(data[:, 1]))*1000   # Señal centrada en mV
    
#     freq, fft = calcular_FFT(time, signal, time_scale)
#     freq =freq/1000 #kHz

#     # Signal
#     axs[idx, 0].plot(time, signal, c=colores[idx])

#     axs[idx, 0].grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
#     axs[idx, 0].set_yticks([-5,np.mean(signal), 5])  
#     # axs[idx, 0].tick_params(axis='y', fontsize=15) 
    
#     # Spectre
#     axs[idx, 1].plot(freq, fft, c=colores[idx])
#     axs[idx, 1].axvline(1, linestyle='--', alpha=.6, c='r')
#     axs[idx, 1].grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
#     axs[idx, 1].set_xlim([0,10])
    
#     # Zoom Spectre
#     axs[idx, 2].plot(freq*1000, fft, c=colores[idx])
#     axs[idx, 2].grid(linestyle=(0,(5, 3)), linewidth=1, c=c_texto, alpha=.25)
#     axs[idx, 2].axvline(1000, linestyle='--', alpha=.6, c='r')
#     axs[idx, 2].set_xlim([0,1100])
    
    
    
#     if idx ==2:
#         axs[idx, 0].set_ylabel('Ruido de la salida del amp. [mV]', fontsize=25)
#         axs[idx, 1].set_ylabel('Amplitud [mV]', fontsize=25)
        
#     if idx ==4:
#         axs[idx, 0].set_xlabel('Tiempo [s]', fontsize=25)
#         axs[idx, 1].set_xlabel('Frecuencia [kHz]', fontsize=25)
#         axs[idx, 2].set_xlabel('Frecuencia [Hz]', fontsize=25)
        
    
    
# # plt.gca().set_facecolor('none')
# # plt.gcf().patch.set_alpha(0)  
# plt.show()

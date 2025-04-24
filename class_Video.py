"""
@author: Tomás Obregón
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize as op
from scipy.signal import fftconvolve
import cv2
import os
import time

# Modelo de ajuste 
def true_gaussian(dom, amp, ux, uy, a, b, c, offs):
    x,y = dom
    return amp * np.exp(a*((x-ux)**2) + b*(x-ux)*(y-uy) + c*((y-uy)**2)) + offs



class Video:
    def __init__(self, path, channel):
        self.path = path
        self.channel = channel
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        
    def create_video(self, ti, tf):
        self.ti, self.tf = ti, tf
        
        # Configuración del video
        cap = cv2.VideoCapture(self.path)
        fps = cap.get(cv2.CAP_PROP_FPS)                          # Frames por segundo
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))    # Número total de frames
    
        # Calcular el frame inicial y final
        start_frame = int(ti * fps)
        end_frame = int(tf * fps)
    
        # Asegurarse de que los frames estén dentro del rango del video
        start_frame = min(max(0, start_frame), total_frames - 1)
        end_frame = min(max(0, end_frame), total_frames - 1)
    
        # Leer frames desde start_frame hasta end_frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
        # Lista donde guardaremos los frames en escala de grises del canal azul
        frames = []
         
        for frame_num in range(start_frame, end_frame + 1):
            ret, frame = cap.read()
            if not ret:
                break
            # Extraer el canal azul
            if self.channel == 'b':
                blue_channel = frame[:, :, 0]    # El 1er canal (índice 0) es el azul en OpenCV
                frames.append(blue_channel)
            elif self.channel == 'g':
                green_channel = frame[:, :, 1]   # El 2er canal (índice 1) es el verde en OpenCV
                frames.append(green_channel)
            elif self.channel == 'r':
                red_channel = frame[:, :, 2]     # El 3er canal (índice 2) es el rojo en OpenCV
                frames.append(red_channel)
            elif self.channel == 'all':    
                frames.append(frame)       # Todos los canales
    
        # Convertir la lista de frames en un array de NumPy
        self.frames = np.array(frames)
        self.fps = fps       
        
        # Liberar el video
        cap.release()
        
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        
    def average(self):
        acumulado = np.zeros(self.frames[0].shape)
        for i in self.frames:
            acumulado = acumulado + i    
            
        self.mean_frame = (acumulado/len(self.frames)) - np.mean(acumulado/len(self.frames))
        
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def show_average_frame(self):
        if not hasattr(self, 'mean_frame'):
            self.average()      
            
        plt.figure(figsize=(10,5))
        plt.imshow(self.mean_frame)
        
        plt.xlabel('$\hat{x}$', fontsize=15)
        plt.ylabel('$\hat{y}$', fontsize=15)
        plt.tight_layout()
        plt.show()
        
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def show_frames(self):
        index = 0
        paused = False
    
        while True:
            if not paused:
                frame = self.frames[index]
                cv2.imshow('Video', frame)
                key = cv2.waitKey(int(1000 / self.fps)) & 0xFF
            else:
                key = cv2.waitKey(0) & 0xFF  # Espera indefinida en pausa
    
            if key == ord('q'):
                break
            elif key == ord('p'):
                paused = not paused  # Pausar o reanudar
            elif key == ord(','):  # '<' retrocede 10
                index = max(0, index - 10)
            elif key == ord('.'):  # '>' avanza 10
                index = min(len(self.frames) - 1, index + 10)
            elif not paused:
                index += 1
    
            # Repetir si llega al final
            if index >= len(self.frames):
                index = 0
    
        cv2.destroyAllWindows()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
    def create_background(self, ti_bg, tf_bg):
        self.ti_bg, self.tf_bg = ti_bg, tf_bg
        
        self.create_video(ti_bg, tf_bg)
        self.average()
        self.background = self.mean_frame

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def autocorr(self, mask, plot):
        self.mask=mask
        
        # Autocorrelacion
        self.corr = fftconvolve(self.background, self.mean_frame[::-1, ::-1], mode='same')
        
        # Maximos
        self.y_max, self.x_max = np.unravel_index(np.argmax(self.corr), self.corr.shape)
        
        
        # Coordenadas X e Y
        x = np.arange(0, self.corr.shape[1])
        y = np.arange(0, self.corr.shape[0])
        X, Y = np.meshgrid(x, y)
        
        # Mascara
        self.x_mask = X[self.y_max-mask:self.y_max+mask+1, self.x_max-mask:self.x_max+mask+1] 
        self.y_mask = Y[self.y_max-mask:self.y_max+mask+1, self.x_max-mask:self.x_max+mask+1] 
        self.z_mask = self.corr[self.y_max-mask:self.y_max+mask+1, self.x_max-mask:self.x_max+mask+1] 
            
        if plot:
            plt.close('all')
            # Definir figura con gridspec
            fig = plt.figure(figsize=(10, 5))
            gs = fig.add_gridspec(2, 2, width_ratios=[2, 1])  # gráfico izquierdo más ancho
            
            # Gráfico IZQUIERDO - ocupa dos filas
            ax1 = fig.add_subplot(gs[:, 0], projection='3d')
            ax1.plot_surface(self.x_mask, self.y_mask, self.z_mask, color='r', linewidth=0, antialiased=True, alpha=.8)
            
            ax1.set_xlabel('$\hat{x}$ [px]')
            ax1.set_ylabel('$\hat{y}$ [px]')
            ax1.set_zticks([])
            ax1.tick_params(axis='both', labelsize=10)
            ax1.set_box_aspect([self.corr.shape[1]/self.corr.shape[0], 1, 1])
            ax1.view_init(40, -75)
            
            # Gráfico SUPERIOR DERECHO
            ax2 = fig.add_subplot(gs[0, 1], projection='3d')
            ax2.plot_surface(X, Y, self.corr, cmap='viridis', linewidth=0, antialiased=False, alpha=.15)
            ax2.plot_surface(self.x_mask, self.y_mask, self.z_mask, color='r', linewidth=0, antialiased=False)
            
            ax2.set_xlabel('$\hat{x}$ [px]')
            ax2.set_ylabel('$\hat{y}$ [px]')
            ax2.set_zticks([])
            ax2.tick_params(axis='both', labelsize=10)
            ax2.set_box_aspect([self.corr.shape[1]/self.corr.shape[0], 1, 1])
            ax2.view_init(40, -75)
            
            # Gráfico INFERIOR DERECHO
            ax3 = fig.add_subplot(gs[1, 1], projection='3d')
            ax3.plot_surface(X, Y, self.corr, cmap='viridis', linewidth=0, antialiased=False, alpha=.15)
            ax3.plot_surface(self.x_mask, self.y_mask, self.z_mask, color='r', linewidth=0, antialiased=False)
            
            ax3.set_xticks([])
            ax3.set_yticks([])
            ax3.set_zticks([])
            ax3.tick_params(axis='both', labelsize=10)
            ax3.set_box_aspect([self.corr.shape[1]/self.corr.shape[0], 1, 1])
            ax3.view_init(90, -90)
            
            plt.tight_layout()
            plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
            plt.show()
                   
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def fit(self, plot=True):
        x_flat = self.x_mask.ravel()
        y_flat = self.y_mask.ravel()
        z_flat = self.z_mask.ravel()

        # creo el meshgrid
        x_dense = np.linspace(min(x_flat), max(x_flat), 100)
        y_dense = np.linspace(min(y_flat), max(y_flat), 100)
        x_dense, y_dense = np.meshgrid(x_dense, y_dense)
        
        p0  = [np.max(self.corr)-np.min(self.corr), self.x_max, self.y_max, 0,0,0, np.max(self.corr)]         
        popt, pcov = op.curve_fit(true_gaussian, (x_flat, y_flat), z_flat, p0=p0, maxfev=10000)
        self.ux = popt[1]
        self.uy = popt[2] 
        self.err_ux = np.sqrt(pcov[1,1])
        self.err_uy = np.sqrt(pcov[2,2])

        z_dense = true_gaussian((x_dense, y_dense), *popt)
        
        # Residuos
        z_dense_para_residuos =  true_gaussian((self.x_mask, self.y_mask), *popt)
        res = self.z_mask - z_dense_para_residuos

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # Grafico - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        if plot:
            plt.close('all')
            fig = plt.figure(figsize=(8, 8))
            text = f'Segmento:\n{self.ti} s - {self.tf} s'
            fig.text(0.5, 0.5, text, ha='center', va='center', fontsize=16, weight='bold', color='black')


            # AX1 - - - - 
            ax1 = fig.add_subplot(2,2,1, projection='3d')

            # Rojo
            ax1.plot_surface(self.x_mask, self.y_mask, self.z_mask, color='r', alpha=.3)
            ax1.errorbar([self.x_max], [self.y_max], [max(z_flat)], xerr=2, yerr=2,
                          capsize=3, elinewidth=1, marker='x', color='red', markersize=5)

            # Verde
            ax1.errorbar([self.ux], [self.uy], [np.max(z_dense)], xerr=self.err_ux, yerr=self.err_uy,
                          capsize=3, elinewidth=1, marker='x', color='g', markersize=5)
            ax1.plot_surface(x_dense, y_dense, z_dense, color='g', alpha=.3)


            ax1.set_xlabel('$\hat{x}$ [px]')
            ax1.set_ylabel('$\hat{y}$ [px]')
            ax1.set_zticks([])
            ax1.set_box_aspect([self.z_mask.shape[1]/self.z_mask.shape[0], 1, 1])
            ax1.view_init(90, -90)


            # AX2 - - - - 
            ax2 = fig.add_subplot(2,2,2, projection='3d')

            # Rojo
            ax2.plot_surface(self.x_mask, self.y_mask, self.z_mask, color='r', alpha=.3)
            ax2.errorbar([self.x_max], [self.y_max], [max(z_flat)], xerr=2,
                          capsize=3, elinewidth=1, marker='x', color='red', markersize=5)

            # Verde
            ax2.errorbar([self.ux], [self.uy], [np.max(z_dense)], xerr=self.err_ux, 
                          capsize=3, elinewidth=1, marker='x', color='g', markersize=5)
            ax2.plot_surface(x_dense, y_dense, z_dense, color='g', alpha=.3)

            ax2.set_xlabel('$\hat{x}$ [px]')
            ax2.set_zlabel('Intensidad')
            ax2.set_yticks([])
            ax2.set_box_aspect([self.z_mask.shape[1]/self.z_mask.shape[0], 1, 1])
            ax2.view_init(0, -90)


            # AX3 - - - - 
            ax3 = fig.add_subplot(2,2,3, projection='3d')

            # Rojo
            ax3.plot_surface(self.x_mask, self.y_mask, self.z_mask, color='r', alpha=.3)
            ax3.errorbar([self.x_max], [self.y_max], [max(z_flat)], yerr=2,
                          capsize=3, elinewidth=1, marker='x', color='red', markersize=5)

            # Verde
            ax3.errorbar([self.ux], [self.uy], [np.max(z_dense)], yerr=self.err_uy,
                          capsize=3, elinewidth=1, marker='x', color='g', markersize=5)
            ax3.plot_surface(x_dense, y_dense, z_dense, color='g', alpha=.3)

            ax3.set_zlabel('Intensidad')
            ax3.set_ylabel('$\hat{y}$ [px]')
            ax3.set_xticks([])
            ax3.set_box_aspect([self.z_mask.shape[1]/self.z_mask.shape[0], 1, 1])
            ax3.view_init(0,0)

            # AX4 - - - - 
            ax4 = fig.add_subplot(2,2,4, projection='3d')
            ax4.plot_surface(self.x_mask, self.y_mask, res/1e5, color='g', alpha=.3)

            ax4.set_zlabel('Residuos (1e5)')
            ax4.set_ylabel('$\hat{y}$ [px]')
            ax4.set_xlabel('$\hat{x}$ [px]')
            ax4.set_box_aspect([self.z_mask.shape[1]/self.z_mask.shape[0], 1, 1])
            ax4.view_init(10, -10)

            plt.tight_layout()
            plt.show()
            
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        
    def hysteresis(self, iterations):
        ti = self.tf_bg + 1
        tf = ti + 3
        
        # Centro
        y0, x0 = 1080//2, 1920//2
   
        
        mov_x = [0]
        mov_y = [0] 
        err_mov_x = [0]
        err_mov_y = [0] 
        
        for i in range(iterations):
            video.create_video(ti, tf)  
            video.average()
            video.autocorr(5, False)
            video.fit(False)
            
            dx = abs(self.ux - x0)
            dy = abs(self.uy - y0)
            
            mov_x.append(dx)
            mov_y.append(dy)
            err_mov_x.append(self.err_ux)
            err_mov_y.append(self.err_uy)
            
            ti = tf + 1
            tf = ti + 3
                
        duty_cycle_ida = [round(i*0.05, 2)*100 for i in range(len(mov_x)//2)]          # Ida
        duty_cycle_vuelta = [round(i*0.05, 2)*100 for i in range(len(mov_x)//2)][::-1] # Vuelta
        
        
        plt.close('all')
        fig = plt.figure(figsize=(8, 8))

        # AX1 - - - - 
        ax1 = fig.add_subplot(2,1,1)

        ax1.errorbar(duty_cycle_ida, mov_x[:len(mov_x)//2], yerr=err_mov_x[:len(mov_x)//2],
                     capsize = 3, elinewidth=2, linewidth=0, marker='.', markersize=5, 
                     c="#A0522D", label='Ida')
        ax1.errorbar(duty_cycle_vuelta, mov_x[len(mov_x)//2:], yerr=err_mov_x[len(mov_x)//2:],
                     capsize = 3, elinewidth=2, linewidth=0, marker='.', markersize=5, 
                     c="#FF4500", label='Vuelta')   

        ax1.grid(linestyle=(0,(5, 3)), linewidth=1, alpha=.25)
        ax1.set_ylabel(r'Desplazamiento en $\hat{x}$', fontsize=15)
        ax1.set_xlabel('Duty Cycle [%]', fontsize=15)
        ax1.set_xticks([0, 25, 50, 75, 100])
        ax1.set_yticks(np.arange(0,501,100))
        ax1.tick_params(axis='both', labelsize=18)
        ax1.legend(fontsize=15, loc='lower right')

        # AX2 - - - - 
        ax2 = fig.add_subplot(2,1,2)

        ax2.errorbar(duty_cycle_ida, mov_y[:len(mov_x)//2], yerr=err_mov_y[:len(mov_x)//2],
                     capsize = 3, elinewidth=2, linewidth=0, marker='.', markersize=5, 
                     c="#A0522D", label='Ida')
        ax2.errorbar(duty_cycle_vuelta, mov_y[len(mov_x)//2:], yerr=err_mov_y[len(mov_x)//2:],
                     capsize = 3, elinewidth=2, linewidth=0, marker='.', markersize=5, 
                     c="#FF4500", label='Vuelta')   

        ax2.grid(linestyle=(0,(5, 3)), linewidth=1, alpha=.25)
        ax2.set_ylabel(r'Desplazamiento en $\hat{y}$', fontsize=15)
        ax2.set_xlabel('Duty Cycle [%]', fontsize=15)
        ax2.set_xticks([0, 25, 50, 75, 100])
        ax2.set_yticks(np.arange(0,7,2))
        ax2.tick_params(axis='both', labelsize=18)
        ax2.legend(fontsize=15, loc='lower right')
        
        self.hyst = [mov_x, mov_y, err_mov_x, err_mov_y]
        
        
        
        
        
#%%
file_name = 'WIN_20250407_13_29_49_Pro.mp4'
path = os.path.expanduser("~/Downloads/"+file_name)

video = Video(path, 'b')
video.create_background(1,4)

video.hysteresis(39)
    
"""
@author: tomas obregon
"""

#%% - - - - - - - Importo - - - - - - - - - - - - - -
# Instrumentalizacion
import pyvisa as visa
import time
from datetime import datetime

# Data analysis
import numpy as np
# import matplotlib.pyplot as plt
#from scipy import optimize as op

def cambiar_long(x):
    time.sleep(0.5)    
    lock.setVoltAux(3,x)
    time.sleep(0.5)      
    
    i=1
    while i<=3:
        lock.setVoltAux(2,5)
        time.sleep(.1)
        lock.setVoltAux(2,0)
        time.sleep(.1) 
        lock.setVoltAux(2,5)
        time.sleep(.1) 
        lock.setVoltAux(2,0)
        time.sleep(.1) 
        lock.setVoltAux(2,5)
        time.sleep(.1)
        lock.setVoltAux(2,0)
        time.sleep(.1) 
        lock.setVoltAux(2,5)
        time.sleep(.1) 
        lock.setVoltAux(2,0)
        
        i+=1
    time.sleep(1)
    
fromvtolam = lambda x: round(62.418181816551126 * x + 417.59090909661654)

#%% - - - - - - - Clase Lock-In - - - - - - - - - - - -
class SR830:
    '''Clase para el manejo amplificador Lockin SR830 usando PyVISA de interfaz'''

    def __init__(self, config):

        self._lockin = visa.ResourceManager().open_resource(config['lockin_addr'])
        print(self._lockin.query('*IDN?'))

        #Configuración inicial del Lock In

        #Modo de medición
        self.setModo(config['medicion_modo'])

        #Display del panel frontal
        self.setDisplay(config['display_modo'])

        #Sensibilidad
        self.setSensibility(config['sens'])

        #Slope del filtro
        self.setFilterSlope(config['slope'])

        #Tiempo de integración del filtro
        self.setIntegrationTime(config['t_int'])

        #Referencia
        self.setModoReferencia(config['ref_intern'])
     

    def __del__(self):
        self._lockin.close()

    def setModo(self, modo):
        '''Selecciona el modo de medición, 0=A, 1=A-B, 2=I, 3=I(10M)'''
        self._lockin.write(f"ISRC {modo}")

    def setSensibility(self, sens):
        '''Setea la sensibilidad'''
        self._lockin.write(f"SENS {sens}")

    def setFilterSlope(self, slope):
        '''Setea la pendiente del filtro pasabajos. 3=24dB/oct '''
        self._lockin.write(f"OFSL {slope}")
        
    def setIntegrationTime(self, tbase):
        '''Setea el tiempo de integración del filtro'''
        #Página 90 (5-4) del manual
        self._lockin.write(f"OFLT {tbase}")

    def setModoReferencia(self, isIntern):
        in_out = isIntern[0]
        '''Setea si la referencia a usar es interna (True) o externa (False)'''
        self._lockin.write(f"FMOD {int(in_out)}")

        if in_out==True:
            def setFreqReferencia(self, freq):
                freq=isIntern[1]
                '''Setea la frecuencia de la referencia interna, en Hz'''
                self._lockin.write(f"FREQ {freq}")
        
            def setVoltReferencia(self, vRef):
                vRef=isIntern[2]
                '''Setea el voltaje RMS de la referencia interna, en V'''
                self._lockin.write(f"SLVL {vRef}")
            
            
    def setVoltAux(self, Aux=1 ,vOut=0):
        '''Setea el voltaje RMS de la referencia interna, en V'''
        self._lockin.write(f"AUXV {Aux}, {vOut}")

    def setDisplay(self, displaymode):
        '''
        Setea el display del panel frontal del Lock-In:
            -'XY': modo X-Y
            -'RT': modo R-Theta
            -Para otros modos, ver el manual.
         '''
        if displaymode=='XY':
            self._lockin.write('DDEF 1, 0') #Canal 1, x
            self._lockin.write('DDEF 2, 0') #Canal 2, y
        elif displaymode=='RT':
            self._lockin.write('DDEF 1,1') #Canal 1, R
            self._lockin.write('DDEF 2,1') #Canal 2, Theta
        else:
            print('No entendí lo que querés ver en el display')

    def getDisplay(self):
        '''Obtiene la medición que acusa el display.'''

        return self._lockin.query_ascii_values('SNAP? 10, 11', separator=",")

    def getMedicion(self, measurement_mode):
        '''
        Obtiene los valores medidos según measurement_mode:
            -'XY': Valores XY
            -'RT': Valores RT
            -Para otros valores, ver el manual. Es posible obtener
            hasta 6 valores simultáneamente.
        '''
        if measurement_mode=='XY':
            return self._lockin.query_ascii_values('SNAP? 1, 2', separator=',')
        elif measurement_mode=='RT':
            return self._lockin.query_ascii_values('SNAP? 3, 4', separator=',')
        else:
            print('No entendí lo que querés medir')

    def getIntegrationTime(self):

        i = int(self._lockin.query('OFLT?'))

        #Lo siguiente convierte a tiempo el parámetro i de la sección 5-6
        if i % 2 == 0:
            t_int = 1 * 10**(i/2-5)
        else:
            t_int = 3 * 10**((i-1)/2 - 5)

        return t_int



#%% - - - - - - - Identifico los aparatos - - - - - - - - - - - -

rm = visa.ResourceManager()
print(rm.list_resources())

gen  = rm.open_resource('USB0::0x0699::0x0346::C034165::INSTR')

 
#%%
# - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - CODIGO PARA EL GENERADOR  - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - -

gen.write('SOUR1:FUNC:SHAP SQU')  # Señal cuadrada
gen.write('SOUR1:VOLT 10')        # Cambiar voltaje
gen.write('SOUR1:FREQ 280')       # Cambiar frecuencia
gen.write('VOLT:OFFS 0')          # Cambiar el offset

# - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - CODIGO PARA EL LOCK-IN  - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - - - - - -
if __name__ == '__main__':
    config = {
          'lockin_addr': 'GPIB0::8::INSTR',
          'medicion_modo': 2,
          'display_modo': 'RT',
          'sens': 19,
          'slope': 3,
          't_int' : 8,
          'ref_intern' : [False],
          }
    lock =  SR830(config)

#%%
v_lambda = list(np.arange(0,5.1,.3))
v_lambda.append(5)
for n in v_lambda:
    print(f"Lambda: {round(fromvtolam(n))}")
    t0 = time.time()
    cambiar_long(n)
    
    barrido_volts = np.linspace(-8,8,150)
    

    fecha_formato = datetime.now().strftime("%d_%m_%Y_%Hh_%Mm_%Ss")
    url = f'corr_volt_{fromvtolam(n)}_{fecha_formato}.txt'
    
    with open(url, 'w') as archivo:
        pass  # El archivo se crea vacío sin agregar contenido
    
    volt=[]
    corr=[]
    
    for i in barrido_volts:
        lock.setVoltAux(1,i)    
        time.sleep(.5)
        
        volt.append(i)
        corr.append(lock.getMedicion('RT')[0])

        with open(url, 'a') as archivo:
            archivo.write(f"{i}\t{lock.getMedicion('RT')[0]}\n")
      
    # np.savetxt(f"corr_volt_{fromvtolam(i)}_{fecha_formato}.txt", [volts,corr])
    
    tf = time.time()
    print("Tardó:", round(tf-t0), "s")






# plt.close('all')
# plt.figure(figsize=[10,6])
    
# plt.subplots_adjust(left=0.1,   # Posición del límite izquierdo
#                     bottom=0.13,  # Posición del límite inferior
#                     right=0.97,    # Posición del límite derecho
#                     top=0.95)     # Posición del límite superior

     
# plt.scatter(volts, corr, marker=".")

# plt.grid(linestyle=(0,(5, 3)), linewidth=1, alpha=.25)
# plt.xlabel('Voltaje [V]', fontsize=25)
# plt.ylabel('Corriente [A]', fontsize=25)
# plt.show()


#%%






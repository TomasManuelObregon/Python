"""
@author: tomas
"""
from machine import Pin, PWM
from time import sleep,time
from esp32 import PCNT
import Newton_Raphson as NR

max_duty = 2**16 - 1

class Desplazador:
    """
    Clase para controlar un desplazador en 3 ejes (X, Y, Z) usando una ESP32.
    Permite generar PWM en los ejes, centrar posiciones, medir con contador
    de pulsos y realizar barridos automáticos en XY.
    """

    def __init__(self, pin_x=33, pin_y=32, pin_z=25, pin_counter=27):
        """
        Inicializa el desplazador configurando los pines de PWM y el contador.

        Parámetros:
            pin_x (int): pin de salida PWM para el eje X.
            pin_y (int): pin de salida PWM para el eje Y.
            pin_z (int): pin de salida PWM para el eje Z.
            pin_counter (int): pin de entrada para el contador de pulsos.
        """
        self.pwm_x = PWM(Pin(pin_x), freq=1221)
        self.pwm_y = PWM(Pin(pin_y), freq=1221)
        self.pwm_z = PWM(Pin(pin_z), freq=1221)
        self.counter = PCNT(0, pin=Pin(pin_counter), rising=PCNT.INCREMENT)   

    def x(self, dc_x):
        """
        Configura el duty cycle del eje X.

        Parámetros:
            dc_x (float): valor entre 0 y 1 correspondiente al duty cycle.
        """
        if dc_x <= 1 and dc_x >=0:
            self.pwm_x.duty_u16(int(dc_x * max_duty/100))
        else:
            print('El duty cycle debe estar entre 0 y 1')

    def y(self, dc_y):
        """
        Configura el duty cycle del eje Y.

        Parámetros:
            dc_y (float): valor entre 0 y 1 correspondiente al duty cycle.
        """
        if dc_y <= 1 and dc_y >=0:
            self.pwm_y.duty_u16(int(dc_y * max_duty/100))
        else:
            print('El duty cycle debe estar entre 0 y 1')
            
    def z(self, dc_z):
        """
        Configura el duty cycle del eje Z.

        Parámetros:
            dc_z (float): valor entre 0 y 1 correspondiente al duty cycle.
        """
        if dc_z <= 1 and dc_z >=0:
            self.pwm_z.duty_u16(int(dc_z * max_duty/100))
        else:
            print('El duty cycle debe estar entre 0 y 1')
        
    def centro(self, in_z=True):
        """
        Centra el desplazador en los ejes X e Y.
        Si in_z=False, también centra el eje Z.

        Parámetros:
            in_z (bool): si es True, centra los 3 ejes; por defecto solo X e Y.
        """
        if in_z:
            self.x(.5)
            self.y(.5)
            self.z(.5)
        else:
            self.x(.5)
            self.y(.5)


    def medir(self, t_int, count):
        """
        Realiza una medición con el contador de pulsos.

        Parámetros:
            t_int (float): tiempo de integración en segundos.
            count (list): lista donde se agrega el valor medido.

        Nota:
            El contador se reinicia después de la medición.
        """
        sleep(.1)
        self.counter.start()
        sleep(t_int)
        count.append(self.counter.value())
        self.counter.stop()
        self.counter.value(0)
 

    def barrer(self, param, t_int, t_slp, count):
        """
        Realiza un barrido automático en los ejes X e Y usando desplazamientos
        calculados con Newton_Raphson.desplazamientos(). Comienza desde la esquina
        inferior izquierda. Para (50%, 50%) corresponden, aproximadamente, los
        valores (4 um, -3.3 um) de desplazamiento. 

        Parámetros:
            param (tuple): self.dcx_inicial (%), self.dcy_inicial (%), self.dcx_final (%), self.dcy_final (%), y paso (um).
            t_int (float): tiempo de integración para cada medición.
            t_slp (float): tiempo de espera entre pasos.
            count (list) : lista donde se almacenan las mediciones.
        """
        print('Calculando los duty cycles...')
        inicio = time()  
        self.dcx, self.dcy, cant_pasos_x = NR.desplazamientos(*param)

        fin = time()
        print(f'Listo! Tardó {fin-inicio} s')
                         
        j = 0
        for i in range(len(self.dcx)):
            if j < cant_pasos_x:
                self.x(self.dcx[i])
                self.y(self.dcy[i])
                sleep(t_slp)
                self.medir(t_int, count)

                j+=1
                
            elif j == cant_pasos_x:
                self.x(0)
                sleep(t_slp)

                self.x(self.dcx[i])
                self.y(self.dcy[i])
                sleep(t_slp)
                self.medir(t_int, count)

                j=0
                
        print('Conteo:')
        print(count)

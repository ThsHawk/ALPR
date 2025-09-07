from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo
import time

class ServoController:
    def __init__(self, pin_number):
        """
        Inicializa o controlador do servo.
        
        Args:
            pin_number (int): O número do pino GPIO ao qual o fio de sinal do servo está conectado.
        """
        # Configura o servo. Os valores de min/max_pulse_width podem ser ajustados
        # para o seu modelo de servo específico, se necessário.
        self.servo = Servo(pin_number, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=PiGPIOFactory())
        self.servo.value = None  # Inicia com o sinal desativado

    def move_to_position(self, value):
        """
        Move o servo para uma posição específica.
        
        Args:
            value (float): Um valor entre -1.0 (posição mínima) e 1.0 (posição máxima).
        """
        # O método value é mais flexível para posições intermediárias
        self.servo.value = value
        time.sleep(0.5) # Pequena pausa para o servo se mover

    def open_gate(self):
        """
        Move o servo para a posição que "abre" a cancela.
        """
        print("Abrindo cancela...")
        self.servo.max()
        time.sleep(1.5)

    def close_gate(self):
        """
        Move o servo para a posição que "fecha" a cancela.
        """
        print("Fechando cancela...")
        self.servo.min()
        time.sleep(1.5)

    def relax(self):
        """
        Desativa o sinal do servo para economizar energia.
        """
        print("Desativando sinal do servo...")
        self.servo.value = None

    def cleanup(self):
        """
        Limpa os recursos do GPIO.
        """
        self.servo.close()
        print("Recursos do servo liberados.")
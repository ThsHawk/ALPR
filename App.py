import time
import sys
import cv2
import pprint
from Alpr import Alpr
from DatabaseHandler import DatabaseHandler
from PiCam import PiCam
from ServoControler import ServoController
from TFTDisplay import TFTDisplay

class App:
    def __init__(self):
        # Inicializa o banco de dados local
        self.db = DatabaseHandler()
        # Inicializa a camera
        self.cam = PiCam(process_interval=2.0)
        if not self.cam.is_running: exit()
        #
        self.plate = None
        # Inicializa o Servo
        self.gate = ServoController(18)
        # Inicializa o display TFT
        self.display = TFTDisplay()

    def frameProcess(self):
        # Pega o frame mais recente do stream de vídeo
        frame = self.cam.get_latest_frame()
        process = Alpr(frame)
        plateFrame = None
        # Verifica se é hora de processar
        if self.cam.should_process():
            print("Procurando uma placa...")
            self.display.show_message("Procurando uma placa...")
            plateFrame = process.search_plate()
        
        if plateFrame is not None:
            print("Processando possível placa...")
            self.display.show_message("Processando possível placa...")
            return process.recognize(plateFrame)


if __name__ == "__main__":
    app = App()
    app.display.show_message(">> Inicio do Programa! <<")
    while True:
        plate = app.frameProcess()
        if plate is not None:
            print("Placa encontrada: " + plate)
            app.display.show_message("Placa encontrada: " + plate)
            with app.db as db:
                db.create_tables()
                isRegistered, description = db.is_plate_registered(plate)
                if isRegistered:
                    #
                    print("Acesso liberado para: " + description)
                    app.display.show_message("Acesso liberado para: " + description)
                    app.gate.open_gate()
                    time.sleep(1)
                    time.sleep(3)
                    app.gate.close_gate()
                    time.sleep(1)
                    app.gate.relax()


                else:
                    print("Acesso negado, placa não identificada no registro!")
                    app.display.show_message("Acesso negado, placa não identificada no registro!")


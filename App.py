import time
import sys
import cv2
import pprint
from Alpr import Alpr
from DatabaseHandler import DatabaseHandler
from PiCam import PiCam
from ServoControler import ServoController

#if len(sys.argv) < 2 :
#    print("Err: no path.")
#    exit()

class App:
    def __init__(self): 
        self.db = DatabaseHandler()
        
        #
        self.cam = PiCam(process_interval=2.0)
        if not self.cam.is_running: exit()
        #
        self.plate = None
        #
        self.gate = ServoController(18)

    def frameProcess(self):

        # Pega o frame mais recente do stream de vídeo
        frame = self.cam.get_latest_frame()
        #if frame is None: break
        
        # Verifica se é hora de processar
        if self.cam.should_process():
            print("Processando um novo frame...")
            inst = Alpr(frame)
            return inst.recognize()

             

    # Pressionar 'q' para sair
    #if cv2.waitKey(1) & 0xFF == ord('q'): break


if __name__ == "__main__":
    app = App()
    while True:
        plate = app.frameProcess()
        if plate is not None:
            print("Placa encontrada: " + plate)
            with app.db as db:
                isRegistered, description = db.is_plate_registered(plate)
                if isRegistered:
                    #
                    print("Acesso liberado para: " + description)
                    app.gate.open_gate()
                    time.sleep(1)
                    time.sleep(3)
                    app.gate.close_gate()
                    time.sleep(1)
                    app.gate.relax()


                else:
                    print("Acesso negado, placa não identificada no registro!")
                    print("")
        #else:
            #print("Placa não encontrada")

                

    #


    # Limpeza
    #cam.release_camera()


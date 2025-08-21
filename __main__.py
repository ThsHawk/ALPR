import time
import sys
import cv2
import pprint
from Alpr import Alpr
from PiCam import PiCam

if len(sys.argv) < 2 :
    print("Err: no path.")
    exit()

cam = PiCam(process_interval=2.0)
if not cam.is_running():
    exit()

while cam.is_running:
    # Pega o frame mais recente do stream de vídeo
    frame = cam.get_latest_frame()
    if frame is None:
        break
    
    # Verifica se é hora de processar
    if cam.should_process():
        print("Processando um novo frame...")

        inst = Alpr(frame)
        text = inst.recognize()
        pprint.pprint(text)

    # Pressionar 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Limpeza
cam.release_camera()




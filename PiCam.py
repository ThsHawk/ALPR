import cv2
from picamera2 import Picamera2
import time

class PiCam:
    def __init__(self, process_interval=2.0):
        """
        Inicializa o processador de câmera usando a biblioteca picamera2.
        
        Args:
            process_interval (float): Intervalo de tempo (em segundos) entre cada processamento de imagem.
        """
        self.picam2 = Picamera2()
        self.process_interval = process_interval
        self.last_capture_time = time.time()
        self.is_running = True

        # Configura a câmera para usar o modo de vídeo
        config = self.picam2.create_preview_configuration(main={"size": (640, 480)})
        self.picam2.configure(config)
        self.picam2.start()

    def get_latest_frame(self):
        """
        Lê e retorna o último frame do stream de vídeo como um array NumPy.
        A picamera2 retorna o frame em formato BGR, pronto para o OpenCV.
        """
        # Captura o frame como um array NumPy
        frame = self.picam2.capture_array()
        
        if frame is None:
            return None
        
        # A picamera2 captura em formato RGB por padrão. O OpenCV usa BGR.
        # Precisamos converter.
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        return frame

    def should_process(self):
        """Verifica se é hora de processar um novo frame."""
        current_time = time.time()
        if current_time - self.last_capture_time >= self.process_interval:
            self.last_capture_time = current_time
            return True
        return False
    
    def release_camera(self):
        """Para a câmera e fecha as janelas."""
        self.picam2.stop()
        cv2.destroyAllWindows()
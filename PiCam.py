import cv2
import time

class PiCam:
    def __init__(self, camera_index=0, process_interval=2.0):
        """
        Inicializa o processador de câmera.
        
        Args:
            camera_index (int): Índice da câmera a ser usada (0 é a padrão).
            process_interval (float): Intervalo de tempo (em segundos) entre cada processamento de imagem.
        """
        self.camera_index = camera_index
        self.process_interval = process_interval
        self.cap = cv2.VideoCapture(self.camera_index)
        self.last_capture_time = time.time()
        self.is_running = True

        if not self.cap.isOpened():
            print("Erro: Não foi possível abrir a câmera. Verifique a conexão e as configurações.")
            self.is_running = False

    def get_latest_frame(self):
        """Lê e retorna o último frame do stream de vídeo."""
        ret, frame = self.cap.read()
        if not ret:
            print("Erro: Não foi possível ler o frame.")
            return None
        return frame

    def should_process(self):
        """Verifica se é hora de processar um novo frame."""
        current_time = time.time()
        if current_time - self.last_capture_time >= self.process_interval:
            self.last_capture_time = current_time
            return True
        return False
    
    def release_camera(self):
        """Libera o objeto da câmera e fecha as janelas."""
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
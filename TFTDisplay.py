# Arquivo: tft_display.py
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7735
from PIL import ImageFont, Image

class TFTDisplay:
    def __init__(self, width=160, height=128):
        # A maioria dos displays 1.8" tem 128x160
        self.width = width
        self.height = height
        
        # Conecta ao display via SPI
        # Estes são os pinos padrão, mas verifique o seu display
        self.serial = spi(port=0, device=0, gpio_DC=27, gpio_RST=17)
        self.device = st7735(self.serial, active_low=False, rotate=0, width=self.width, height=self.height)
        
        # Carrega uma fonte para o texto
        try:
            self.font = ImageFont.truetype("DejaVuSansMono.ttf", 10)
        except IOError:
            self.font = ImageFont.load_default()

    def show_message(self, line1, line2=""):
        with canvas(self.device) as draw:
            # Limpa o display
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")
            
            # Desenha o texto nas coordenadas (x, y)
            draw.text((10, 50), line1, fill="white", font=self.font)
            draw.text((10, 70), line2, fill="white", font=self.font)

    def clear(self):
        self.device.clear()
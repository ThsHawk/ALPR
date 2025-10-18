from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7735
from PIL import ImageFont, Image
from collections import deque

class TFTDisplay:
    def __init__(self, width=160, height=128):
        # Dimensões do Display (ajuste conforme o seu hardware)
        self.width = width
        self.height = height
        self.background = "black"
        self.textColor = "white"

        # Conecta ao display via SPI (ajuste os pinos GPIO)
        # Exemplo: porta=0, device=0 (CE0), DC=GPIO 27, RST=GPIO 17
        self.serial = spi(port=0, device=0, gpio_DC=27, gpio_RST=17)
        # Cria o dispositivo ST7735 (ajuste 'rotate' se necessário)
        self.device = st7735(self.serial, active_low=False, rotate=0, width=self.width, height=self.height)
        
        # Carrega uma fonte
        try:
            # Tente usar uma fonte de melhor qualidade
            self.font = ImageFont.truetype("DejaVuSansMono.ttf", 10)
        except IOError:
            # Fonte padrão da PIL
            self.font = ImageFont.load_default()
            
        # Determina a altura que o texto ocupará (necessário para calcular o número de linhas)
        # O método getsize() é mais preciso, mas para fontes simples, o valor '12' é uma boa estimativa.
        self.altura_linha = 12 
        
        # Calcula o número máximo de linhas que cabem no display
        self.num_linhas_max = self.height // self.altura_linha

        # Inicializa o BUFFER CIRCULAR (deque) com strings vazias
        self.buffer_mensagens = deque([""] * self.num_linhas_max, maxlen=self.num_linhas_max)
        
        # Limpa o display na inicialização
        self.device.clear()

    def _redraw_terminal(self):
        """
        Método privado para redesenhar todas as linhas do buffer na tela.
        """
        # Abre o canvas para desenho
        with canvas(self.device) as draw:
            # 1. Limpa o fundo com a cor preta (ou a cor de fundo definida)
            draw.rectangle(self.device.bounding_box, outline=self.background, fill=self.background)
            
            # 2. Itera sobre o buffer (do topo para a base)
            for i, linha in enumerate(self.buffer_mensagens):
                # A posição Y é calculada a partir do índice da linha no buffer
                y_pos = i * self.altura_linha
                
                # Desenha a linha na posição (x=1, y=y_pos)
                draw.text((1, y_pos), linha, fill=self.textColor, font=self.font)

    def show_message(self, message):
        """
        Adiciona uma nova mensagem ao buffer circular e redesenha o terminal.
        """
        # Adiciona a nova mensagem ao final do deque. 
        # Se o buffer estiver cheio, o item mais antigo (topo) é automaticamente removido.
        self.buffer_mensagens.append(message)
        
        # Redesenha a tela para mostrar a nova configuração do buffer
        self._redraw_terminal()

    def clear(self):
        self.device.clear()
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
            
        # Determina a altura da linha e a largura máxima de desenho
        # getbbox() retorna (left, top, right, bottom). A altura é bottom - top.
        _, top, _, bottom = self.font.getbbox('A')
        self.altura_linha = (bottom - top) + 2 # Altura da fonte + pequeno espaçamento
        self.margem_lateral = 2 # Margem em pixels para evitar que o texto encoste na borda
        self.largura_max_texto = self.width - self.margem_lateral 
        
        # Calcula o número máximo de linhas que cabem no display
        self.num_linhas_max = self.height // self.altura_linha

        # Inicializa o BUFFER CIRCULAR (deque) com strings vazias
        self.buffer_mensagens = deque([""] * self.num_linhas_max, maxlen=self.num_linhas_max)
        
        # Limpa o display na inicialização
        self.device.clear()

    def _wrap_text_to_lines(self, text):
        """
        Divide uma string em uma lista de linhas que cabem na largura da tela
        (em pixels), quebrando somente nos limites das palavras.
        """
        words = text.split()
        if not words:
            return [""]
        
        lines = []
        current_line = words[0]

        for word in words[1:]:
            # Tenta adicionar a próxima palavra à linha atual
            test_line = current_line + " " + word
            
            # Calcula a largura da linha de teste em pixels
            # getbbox() retorna (left, top, right, bottom). A largura é right - left.
            left, _, right, _ = self.font.getbbox(test_line)
            largura = right - left
            
            if largura <= self.largura_max_texto:
                # A palavra cabe, então a adicionamos
                current_line = test_line
            else:
                # A palavra não cabe, finaliza a linha atual e começa uma nova
                lines.append(current_line)
                current_line = word # A nova linha começa com a palavra que não coube

        # Adiciona a última linha restante
        lines.append(current_line)
        return lines

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
        Agora gerencia quebras de linha longas.
        """
        # 1. Quebra a mensagem longa em várias linhas se necessário
        linhas_quebradas = self._wrap_text_to_lines(message)
        
        # 2. Adiciona CADA linha gerada ao buffer circular
        # Isso garante que a rolagem funcione corretamente, tratando uma única 
        # mensagem longa como várias linhas de terminal.
        for linha in linhas_quebradas:
            # O deque já gerencia o maxlen e a rolagem
            self.buffer_mensagens.append(linha)
        
        # 3. Redesenha a tela para mostrar a nova configuração do buffer
        self._redraw_terminal()

    def clear(self):
        self.device.clear()
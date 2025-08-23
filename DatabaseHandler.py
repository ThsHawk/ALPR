import sqlite3
from datetime import datetime

class DatabaseHandler:
    def __init__(self, db_file):
        """
        Inicializa o gerenciador do banco de dados e cria a conexão.
        
        Args:
            db_file (str): O caminho para o arquivo do banco de dados SQLite.
        """
        self.db_file = db_file
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """
        Gerenciador de contexto para abrir a conexão.
        """
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        print(f"Conectado ao banco de dados: {self.db_file}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Gerenciador de contexto para fechar a conexão.
        """
        if self.conn:
            self.conn.commit()
            self.conn.close()
            print(f"Conexão com o banco de dados {self.db_file} fechada.")

    def create_tables(self):
        """
        Cria as duas tabelas necessárias: 'registered_plates' e 'access_log'.
        """
        # Tabela 1: Placas cadastradas
        query_registered = "CREATE TABLE IF NOT EXISTS registered_plates (id INTEGER PRIMARY KEY AUTOINCREMENT, plate_number TEXT NOT NULL UNIQUE, description TEXT);"
        """
        CREATE TABLE IF NOT EXISTS registered_plates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT NOT NULL UNIQUE,
            description TEXT
        );
        """
        self.cursor.execute(query_registered)
        print("Tabela 'registered_plates' verificada/criada.")

        # Tabela 2: Log de acessos
        query_log = "CREATE TABLE IF NOT EXISTS access_log (id INTEGER PRIMARY KEY AUTOINCREMENT, plate_number TEXT NOT NULL, timestamp TEXT NOT NULL, access_granted BOOLEAN NOT NULL );"
        """
        CREATE TABLE IF NOT EXISTS registered_plates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT NOT NULL UNIQUE,
            description TEXT
        );
        """
        self.cursor.execute(query_log)
        print("Tabela 'access_log' verificada/criada.")

    def register_plate(self, plate_number, description=""):
        """
        Cadastra uma nova placa no banco de dados.
        
        Args:
            plate_number (str): A string da placa de carro.
            description (str): Uma descrição opcional para a placa (ex: "carro do diretor").
        """
        query = "INSERT OR IGNORE INTO registered_plates (plate_number, description) VALUES (?, ?);"
        self.cursor.execute(query, (plate_number, description))
        print(f"Placa '{plate_number}' cadastrada.")

    def unregister_plate(self, plate_number):
        """
        Remove o cadastro de uma placa da tabela de placas cadastradas.
        
        Args:
            plate_number (str): A string da placa de carro a ser removida.
        """
        query = "DELETE FROM registered_plates WHERE plate_number = ?;"
        self.cursor.execute(query, (plate_number,))
        print(f"Placa '{plate_number}' removida dos cadastros.")

    def log_access(self, plate_number, access_granted):
        """
        Registra um evento de acesso (placa reconhecida).
        
        Args:
            plate_number (str): A string da placa de carro.
            access_granted (bool): True se o acesso foi concedido, False caso contrário.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "INSERT INTO access_log (plate_number, timestamp, access_granted) VALUES (?, ?, ?);"
        self.cursor.execute(query, (plate_number, timestamp, access_granted))
        print(f"Acesso registrado para a placa '{plate_number}'.")

    def is_plate_registered(self, plate_number):
        """
        Verifica se uma placa existe na tabela de placas cadastradas.
        
        Args:
            plate_number (str): A string da placa de carro.
            
        Returns:
            bool: True se a placa está cadastrada, False caso contrário.
        """
        query = "SELECT description FROM registered_plates WHERE plate_number = ?;"
        self.cursor.execute(query, (plate_number,))
        result = self.cursor.fetchone()
        if result:
            # Se um resultado foi encontrado, ele é uma tupla com a descrição
            description = result[0]
            return True, description
        else:
            # Se nenhum resultado foi encontrado, retorna False
            return False, ""
    
    def get_all_plates(self):
        """
        Consulta e retorna todos os registros de placas.
        
        Returns:
            list: Uma lista de tuplas, onde cada tupla representa uma linha da tabela.
        """
        query = "SELECT * FROM registered_plates;"
        self.cursor.execute(query)
        return self.cursor.fetchall()
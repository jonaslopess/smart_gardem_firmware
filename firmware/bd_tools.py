import sqlite3
import datetime as dt

# BD_PATH = "machine-gun-analyser/banco.db"
BD_PATH = "../database/banco.db"

class BancoDeDados:
    """Classe que representa o banco de dados (database) da aplicação"""
    
    def __init__(self, nome=BD_PATH):
        """Inicializa o banco de dados"""
        self.nome, self.conexao = nome, None

    def conecta(self):
        """Conecta passando o nome do arquivo"""
        self.conexao = sqlite3.connect(self.nome)

    def desconecta(self):
        """Desconecta do banco"""
        try:
            self.conexao.close()
        except AttributeError:
            pass

    def criar_tabelas(self):
        # Cria as tabelas do banco
        try:
            # definindo um cursor
            # o cursor permite navegar e manipular os registros do banco de dados
            cursor = self.conexao.cursor()
            
            # cria a tabela (se ela não existir) utilizando um comando SQL
            # tipos de dados do SQlite3: http://www.sqlite.org/datatype3.html
            # o execute lê e executa comandos SQL diretamente no banco de dados
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS MonitoringCapability (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    key_word VARCHAR(45) NOT NULL,
                    current_value FLOAT NOT NULL DEFAULT 0.0
                    
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS MonitoringLog (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    temperature_value FLOAT,
                    humidity_value FLOAT,
                    light_value FLOAT,
                    moisture_value FLOAT,
                    balance INT,
                    total_irrigation INT
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS TransactionLog (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    tx_hash VARCHAR(66) NOT NULL,
                    type VARCHAR(45) NOT NULL,
                    delay FLOAT,
                    cost INT,
                    msg VARCHAR(90)
            );
            """)

        except AttributeError:
            print('Faça a conexão do banco antes de criar as tabelas.')

    def inserir_monitoring_capacity(
            self, 
            key_word    
        ):
        try:
            cursor = self.conexao.cursor()

            try:
                cursor.execute(f"""
                    SELECT * FROM MonitoringCapability
                    WHERE
                        key_word = '{key_word}'
                """)
                if len(cursor.fetchall()) == 0:
                
                    # insere na tabela
                    cursor.execute("""
                    INSERT INTO MonitoringCapability (
                        key_word
                    ) VALUES (?)
                    """, (
                        key_word,
                    ))

                    # o commit grava de fato as alterações na tabela
                    # pode-se fazer alterações na tabela com as instruções INSERT, UPDATE, DELETE
                    self.conexao.commit()

                    return cursor.lastrowid
                else:
                    return print('Já existe MonitoringCapability com esta configuração!')
            except sqlite3.IntegrityError:
                print('erro!')
        except AttributeError:
            print('Faça a conexão do banco antes de inserir.')

    def inserir_monitoring_log(self,
                    timestamp,
                    temperature_value,
                    humidity_value,
                    light_value,
                    moisture_value,
                    balance,
                    total_irrigation
            ):
        try:
            cursor = self.conexao.cursor()

            try:
                cursor.execute(f"""
                    SELECT * FROM MonitoringLog
                    WHERE
                        timestamp = '{timestamp}'
                """)
                if len(cursor.fetchall()) == 0:
                    # insere na tabela
                    cursor.execute("""
                    INSERT INTO MonitoringLog (
                        timestamp,
                        temperature_value,
                        humidity_value,
                        light_value,
                        moisture_value,
                        balance,
                        total_irrigation
                    ) VALUES (?,?,?,?,?,?,?)
                    """, (
                        timestamp,
                        temperature_value,
                        humidity_value,
                        light_value,
                        moisture_value,
                        balance,
                        total_irrigation
                    ))
                else:
                    print("Já existe MonitoringLog para este timestamp!")

                # o commit grava de fato as alterações na tabela
                # pode-se fazer alterações na tabela com as instruções INSERT, UPDATE, DELETE
                self.conexao.commit()
            except sqlite3.IntegrityError:
                print('erro!')
        except AttributeError:
            print('Faça a conexão do banco antes de inserir.')

    def inserir_transaction_log(self,
                    tx_hash,
                    type,
                    delay,
                    cost,
                    msg
            ):
        try:
            cursor = self.conexao.cursor()

            try:
                cursor.execute("""
                INSERT INTO TransactionLog (
                    tx_hash,
                    type,
                    delay,
                    cost,
                    msg
                ) VALUES (?,?,?,?,?)
                """, (
                    tx_hash,
                    type,
                    delay,
                    cost,
                    msg
                ))

                # o commit grava de fato as alterações na tabela
                # pode-se fazer alterações na tabela com as instruções INSERT, UPDATE, DELETE
                self.conexao.commit()
            except sqlite3.IntegrityError:
                print('erro!')
        except AttributeError:
            print('Faça a conexão do banco antes de inserir.')
    
    def get_all_monitoring_logs(self):
        try:
            cursor = self.conexao.cursor()

            # obtém todos os dados
            cursor.execute(f"""
                SELECT * FROM MonitoringLog
            """)
            return cursor.fetchall()

        except AttributeError:
            print('Faça a conexão do banco antes de consultar.')
    
    def get_all_transaction_logs(self):
        try:
            cursor = self.conexao.cursor()

            # obtém todos os dados
            cursor.execute(f"""
                SELECT * FROM TransactionLog
            """)
            return cursor.fetchall()

        except AttributeError:
            print('Faça a conexão do banco antes de consultar.')
    
    def get_all_monitoring_capabilities(self):
        try:
            cursor = self.conexao.cursor()

            # obtém todos os dados
            cursor.execute(f"""
                SELECT * FROM MonitoringCapability
            """)
            return cursor.fetchall()

        except AttributeError:
            print('Faça a conexão do banco antes de consultar.')

    def get_backup(self, file_name):
        import io
        with io.open(file_name, 'w') as p: 
            # iterdump() function
            for line in self.conexao.iterdump(): 
                p.write('%s\n' % line)


#if __name__ == '__main__':
#   bd = BancoDeDados()
#   bd.conecta()
#   bd.criar_tabelas()
#   bd.inserir_monitoring_capacity("temperature")
#   bd.inserir_monitoring_capacity("humidity")
#   bd.inserir_monitoring_capacity("light")
#   bd.inserir_monitoring_capacity("moisture")
    
#   bd.desconecta()
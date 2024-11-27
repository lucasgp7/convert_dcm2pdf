import configparser
import os
import psycopg2
import logging

class PostgreSQLConnector:
    def __init__(self, config_path='config/config.ini'):
        """
        Inicializa o conector PostgreSQL com configurações do arquivo de configuração
        
        :param config_path: Caminho para o arquivo de configuração
        """
        # Configura logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Lê configurações
        self.config = configparser.ConfigParser()
        
        # Verifica se o arquivo de configuração existe
        if not os.path.exists(config_path):
            self.logger.error(f"Arquivo de configuração não encontrado: {config_path}")
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
        
        self.config.read(config_path)
        
        # Parâmetros de conexão
        self.host = self.config['postgresql']['host']
        self.user = self.config['postgresql']['user']
        self.password = self.config['postgresql']['password']
        self.database = self.config['postgresql']['database']
        
        # Conexão
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        Estabelece conexão com o banco de dados PostgreSQL
        
        :return: Conexão psycopg2
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            self.logger.info("Conexão com o banco de dados estabelecida com sucesso")
            return self.connection
        except (Exception, psycopg2.Error) as error:
            self.logger.error(f"Erro ao conectar ao banco de dados PostgreSQL: {error}")
            raise

    def execute_query(self, query, params=None):
        """
        Executa uma consulta SQL
        
        :param query: Consulta SQL a ser executada
        :param params: Parâmetros para a consulta (opcional)
        :return: Resultados da consulta
        """
        try:
            if not self.connection:
                self.connect()
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            return self.cursor.fetchall()
        except (Exception, psycopg2.Error) as error:
            self.logger.error(f"Erro ao executar consulta: {error}")
            raise

    def execute_insert(self, query, params=None):
        """
        Executa uma inserção no banco de dados
        
        :param query: Consulta de inserção SQL
        :param params: Parâmetros para a inserção
        """
        try:
            if not self.connection:
                self.connect()
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            self.connection.commit()
            self.logger.info("Inserção realizada com sucesso")
        except (Exception, psycopg2.Error) as error:
            if self.connection:
                self.connection.rollback()
            self.logger.error(f"Erro ao realizar inserção: {error}")
            raise

    def close(self):
        """
        Fecha a conexão e o cursor do banco de dados
        """
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
                self.logger.info("Conexão com o banco de dados fechada")
        except (Exception, psycopg2.Error) as error:
            self.logger.error(f"Erro ao fechar conexão: {error}")

    def __del__(self):
        """
        Destrutor para garantir que a conexão seja fechada
        """
        self.close()

# Exporta a classe para ser importada
__all__ = ['PostgreSQLConnector']
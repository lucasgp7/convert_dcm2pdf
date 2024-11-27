import os
import sys
import logging
import configparser
import psycopg2
from psycopg2 import sql

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from convert_dcm2pdf.database.connect import PostgreSQLConnector
from convert_dcm2pdf.utils.logging_config import setup_logging

# Configura logging
setup_logging()
logger = logging.getLogger(__name__)

def create_database():
    """
    Cria o banco de dados se não existir
    """
    try:
        # Lê configurações
        config = configparser.ConfigParser()
        config.read('./config/config.ini')
        
        # Parâmetros de conexão
        host = config.get('postgresql', 'host')
        user = config.get('postgresql', 'user')
        password = config.get('postgresql', 'password')
        database = config.get('postgresql', 'database')
        
        # Conecta ao banco de dados padrão para criar novo banco
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database='postgres'  # Banco de sistema padrão
        )
        conn.autocommit = True
        
        # Cria cursor
        cur = conn.cursor()
        
        # Verifica se o banco de dados já existe
        cur.execute(sql.SQL("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s"), (database,))
        exists = cur.fetchone()
        
        if not exists:
            # Cria o banco de dados
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database)))
            logger.info(f"Banco de dados {database} criado com sucesso.")
        else:
            logger.info(f"Banco de dados {database} já existe.")
        
        # Fecha conexão
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Erro ao criar banco de dados: {e}")
        raise

def create_tables():
    """
    Cria tabelas necessárias para o projeto
    """
    try:
        # Usa o conector para estabelecer conexão
        connector = PostgreSQLConnector()
        conn = connector.connect()
        cur = conn.cursor()
        
        # SQL para criar tabelas
        tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS dicom_files (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                filepath VARCHAR(512) NOT NULL,
                patient_id VARCHAR(100),
                study_date DATE,
                modality VARCHAR(50),
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            """
            CREATE TABLE IF NOT EXISTS conversion_log (
                id SERIAL PRIMARY KEY,
                dicom_file_id INTEGER REFERENCES dicom_files(id),
                pdf_filepath VARCHAR(512),
                conversion_status VARCHAR(50),
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            """
            CREATE TABLE IF NOT EXISTS download_log (
                id SERIAL PRIMARY KEY,
                patient_id VARCHAR(100),
                source VARCHAR(255),
                status VARCHAR(50),
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        # Executa criação de tabelas
        for table_sql in tables_sql:
            cur.execute(table_sql)
        
        # Commita as alterações
        conn.commit()
        logger.info("Tabelas criadas com sucesso.")
        
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        raise
    finally:
        # Fecha conexão
        connector.close()

def main():
    """
    Função principal para configuração do banco de dados
    """
    try:
        logger.info("Iniciando configuração do banco de dados...")
        
        # Cria banco de dados
        create_database()
        
        # Cria tabelas
        create_tables()
        
        logger.info("Configuração do banco de dados concluída com sucesso.")
    
    except Exception as e:
        logger.error(f"Erro na configuração do banco de dados: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
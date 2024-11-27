import sys
import logging
from convert_dcm2pdf.core.config_manager import ConfigManager
from convert_dcm2pdf.database.connect import PostgreSQLConnector

def create_pdf_storage_table(connector):
    """
    Cria tabela para armazenamento de PDFs
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS pdf_storage (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        file_content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(50) DEFAULT 'active'
    )
    """
    connector.execute(create_table_query)
    print("Tabela pdf_storage criada com sucesso.")

def add_index(connector):
    """
    Adiciona índices para melhorar performance
    """
    create_index_queries = [
        "CREATE INDEX IF NOT EXISTS idx_pdf_filename ON pdf_storage(filename)",
        "CREATE INDEX IF NOT EXISTS idx_pdf_status ON pdf_storage(status)"
    ]
    
    for query in create_index_queries:
        connector.execute(query)
        print(f"Índice criado: {query}")

def main():
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Carregar configurações
        config_manager = ConfigManager()
        db_config = config_manager.get_database_config()
        
        # Conectar ao banco de dados
        with PostgreSQLConnector(db_config) as connector:
            print("Iniciando migração de banco de dados...")
            
            # Criar tabela
            create_pdf_storage_table(connector)
            
            # Adicionar índices
            add_index(connector)
            
            print("Migração concluída com sucesso.")
    
    except Exception as e:
        logging.error(f"Erro durante migração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
import os
import logging
from logging.config import fileConfig

def setup_logging(
    default_path='config/logging.conf', 
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """
    Configura logging para o projeto
    
    Args:
        default_path (str): Caminho para o arquivo de configuração de log
        default_level (logging.LEVEL): Nível padrão de log
        env_key (str): Chave de ambiente para configuração de log
    """
    path = os.getenv(env_key, default_path)
    
    if os.path.exists(path):
        fileConfig(path, disable_existing_loggers=False)
    else:
        logging.basicConfig(
            level=default_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('app.log')
            ]
        )
        logging.warning(f"Logging configuration file not found at {path}")
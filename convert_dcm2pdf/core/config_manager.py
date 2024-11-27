import os
from typing import Dict, Any
from configparser import ConfigParser
from dotenv import load_dotenv

class ConfigManager:
    """
    Gerencia configurações do projeto
    Suporta configurações via arquivo .ini e variáveis de ambiente
    """
    
    def __init__(self, config_path: str = None):
        """
        Inicializa o gerenciador de configurações

        Args:
            config_path (str, opcional): Caminho para o arquivo de configuração
        """
        # Carrega variáveis de ambiente
        load_dotenv()
        
        # Caminho padrão para configurações
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 'config', 'config.ini'
        )
        
        # Parser de configurações
        self.config = ConfigParser()
        self.config.read(self.config_path)
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Obtém valor de configuração, primeiro de variáveis de ambiente,
        depois do arquivo de configuração

        Args:
            section (str): Seção da configuração
            key (str): Chave da configuração
            default (Any, opcional): Valor padrão se não encontrado

        Returns:
            Any: Valor da configuração
        """
        # Prioriza variáveis de ambiente
        env_key = f"{section.upper()}_{key.upper()}"
        env_value = os.getenv(env_key)
        
        if env_value is not None:
            return env_value
        
        # Então tenta arquivo de configuração
        try:
            return self.config.get(section, key)
        except:
            return default
    
    def get_database_config(self) -> Dict[str, str]:
        """
        Obtém configurações de banco de dados

        Returns:
            Dict[str, str]: Configurações de conexão com banco de dados
        """
        return {
            'host': self.get('postgresql', 'host', 'localhost'),
            'database': self.get('postgresql', 'database', 'irg'),
            'user': self.get('postgresql', 'user', 'postgres'),
            'password': self.get('postgresql', 'password', ''),
        }
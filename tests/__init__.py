# Configurações e importações para testes
import os
import sys

# Adiciona o diretório do projeto ao path para importações
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

__all__ = []
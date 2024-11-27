import configparser
import os
import pytest

def test_config_file_exists():
    """Verifica se o arquivo de configuração existe"""
    assert os.path.exists('config/config.ini'), "Arquivo de configuração não encontrado"

def test_config_parse():
    """Testa se o arquivo de configuração pode ser parseado corretamente"""
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    
    # Verificações para seção PostgreSQL
    assert 'postgresql' in config.sections(), "Seção postgresql não encontrada"
    assert config['postgresql']['host'] == 'localhost', "Host PostgreSQL incorreto"
    assert config['postgresql']['user'] == 'postgres', "Usuário PostgreSQL incorreto"
    assert config['postgresql']['password'] == 'lucas123', "Senha PostgreSQL incorreta"
    assert config['postgresql']['database'] == 'postgres', "Database PostgreSQL incorreta"

def test_dcm_config():
    """Testa configurações da seção DCM"""
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    
    assert 'dcm' in config.sections(), "Seção dcm não encontrada"
    assert config['dcm']['executable_path'].endswith('dcm2pdf.exe'), "Caminho do executável DCM incorreto"
    assert os.path.exists(config['dcm']['executable_path']), "Executável DCM não encontrado"

def test_ssh_config():
    """Testa configurações da seção SSH"""
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    
    assert 'ssh' in config.sections(), "Seção ssh não encontrada"
    assert config['ssh']['host'] == 'localhost', "Host SSH incorreto"
    assert config['ssh']['user'] == 'seu_usuario', "Usuário SSH incorreto"
    assert config['ssh']['password'] == 'sua_senha', "Senha SSH incorreta"

def test_paths_config():
    """Testa configurações de diretórios"""
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    
    assert 'paths' in config.sections(), "Seção paths não encontrada"
    
    # Verifica se os diretórios existem ou podem ser criados
    download_dir = config['paths']['download_directory']
    pdf_dir = config['paths']['pdf_directory']
    log_dir = config['paths']['log_directory']
    
    # Converte para caminho absoluto se for relativo
    download_dir = os.path.abspath(download_dir)
    pdf_dir = os.path.abspath(pdf_dir)
    log_dir = os.path.abspath(log_dir)
    
    # Cria diretórios se não existirem
    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    
    assert os.path.isdir(download_dir), f"Diretório de download inválido: {download_dir}"
    assert os.path.isdir(pdf_dir), f"Diretório de PDFs inválido: {pdf_dir}"
    assert os.path.isdir(log_dir), f"Diretório de logs inválido: {log_dir}"

if __name__ == '__main__':
    pytest.main([__file__])
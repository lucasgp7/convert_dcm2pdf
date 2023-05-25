import psycopg2
import paramiko
import configparser
import logging
import os
import subprocess
import shutil

# Configurar o logger
logging.basicConfig(filename='app.log', level=logging.INFO)

# Obtenha o caminho absoluto para o arquivo config.properties
caminho_arquivo = os.path.join('config.properties')

# Carregue as configurações do arquivo
config = configparser.ConfigParser()
config.read(caminho_arquivo, encoding='utf-8')

# Obter o caminho do executável caminhoDCMTK a partir do arquivo de configuração
dcm_executable = config.get('dcm', 'dcm_executable')

# Configurações de conexão com o banco de dados PostgreSQL
db_host = '127.0.0.1'
db_user = 'postgres'
db_password = '123'
db_database = 'irg'

con = psycopg2.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_database
)

# Configurações de conexão SSH
ssh_host = 'fd55:afaf::171:0:1'
ssh_user = 'animati'
ssh_password = 'eS4IezITMh29pmkM'

# Conexão SSH ao servidor Linux
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ssh_host, username=ssh_user, password=ssh_password)

# Pasta de destino para os arquivos .dcm no Windows
# Substitua pelo caminho desejado no Windows
download_directory = r'D:/Animati_Clientes/IRG/dcm'

# Pasta de destino para os arquivos PDF no Windows
# Substitua pelo caminho desejado no Windows
target_directory = r'D:/Animati_Clientes/IRG/pdf'

try:
    # Criar um cursor para executar consultas SQL
    cursor = con.cursor()

    # Consulta SQL
    consulta_sql = "SELECT pk, filepath, accession_no FROM public.study s LIMIT 4"

    # Executar a consulta SQL
    cursor.execute(consulta_sql)

    # Obter os resultados
    resultados = cursor.fetchall()

    # Lista de casos a serem processados
    casos = resultados

    # Processar os resultados
    for resultado in casos:
        pk = resultado[0]
        filepath = resultado[1]
        accession_no = resultado[2]

        # Caminho completo do arquivo no servidor Linux
        remote_filepath = f'/union/pacs-data/archive/{filepath}'

        # Caminho completo do arquivo .dcm no Windows
        local_filepath = os.path.join(download_directory, accession_no + '.dcm')

        # Baixar o arquivo .dcm do servidor Linux para o Windows
        ftp = ssh.open_sftp()
        ftp.get(remote_filepath, local_filepath)
        ftp.close()

        # Verificar se o arquivo .dcm foi baixado com sucesso
        if os.path.isfile(local_filepath):
            logging.info(f"Arquivo .dcm baixado com sucesso: {local_filepath}")
            print("Arquivo .dcm baixado com sucesso de An: ", accession_no)
        else:
            logging.error(f"Erro ao baixar o arquivo .dcm: {remote_filepath}")
            continue

        # Caminho completo do arquivo PDF no Windows
        pdf_filepath = os.path.join(target_directory, accession_no + '.pdf')

        # Percorrer os arquivos no diretório de download
        for root, dirs, files in os.walk(download_directory):
            for file in files:
                file_path = os.path.join(root, file) 
                file_path = os.path.join(root, file)  # Caminho completo do arquivo .dcm
                pdf_path = os.path.join(target_directory, file.replace('.dcm', '.pdf'))  # Caminho completo do arquivo PDF

                # Conversão do arquivo .dcm em PDF usando o DCMTK
                command = f"{dcm_executable} -v {file_path} {pdf_path}"
                print(command)
                result = subprocess.run(command, shell=True, capture_output=True, text=True)

                # Verificar se a conversão foi bem-sucedida
                if result.returncode == 0:
                    logging.info(f"Arquivo convertido com sucesso: {pdf_path}")
                    print("Arquivo convertido com sucesso:")
                else:
                    logging.error(f"Erro ao converter o arquivo .dcm: {file_path}")
                    print("Erro ao converter o arquivo .dcm:")

        # Mover o arquivo PDF para a pasta de destino no Windows
        shutil.move(pdf_filepath, target_directory)
        logging.info(f"PDF movido para a pasta de destino: {pdf_filepath}")

except psycopg2.Error as e:
    logging.error(f"Erro ao acessar o banco de dados PostgreSQL: {e}")

except Exception as e:
    logging.error(f"Erro ao executar consulta SQL: {str(e)}")

finally:
    # Fechar cursor e conexão com o banco de dados
    cursor.close()
    con.close()

    # Fechar conexão SSH
    ssh.close()


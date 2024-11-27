import os
import logging
import paramiko
from typing import List, Tuple
from convert_dcm2pdf.database.connect import PostgreSQLConnector
from convert_dcm2pdf.utils.exceptions import DownloadError

class DCMDownloader:
    """
    Classe responsável por download de arquivos DICOM do servidor
    """
    def __init__(self, config_manager):
        """
        Inicializa o downloader com configurações

        Args:
            config_manager (ConfigManager): Gerenciador de configurações
        """
        self.logger = logging.getLogger(__name__)
        self.config = config_manager
        
        # Configurações SSH
        self.ssh_host = self.config.get('ssh', 'host')
        self.ssh_user = self.config.get('ssh', 'user')
        self.ssh_password = self.config.get('ssh', 'password')
        
        # Configurações de banco de dados
        self.db_config = self.config.get_database_config()
        
        # Diretório de download
        self.download_directory = self.config.get('paths', 'download_directory', './downloads')
        os.makedirs(self.download_directory, exist_ok=True)

    def _connect_ssh(self) -> paramiko.SSHClient:
        """
        Estabelece conexão SSH segura

        Returns:
            paramiko.SSHClient: Cliente SSH conectado
        
        Raises:
            DownloadError: Se falhar conexão SSH
        """
        try:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.ssh_host, 
                username=self.ssh_user, 
                password=self.ssh_password
            )
            return ssh
        except Exception as e:
            self.logger.error(f"Erro de conexão SSH: {e}")
            raise DownloadError(f"Falha na conexão SSH: {e}")

    def _get_dcm_files_to_download(self, limit: int = 10) -> List[Tuple[str, str]]:
        """
        Busca lista de arquivos DICOM para download do banco de dados

        Args:
            limit (int, opcional): Limite de arquivos para download. Padrão 10.

        Returns:
            List[Tuple[str, str]]: Lista de tuplas (filepath, accession_no)
        """
        try:
            with PostgreSQLConnector(self.db_config) as connector:
                query = """
                SELECT filepath, accession_no 
                FROM public.study 
                WHERE filepath IS NOT NULL 
                LIMIT %s
                """
                return connector.fetch_all(query, (limit,))
        except Exception as e:
            self.logger.error(f"Erro ao buscar arquivos DICOM: {e}")
            return []

    def download_dcm_files(self, limit: int = 10) -> List[str]:
        """
        Realiza download de arquivos DICOM

        Args:
            limit (int, opcional): Limite de arquivos. Padrão 10.

        Returns:
            List[str]: Caminhos dos arquivos baixados
        """
        ssh = self._connect_ssh()
        downloaded_files = []

        try:
            # Obter lista de arquivos para download
            files_to_download = self._get_dcm_files_to_download(limit)
            
            # Iniciar transferência SFTP
            sftp = ssh.open_sftp()

            for remote_filepath, accession_no in files_to_download:
                try:
                    # Caminho completo remoto
                    full_remote_path = f'/union/pacs-data/archive/{remote_filepath}'
                    
                    # Caminho local para salvar
                    local_filepath = os.path.join(
                        self.download_directory, 
                        f'{accession_no}.dcm'
                    )
                    
                    # Baixar arquivo
                    sftp.get(full_remote_path, local_filepath)
                    downloaded_files.append(local_filepath)
                    
                    self.logger.info(f"Arquivo baixado: {local_filepath}")
                
                except Exception as file_error:
                    self.logger.error(f"Erro ao baixar {remote_filepath}: {file_error}")
            
            sftp.close()
        
        except Exception as e:
            self.logger.error(f"Erro durante download de DCM: {e}")
        
        finally:
            ssh.close()
        
        return downloaded_files
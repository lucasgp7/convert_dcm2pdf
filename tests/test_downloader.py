import os
import pytest
from unittest.mock import Mock, patch
from convert_dcm2pdf.core.dcm_downloader import DCMDownloader
from convert_dcm2pdf.utils.exceptions import DownloadError

class TestDCMDownloader:
    @pytest.fixture
    def mock_config_manager(self):
        """
        Fixture para criar mock de ConfigManager
        """
        config_mock = Mock()
        config_mock.get.side_effect = [
            'localhost',  # ssh host
            'user',       # ssh user
            'password',   # ssh password
            './downloads'  # download directory
        ]
        config_mock.get_database_config.return_value = {
            'host': 'localhost',
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_pass'
        }
        return config_mock

    def test_downloader_initialization(self, mock_config_manager):
        """
        Testa inicialização do downloader
        """
        downloader = DCMDownloader(mock_config_manager)
        
        assert downloader.ssh_host == 'localhost'
        assert downloader.download_directory == './downloads'
        assert os.path.exists('./downloads')

    @patch('paramiko.SSHClient')
    @patch('dicom_converter.database.postgres_connector.PostgreSQLConnector')
    def test_download_dcm_files(self, mock_connector, mock_ssh_client, mock_config_manager):
        """
        Testa download de arquivos DICOM
        """
        # Configurar mocks
        mock_connector.return_value.__enter__.return_value.fetch_all.return_value = [
            ('/path/to/file1.dcm', 'ACC001'),
            ('/path/to/file2.dcm', 'ACC002')
        ]
        
        mock_sftp = mock_ssh_client.return_value.open_sftp.return_value
        
        # Criar downloader
        downloader = DCMDownloader(mock_config_manager)
        
        # Executar download
        downloaded_files = downloader.download_dcm_files(limit=2)
        
        # Verificações
        assert len(downloaded_files) == 2
        assert mock_sftp.get.call_count == 2

    def test_ssh_connection_failure(self, mock_config_manager):
        """
        Testa falha de conexão SSH
        """
        mock_config_manager.get.side_effect = Exception("Conexão falhou")
        
        with pytest.raises(DownloadError):
            downloader = DCMDownloader(mock_config_manager)
            downloader._connect_ssh()
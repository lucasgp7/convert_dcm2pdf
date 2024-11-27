import pytest
from unittest.mock import Mock, patch
from convert_dcm2pdf.core.dcm_converter import DCMConverter

class TestDCMConverter:
    @pytest.fixture
    def mock_config_manager(self):
        """
        Fixture to create a mock of ConfigManager
        """
        config_manager_mock = Mock()
        config_manager_mock.get.side_effect = [
            '/path/to/dcmtk',  # DCM executable path
            './downloads',    # Download directory
            './pdfs'          # PDF directory
        ]
        config_manager_mock.get_database_config.return_value = {
            'host': 'localhost',
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_pass'
        }
        return config_manager_mock


class DicomConverterError(Exception):
    """
    Classe base de exceções para o projeto DicomConverter
    """
    pass

class ConfigurationError(DicomConverterError):
    """
    Exceção para erros de configuração
    """
    pass

class DownloadError(DicomConverterError):
    """
    Exceção específica para erros durante o processo de download
    """
    pass

class ConversionError(DicomConverterError):
    """
    Exceção para erros durante a conversão de arquivos DICOM
    """
    pass

class DatabaseError(DicomConverterError):
    """
    Exceção para erros relacionados a operações de banco de dados
    """
    pass

# Exporta as exceções
__all__ = [
    'DicomConverterError',
    'ConfigurationError',
    'DownloadError', 
    'ConversionError',
    'DatabaseError'
]
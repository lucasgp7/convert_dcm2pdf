import sys
import logging
from convert_dcm2pdf.core.dcm_downloader import DCMDownloader
from convert_dcm2pdf.core.dcm_converter import DCMConverter
from convert_dcm2pdf.utils.logging_config import setup_logging
from convert_dcm2pdf.core.config_manager import ConfigManager

def main():
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Gerenciar configurações
        config_manager = ConfigManager()

        while True:
            print("\nDICOM Converter")
            print("1 - Baixar arquivos DICOM")
            print("2 - Converter arquivos DICOM")
            print("3 - Sair")
            
            escolha = input("Escolha uma opção: ")

            if escolha == '1':
                downloader = DCMDownloader(config_manager)
                downloader.download_dcm_files()
            
            elif escolha == '2':
                converter = DCMConverter(config_manager)
                converter.convert_all_dcm_files()
            
            elif escolha == '3':
                print("Encerrando...")
                break
            
            else:
                print("Opção inválida!")

    except Exception as e:
        logger.error(f"Erro inesperado: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
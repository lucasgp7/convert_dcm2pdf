import os
import base64
import logging
import subprocess
from typing import List, Optional, Tuple
from convert_dcm2pdf.database.connect import PostgreSQLConnector
from convert_dcm2pdf.utils.exceptions import ConversionError

class DCMConverter:
    """
    Classe responsável pela conversão de arquivos DICOM para PDF
    """
    def __init__(self, config_manager):
        """
        Inicializa o conversor

        Args:
            config_manager (ConfigManager): Gerenciador de configurações
        """
        self.logger = logging.getLogger(__name__)
        self.config = config_manager
        
        # Configurações de conversão
        self.dcm_executable = self.config.get('dcm', 'executable_path')
        self.download_directory = self.config.get('paths', 'download_directory', './downloads')
        self.pdf_directory = self.config.get('paths', 'pdf_directory', './pdfs')
        
        # Configurações de banco de dados
        self.db_config = self.config.get_database_config()
        
        # Criar diretórios se não existirem
        os.makedirs(self.download_directory, exist_ok=True)
        os.makedirs(self.pdf_directory, exist_ok=True)

    def _convert_dcm_to_pdf(self, dcm_filepath: str) -> Optional[str]:
        """
        Converte arquivo DICOM para PDF

        Args:
            dcm_filepath (str): Caminho do arquivo DICOM

        Returns:
            Optional[str]: Caminho do arquivo PDF gerado ou None se falhar
        """
        try:
            # Nome do arquivo PDF
            pdf_filename = os.path.basename(dcm_filepath).replace('.dcm', '.pdf')
            pdf_filepath = os.path.join(self.pdf_directory, pdf_filename)
            
            # Comando de conversão
            command = f"{self.dcm_executable} -v {dcm_filepath} {pdf_filepath}"
            
            # Executar conversão
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            self.logger.info(f"Conversão de {dcm_filepath} para PDF concluída")
            return pdf_filepath
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro na conversão: {e.stderr}")
            raise ConversionError(f"Falha na conversão: {e.stderr}")

    def _read_pdf_as_base64(self, pdf_path: str) -> str:
        """
        Lê arquivo PDF e converte para base64

        Args:
            pdf_path (str): Caminho do arquivo PDF

        Returns:
            str: Conteúdo do PDF em base64
        """
        with open(pdf_path, 'rb') as pdf_file:
            return base64.b64encode(pdf_file.read()).decode('utf-8')

    def convert_all_dcm_files(self) -> Tuple[List[str], List[str]]:
        """
        Converte todos os arquivos DCM no diretório de download para PDF
        e salva no banco de dados

        Returns:
            Tuple[List[str], List[str]]: Lista de PDFs gerados e lista de arquivos com erro
        """
        # Listar arquivos DCM no diretório
        dcm_files = [
            os.path.join(self.download_directory, f) 
            for f in os.listdir(self.download_directory) 
            if f.endswith('.dcm')
        ]

        # Se não há arquivos, imprimir mensagem
        if not dcm_files:
            print("Nenhum arquivo encontrado")
            return [], []

        # Informar total de arquivos
        print(f"Total de arquivos encontrados: {len(dcm_files)}")

        converted_pdfs = []
        error_files = []

        for dcm_filepath in dcm_files:
            try:
                # Converter DCM para PDF
                pdf_path = self._convert_dcm_to_pdf(dcm_filepath)
                
                if pdf_path:
                    # Converter PDF para base64
                    pdf_base64 = self._read_pdf_as_base64(pdf_path)
                    
                    # Salvar no banco de dados
                    self._save_pdf_to_database(
                        os.path.basename(pdf_path), 
                        pdf_base64
                    )
                    
                    converted_pdfs.append(pdf_path)
                    print(f"Convertido com sucesso: {os.path.basename(dcm_filepath)}")
            
            except Exception as e:
                error_files.append(dcm_filepath)
                print(f"Erro ao processar {os.path.basename(dcm_filepath)}: {e}")
        
        # Resumo final
        print(f"\nResumo:")
        print(f"Total de arquivos processados: {len(dcm_files)}")
        print(f"Convertidos com sucesso: {len(converted_pdfs)}")
        print(f"Falhas na conversão: {len(error_files)}")

        return converted_pdfs, error_files

    def _save_pdf_to_database(self, filename: str, pdf_base64: str):
        """
        Salva PDF convertido no banco de dados

        Args:
            filename (str): Nome do arquivo PDF
            pdf_base64 (str): Conteúdo do PDF em base64
        """
        try:
            if not self.db_config:
                raise ValueError("Configuração do banco de dados não encontrada")
            
            try:
                with PostgreSQLConnector(self.db_config) as connector:
                    query = """
                    INSERT INTO pdf_storage (filename, file_content)
                    VALUES (%s, %s)
                    """
                    connector.execute_insert(query, (filename, pdf_base64))
            except (Exception) as e:
                self.logger.error(f"Erro ao inserir PDF no banco de dados: {e}")
                
        
        except Exception as e:
            self.logger.error(f"Erro ao salvar PDF no banco: {e}")
from typing import List, Optional
from PyPDF2 import PdfMerger
from platformdirs import user_downloads_dir
import os


class PDFService:
    def __init__(self, output_dir: str = f"{user_downloads_dir()}/TIRUS_DOWNLOADS"):
        # Diretório de saída onde o PDF mergeado será salvo
        self.output_dir = output_dir

    def merge_pdfs(self, pdf_paths: List[str], output_filename: str) -> str:
        """
        Método para realizar o merge de vários PDFs em um único arquivo.
        Retorna o caminho do arquivo PDF gerado.
        """
        # Verifica se os PDFs fornecidos existem
        for pdf in pdf_paths:
            if not os.path.exists(pdf):
                raise FileNotFoundError(f"O arquivo {pdf} não foi encontrado.")

        # Cria o objeto PdfMerger
        merger = PdfMerger()

        # Adiciona todos os PDFs fornecidos
        for pdf in pdf_paths:
            merger.append(pdf)

        # Definindo o caminho do arquivo de saída
        output_path = os.path.join(self.output_dir, output_filename)

        # Escreve o arquivo de saída
        merger.write(output_path)
        merger.close()

        return output_path

    def list_pdfs_in_directory(self) -> List[str]:
        """
        Retorna uma lista de arquivos PDF no diretório de saída.
        """
        return [f for f in os.listdir(self.output_dir) if f.endswith(".pdf")]


# Exemplo de uso:
if __name__ == "__main__":
    output_dir = "/path/to/output"  # Defina o diretório onde o PDF gerado será salvo
    pdf_service = PDFService(output_dir)

    # Caminhos dos PDFs que você quer mesclar
    pdfs_to_merge = ["/path/to/pdf1.pdf", "/path/to/pdf2.pdf", "/path/to/pdf3.pdf"]
    output_filename = "merged_output.pdf"  # Nome do arquivo PDF resultante

    try:
        merged_pdf_path = pdf_service.merge_pdfs(pdfs_to_merge, output_filename)
        print(f"PDF mesclado foi salvo em: {merged_pdf_path}")
    except FileNotFoundError as e:
        print(f"Erro: {e}")

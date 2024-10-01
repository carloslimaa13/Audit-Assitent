# Importando as bibliotecas
import streamlit as st
import PyPDF2
import fitz
import io
from pdfminer.high_level import extract_text
import re
import pytesseract
from PIL import Image
from io import BytesIO

# Apontar onde está o executável do PyTesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\BR0191766727\OneDrive - Enel Spa\PyTesseract-OCR\tesseract-ocr-w64-setup-5.4.0.20240606'

# Título da página
st.write("""
# Audit Brasil
Bem-vindo ao assistente Audit Brasil.
Por aqui você pode ter um auxílio e otimizar seu tempo analisando contratos. Basta adicionar os contratos abaixo e digitar quais palavras ou frases deseja buscar dentro deles.
""")

# Função para limpar o texto
def limpar_texto(texto):
    # Substituir múltiplas quebras de linha por duas para garantir a separação de parágrafos
    texto = re.sub(r'\n\s*\n', '\n\n', texto)  # Garante que parágrafos fiquem com duas quebras de linha

    # Tratar os hífens no final das linhas
    texto = re.sub(r'-\s+', '', texto)

    # Remover cabeçalhos e rodapés
    texto = re.sub(r'Header Text|Footer Text', ' ', texto)

    # Remover caracteres invisíveis
    texto = texto.replace('\u200b', '').strip()

    # Converter caracteres especiais
    texto = texto.encode('utf-8', 'ignore').decode('utf-8')

    return texto

# Função para extrair texto do PDF
def extrair_texto_pdf(arquivos_carregados):
    # Tentativa inicial de extração com PyPDF2 (Para PDFs baseados em texto)
    try:
        reader = PyPDF2.PdfReader(arquivos_carregados)
        texto_extraido = ""
        for pagina in reader.pages:
            texto_extraido += pagina.extract_text()

        if texto_extraido:
            return limpar_texto(texto_extraido)

    except Exception as e:
        st.error(f"ERRO: Erro ao tentar extrair texto com PyPDF2: {e}")

    # Caso o PyPDF2 falhe, tentamos com pdfminer (maior compatibilidade com PDFs complexos)
    try:
        texto_extraido = extract_text(arquivos_carregados)
        return limpar_texto(texto_extraido)

    except Exception as e:
        st.error(f"ERRO: Erro ao tentar extrair texto com pdfminer: {e}")

    return None  # Retorna None se falhar em todas as tentativas

# Função para extrair texto de PDFs digitalizados
def extrair_texto_ocr(arquivos_carregados):
    try:
        # Lê o arquivo carregado como bytes
        arquivo_bytes = arquivos_carregados.read()
        arquivo_buffer = BytesIO(arquivo_bytes)

        # Abre o arquivo PDF com fitz(PyMuPDF)
        doc = fitz.open(stream=arquivo_buffer.getvalue(), filetype="pdf")
        texto_extraido = ""

        # Iterar sobre as páginas do documento
        for num_pagina in range(len(doc)):
            st.write(f"Processando página com {num_pagina + 1}...")
            pagina = doc.load_page(num_pagina)

            # Converte a página em imagem com DPI alta para melhorar a resolução do OCR
            pix = pagina.get_pixmap(dpi=300)
        
            # Converte o pixmap em uma imagem PIL
            img = Image.open(io.BytesIO(pix.pil_tobytes()))
            
            # Converte a imagem PIL para um formato compatível (RGB)
            img = img.convert('RGB')

            # Aplica o OCR à imagem da página
            ocr_result = pytesseract.image_to_string(img)
            st.write(f"Resultado do OCR na página {num_pagina + 1}: {ocr_result[:100]}...")  # Exibe os primeiros 100 caracteres

            # Adiciona o texto OCR extraído ao resultado final
            texto_extraido += ocr_result
        
        return limpar_texto(texto_extraido)

    except Exception as e:
        st.error(f"ERRO: Erro ao tentar extrair texto com OCR: {e}.  "
                  f"Verifique se o arquivo é realmente digitalizado. "
                  f"Se ele for, procure o Carlos e mande ele resolver kkkkkkkkkkkkk")

    return None

# Botões para selecionar o tipo de PDF
st.write("### Selecione o tipo de arquivo:")
opcao = st.radio("Escolha o tipo de arquivo:", ("PDF com texto", "PDF digitalizado"))

# Upload de múltiplos arquivos
st.write("### Adicione os arquivos abaixo")
arquivos_carregados = st.file_uploader("Arraste ou selecione os arquivos.", type="pdf", accept_multiple_files=True, help="Faça o upload aqui!")

# Processar cada arquivo PDF carregado
if arquivos_carregados:
    for arquivo_carregado in arquivos_carregados:
        st.write(f"Processando {arquivo_carregado.name}...")

        if opcao == "PDF com texto":
            # Apenas processar se for PDF com texto
            texto_extraido = extrair_texto_pdf(arquivo_carregado)
            if texto_extraido:
                st.text_area(f"Conteúdo extráido de {arquivo_carregado.name}:", texto_extraido, height=300)
            else:
                st.error(f"ERRO: Erro ao extrair o texto de {arquivo_carregado.name}.")
            
        elif opcao == "PDF digitalizado":
            # Para processar se for PDF digitalizado
            texto_extraido = extrair_texto_ocr(arquivo_carregado)
            if texto_extraido:
                st.text_area(f"Conteúdo extraído de {arquivo_carregado.name}:", texto_extraido, height=300)
            else:
                st.error(f"ERRO: Erro ao extrair o texto de {arquivo_carregado.name}.")
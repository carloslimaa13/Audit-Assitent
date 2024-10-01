# Importando as bibliotecas
import streamlit as st
import PyPDF2
from pdfminer.high_level import extract_text
import re

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


# Upload de múltiplos arquivos
st.write("### Adicione os arquivos abaixo")
arquivos_carregados = st.file_uploader("Arraste ou selecione os arquivos.", type="pdf", accept_multiple_files=True, help="Faça o upload aqui!")

# Processar cada arquivo PDF carregado
if arquivos_carregados:
    for arquivo_carregado in arquivos_carregados:
        st.write(f"Processando {arquivo_carregado.name}...")
        texto_extraido = extrair_texto_pdf(arquivo_carregado)
        if texto_extraido:
            st.text_area(f"Conteúdo extraído de {arquivo_carregado.name}:", texto_extraido, height=300)
        else:
            st.error(f"ERRO: Erro ao extrair o texto de {arquivo_carregado.name}.")

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

# Função para buscar palavras ou frases nos textos extraídos
def buscar_texto(palavra, textos):
    resultados = {}
    # Usa uma expressão regular para garantir que a busca seja por palavra exata
    padrao = rf'\b{re.escape(palavra)}\b'  # Adiciona delimitadores de palavra

    for nome_arquivo, texto in textos.items():
        paragrafos = texto.split('\n\n')  # Separa o texto por parágrafos (duas quebras de linha)
        encontrados = []  # Lista para armazenar os parágrafos encontrados
        for paragrafo in paragrafos:
            if re.search(padrao, paragrafo, re.IGNORECASE):  # Busca pela palavra exata, ignorando maiúsculas/minúsculas
                encontrados.append(paragrafo)
        if encontrados:
            resultados[nome_arquivo] = encontrados  # Adiciona os parágrafos encontrados ao dicionário
    return resultados

# Upload de múltiplos arquivos
st.write("### Adicione os arquivos abaixo")
arquivos_carregados = st.file_uploader("Arraste ou selecione os arquivos.", type="pdf", accept_multiple_files=True, help="Faça o upload aqui!")

# Dicionário para armazenar o conteúdo extraído de cada arquivo
textos_pdf = {}

# Processar cada arquivo PDF carregado
if arquivos_carregados:
    for arquivo_carregado in arquivos_carregados:
        st.write(f"Processando {arquivo_carregado.name}...")
        texto_extraido = extrair_texto_pdf(arquivo_carregado)
        if texto_extraido:
            textos_pdf[arquivo_carregado.name] = texto_extraido
        else:
            st.error(f"ERRO: Erro ao extrair o texto de {arquivo_carregado.name}.")

# Campo para o usuário digitar a palavra ou frase que deseja buscar
palavra_busca = st.text_input("Digite a palavra ou frase que deseja buscar:")

# Botão para realizar a busca
if st.button("Buscar"):
    if palavra_busca and textos_pdf:
        resultados_busca = buscar_texto(palavra_busca, textos_pdf)
        if resultados_busca:
            for nome_arquivo, paragrafos in resultados_busca.items():
                with st.expander(f"Resultados para '{palavra_busca}' em {nome_arquivo}"):
                    for paragrafo in paragrafos:
                        st.write(paragrafo)  # Exibe cada parágrafo encontrado
        else:
            st.write("Nenhum resultado encontrado para a busca.")
    else:
        st.write("Por favor, insira uma palavra/frase válida e carregue arquivos PDF.")

import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

# Função para carregar o arquivo CSV
def load_data(file):
    try:
        # Tenta carregar com delimitador padrão ';'
        data = pd.read_csv(
            file, 
            sep=';',  # Delimitador padrão
            engine='python',  # Motor mais tolerante
            on_bad_lines='skip'  # Ignora linhas problemáticas
        )
        # Normalizar os nomes das colunas (remover espaços e usar caixa alta)
        data.columns = data.columns.str.strip().str.upper()
        return data
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo CSV: {e}")
        return None

# Função para aplicar gradiente nas células (faixa hora por dia da semana)
def apply_gradient(df):
    styles = df.copy()
    for col in df.columns:
        max_val = df[col].max()
        styles[col] = df[col].apply(
            lambda x: f"background-color: rgba(255, {255 - int((x / max_val) * 255)}, {255 - int((x / max_val) * 255)}, 1)"
            if pd.notna(x) else ""
        )
    return styles

# Função para gerar o PDF
def generate_pdf(data, title="CARTÃO PROGRAMA"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Adicionar Título
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)

    # Adicionar tabela
    pdf.set_font("Arial", size=10)
    col1_width = 80
    col2_width = 100

    pdf.cell(col1_width, 10, "FAIXA HORA", 1, 0, 'C')
    pdf.cell(col2_width, 10, "LOGRADOUROS", 1, 1, 'C')

    for row in data.itertuples():
        pdf.cell(col1_width, 10, str(row.FAIXA_HORA_1), 1, 0, 'C')
        pdf.cell(col2_width, 10, str(row.LOGRADOURO), 1, 1, 'C')

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# Configuração do Streamlit
st.title("Análise de Ocorrências com Filtros e Relatório")

# Sidebar: Upload do arquivo CSV
st.sidebar.header("Configurações")
uploaded_file = st.sidebar.file_uploader("Selecione o Arquivo CSV", type=["csv"])

if uploaded_file:
    data = load_data(uploaded_file)
    
    if data is not None:
        # Exibir colunas disponíveis
        st.write("Colunas disponíveis no CSV:")
        st.write(data.columns.tolist())

        # Verificar se as colunas necessárias existem no CSV
        required_columns = ["DESCR_NATUREZA_PRINCIPAL", "MUNICIPIO", "SETOR", "DIA_DA_SEMANA_FATO", "FAIXA_HORA_1", "TENTADO_CONSUMADO_PRINCIPAL"]
        missing_columns = [col for col in required_columns if col not in data.columns]

        if missing_columns:
            st.error(f"As seguintes colunas obrigatórias estão ausentes no arquivo CSV: {missing_columns}")
        else:
            # Sidebar: Filtros
            st.sidebar.header("Filtros")
            nature_filter = st.sidebar.multiselect("Selecione Natureza(s):", data["DESCR_NATUREZA_PRINCIPAL"].unique())
            municipio_filter = st.sidebar.selectbox("Selecione Município:", data["MUNICIPIO"].unique())
            setor_filter = st.sidebar.selectbox("Selecione Setor:", data["SETOR"].unique())

            # Aplicar filtros
            filtered_data = data[
                (data["DESCR_NATUREZA_PRINCIPAL"].isin(nature_filter) if nature_filter else True) &
                (data["MUNICIPIO"] == municipio_filter if municipio_filter else True) &
                (data["SETOR"] == setor_filter if setor_filter else True)
            ]

            # Exibir dados filtrados
            st.subheader("Dados Filtrados")
            st.dataframe(filtered_data)

            # Gráfico 1: Quantidade de registros por dia da semana
            st.subheader("Quantidade de Registros por Dia da Semana")
            registros_por_dia = filtered_data["DIA_DA_SEMANA_FATO"].value_counts().sort_index()
            fig1 = px.bar(
                registros_por_dia,
                x=registros_por_dia.index,
                y=registros_por_dia.values,
                title="Registros por Dia da Semana",
                labels={"x": "Dia da Semana", "y": "Quantidade de Registros"}
            )
            st.plotly_chart(fig1)

            # Gráfico 2: Faixa Hora 1 por Dia da Semana (com gradiente)
            st.subheader("Quantidade (Faixa Hora 1) por Dia da Semana")
            faixa_hora_pivot = (
                filtered_data.pivot_table(
                    index="DIA_DA_SEMANA_FATO",
                    columns="FAIXA_HORA_1",
                    aggfunc="size",
                    fill_value=0
                )
            )
            st.dataframe(faixa_hora_pivot.style.apply(apply_gradient, axis=None))

            # Gráfico 3: Pizza (Tentado x Consumado)
            st.subheader("Tentado x Consumado")
            tentado_consumado = filtered_data["TENTADO_CONSUMADO_PRINCIPAL"].value_counts()
            fig3 = px.pie(
                names=tentado_consumado.index,
                values=tentado_consumado.values,
                title="Tentado x Consumado"
            )
            st.plotly_chart(fig3)

            # Botão para gerar PDF
            st.sidebar.subheader("Gerar Relatório")
            if st.sidebar.button("Baixar PDF"):
                # Criar tabela para o PDF (ordenada por quantidade)
                pdf_data = (
                    filtered_data.groupby("FAIXA_HORA_1")["LOGRADOURO"]
                    .count()
                    .reset_index()
                    .rename(columns={"LOGRADOURO": "Quantidade"})
                    .sort_values(by="Quantidade", ascending=False)
                )
                
                # Gerar PDF
                pdf_file = generate_pdf(pdf_data)
                
                # Botão para download
                st.sidebar.success("PDF Gerado com Sucesso!")
                st.sidebar.download_button(
                    label="Baixar PDF",
                    data=pdf_file,
                    file_name="relatorio_ocorrencias.pdf",
                    mime="application/pdf"
                )

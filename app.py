import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

# Função para carregar o arquivo CSV
def load_data(file):
    try:
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
    col1_width = 80  # Largura da coluna "FAIXA HORA"
    col2_width = 100  # Largura da coluna "LOGRADOURO"
    col3_width = 100  # Largura da coluna "BAIRRO"

    pdf.cell(col1_width, 10, "FAIXA HORA", 1, 0, 'C')
    pdf.cell(col2_width, 10, "LOGRADOURO", 1, 0, 'C')
    pdf.cell(col3_width, 10, "BAIRRO", 1, 1, 'C')

    # Verificar os dados antes de iterar
    if data.empty:
        pdf.cell(0, 10, "Nenhum dado disponível para gerar o PDF.", 1, 1, 'C')
    else:
        for row in data.itertuples():
            pdf.cell(col1_width, 10, str(row.FAIXA_HORA_1), 1, 0, 'C')
            pdf.cell(col2_width, 10, str(row.LOGRADOURO), 1, 0, 'C')
            pdf.cell(col3_width, 10, str(row.BAIRRO), 1, 1, 'C')

    # Salvar o PDF como bytes
    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))  # Escreve o PDF no buffer
    pdf_output.seek(0)  # Retorna ao início do buffer
    return pdf_output

# Configuração do Streamlit
st.title("Análise de Ocorrências com Filtros e Relatório")

# Sidebar: Upload do arquivo CSV
st.sidebar.header("Configurações")
uploaded_file = st.sidebar.file_uploader("Selecione o Arquivo CSV", type=["csv"])

if uploaded_file:
    data = load_data(uploaded_file)
    
    if data is not None:
        st.write("Colunas disponíveis no CSV:")
        st.write(data.columns.tolist())

        # Verificar colunas obrigatórias
        required_columns = ["DESCR_NATUREZA_PRINCIPAL", "MUNICIPIO", "SETOR", "DIA_DA_SEMANA_FATO", "FAIXA_HORA_1", "LOGRADOURO", "BAIRRO"]
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
            if not filtered_data.empty:
                st.subheader("Dados Filtrados")
                st.dataframe(filtered_data)

                # Gráfico 1: Quantidade de registros por dia da semana
                st.subheader("Quantidade de Registros por Dia da Semana")
                registros_por_dia = filtered_data["DIA_DA_SEMANA_FATO"].value_counts().sort_index()

                if not registros_por_dia.empty:
                    fig1 = px.bar(
                        registros_por_dia,
                        x=registros_por_dia.index,
                        y=registros_por_dia.values,
                        title="Registros por Dia da Semana",
                        labels={"x": "Dia da Semana", "y": "Quantidade de Registros"}
                    )
                    st.plotly_chart(fig1)
                else:
                    st.warning("Nenhum dado disponível para exibir no gráfico.")

                # Preparar dados para PDF
                pdf_data = (
                    filtered_data[["FAIXA_HORA_1", "LOGRADOURO", "BAIRRO"]]  # Manter colunas necessárias
                    .dropna()  # Remover linhas com valores ausentes
                    .sort_values(by="FAIXA_HORA_1")  # Ordenar pela faixa horária
                )

                # Gerar PDF
                st.sidebar.subheader("Gerar Relatório")
                if st.sidebar.button("Baixar PDF"):
                    pdf_file = generate_pdf(pdf_data)
                    st.sidebar.success("PDF Gerado com Sucesso!")
                    st.sidebar.download_button(
                        label="Baixar PDF",
                        data=pdf_file,
                        file_name="relatorio_ocorrencias.pdf",
                        mime="application/pdf"
                    )
            else:
                st.warning("Nenhum dado disponível após aplicar os filtros.")

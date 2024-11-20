import streamlit as st
from utils.data_processing import load_data, filter_data, validate_columns
from utils.charts import create_bar_chart
from utils.maps import plot_crime_map, plot_heatmap, plot_route_map
from utils.pdf_generator import generate_pdf

st.title("Análise de Ocorrências com Filtros e Relatório")

# Upload do CSV
uploaded_file = st.sidebar.file_uploader("Selecione o Arquivo CSV", type=["csv"])

if uploaded_file:
    # Carregar os dados
    data = load_data(uploaded_file)

    if data is not None:
        # Validar colunas necessárias
        required_columns = ["DESCR_NATUREZA_PRINCIPAL", "MUNICIPIO", "SETOR", "DIA_DA_SEMANA_FATO", 
                            "FAIXA_HORA_1", "LATITUDE", "LONGITUDE", "LOGRADOURO", "BAIRRO"]
        try:
            validate_columns(data, required_columns)
        except ValueError as e:
            st.error(str(e))
            st.stop()

        # Configurar filtros
        st.sidebar.header("Filtros")
        nature_filter = st.sidebar.multiselect("Selecione Natureza(s):", data["DESCR_NATUREZA_PRINCIPAL"].unique())
        municipio_filter = st.sidebar.selectbox("Selecione Município:", data["MUNICIPIO"].unique())
        setor_filter = st.sidebar.selectbox("Selecione Setor:", data["SETOR"].unique())

        # Aplicar filtros
        filtered_data = filter_data(data, nature_filter, municipio_filter, setor_filter)

        if not filtered_data.empty:
            st.subheader("Dados Filtrados")
            st.dataframe(filtered_data)

            # Gráficos
            st.subheader("Gráfico de Registros por Dia da Semana")
            st.plotly_chart(create_bar_chart(filtered_data, "DIA_DA_SEMANA_FATO"))

            # Mapas
            st.subheader("Mapa de Pontos de Crimes")
            st.map(plot_crime_map(filtered_data))

            st.subheader("Mapa de Calor")
            st.map(plot_heatmap(filtered_data))

            st.subheader("Mapa de Caminho")
            st.map(plot_route_map(filtered_data))

            # PDF
            st.sidebar.subheader("Gerar Relatório")
            if st.sidebar.button("Gerar PDF"):
                pdf_file = generate_pdf(filtered_data)
                st.sidebar.download_button(
                    label="Baixar PDF",
                    data=pdf_file,
                    file_name="relatorio_ocorrencias.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("Nenhum dado disponível após aplicar os filtros.")

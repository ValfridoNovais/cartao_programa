import pandas as pd

def load_data(file):
    try:
        data = pd.read_csv(file, sep=';', engine='python', on_bad_lines='skip')
        data.columns = data.columns.str.strip().str.upper()

        # Substituir vírgulas por pontos e converter para float
        if "LATITUDE" in data.columns and "LONGITUDE" in data.columns:
            data["LATITUDE"] = data["LATITUDE"].str.replace(",", ".").astype(float)
            data["LONGITUDE"] = data["LONGITUDE"].str.replace(",", ".").astype(float)

        return data
    except Exception as e:
        raise ValueError(f"Erro ao carregar o arquivo: {e}")

def validate_columns(data, required_columns):
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise ValueError(f"As seguintes colunas estão ausentes no arquivo CSV: {missing_columns}")

def filter_data(data, nature_filter, municipio_filter, setor_filter):
    filtered_data = data[
        (data["DESCR_NATUREZA_PRINCIPAL"].isin(nature_filter) if nature_filter else True) &
        (data["MUNICIPIO"] == municipio_filter if municipio_filter else True) &
        (data["SETOR"] == setor_filter if setor_filter else True)
    ]

    # Verificar se colunas essenciais foram mantidas
    required_columns = ["LATITUDE", "LONGITUDE", "LOGRADOURO", "BAIRRO"]
    for col in required_columns:
        if col not in filtered_data.columns:
            raise ValueError(f"A coluna '{col}' foi perdida após o filtro.")

    return filtered_data

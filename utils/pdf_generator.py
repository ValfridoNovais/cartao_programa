from fpdf import FPDF
from io import BytesIO

def generate_pdf(data, title="CARTÃO PROGRAMA"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=10)
    col1_width = 80
    col2_width = 100
    col3_width = 100

    # Garantir que as colunas essenciais existem no DataFrame
    required_columns = ["FAIXA_HORA_1", "LOGRADOURO", "BAIRRO"]
    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"A coluna '{col}' está ausente no DataFrame para o PDF.")

    # Cabeçalho da tabela
    pdf.cell(col1_width, 10, "FAIXA HORA", 1, 0, 'C')
    pdf.cell(col2_width, 10, "LOGRADOURO", 1, 0, 'C')
    pdf.cell(col3_width, 10, "BAIRRO", 1, 1, 'C')

    # Preencher a tabela com os dados
    for row in data.itertuples():
        pdf.cell(col1_width, 10, str(row.FAIXA_HORA_1), 1, 0, 'C')
        pdf.cell(col2_width, 10, str(row.LOGRADOURO), 1, 0, 'C')
        pdf.cell(col3_width, 10, str(row.BAIRRO), 1, 1, 'C')

    # Salvar o PDF como bytes
    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))
    pdf_output.seek(0)
    return pdf_output

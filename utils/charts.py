import plotly.express as px

def create_bar_chart(data, column):
    counts = data[column].value_counts().sort_index()
    fig = px.bar(
        x=counts.index,
        y=counts.values,
        labels={"x": column, "y": "Quantidade"},
        title=f"Registros por {column}"
    )
    return fig

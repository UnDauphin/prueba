import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import geopandas as gpd
import numpy as np

df_C = pd.read_csv("datos_contributivo.csv", dtype={"CodDepto":"str"})
df_S = pd.read_csv("datos_subsidiado.csv", dtype={"CodDepto":"str"})
df_E = pd.read_csv("datos_especial.csv", dtype={"CodDepto":"str"})

# Cargar shapefile Colombia
mapa_col = gpd.read_file("coordenadas/COLOMBIA/COLOMBIA.shp", encoding="latin1")

# Unir con datos por régimen
geo_df_C = mapa_col.merge(df_C, left_on="DPTO_CCDGO", right_on="CodDepto")
geo_df_S = mapa_col.merge(df_S, left_on="DPTO_CCDGO", right_on="CodDepto")
geo_df_E = mapa_col.merge(df_E, left_on="DPTO_CCDGO", right_on="CodDepto")

# ======================
# 2. Funciones para gráficos
# ======================

# Boxplot comparativo
def grafico_boxplot():
    df_box = pd.DataFrame({
        "Contributivo": geo_df_C["NumPersonas"],
        "Subsidiado": geo_df_S["NumPersonas"],
        "Especial": geo_df_E["NumPersonas"]
    })
    df_long = df_box.melt(var_name="Régimen", value_name="NumPersonas")
    fig = px.box(df_long, x="Régimen", y="NumPersonas", title="Distribución por Régimen")
    return fig

# Mapas por régimen
def mapa_regimen(geo_df, nombre):
    fig = px.choropleth(
        geo_df,
        geojson=geo_df.geometry.__geo_interface__,
        locations=geo_df.index,
        color="NumPersonas",
        hover_name="Departamento",
        title=f"Afiliados Régimen {nombre}",
        color_continuous_scale="Viridis"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    return fig

# ======================
# 3. Configuración de Dash
# ======================
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Análisis Afiliados por Régimen", style={'textAlign': 'center'}),

    dcc.Tabs([
        dcc.Tab(label='Contexto', children=[
            html.H3("Contexto"),
            html.P("""
                Esta aplicación analiza la distribución de afiliados al sistema de salud en Colombia,
                distinguiendo entre los regímenes Contributivo, Subsidiado y Especial.
                Los datos originales provienen de registros municipales del año 2022 y han sido
                agregados a nivel departamental para facilitar la visualización geográfica.
            """),
            html.P([
                "Fuente de datos: ",
                html.A("Número de afiliados por departamento, municipio y régimen",
                       href="https://www.datos.gov.co/Salud-y-Protecci-n-Social/N-mero-de-afiliados-por-departamento-municipio-y-r/hn4i-593p/about_data",
                       target="_blank")
            ])
        ]),
        dcc.Tab(label='Boxplot Comparativo', children=[
            html.H3("Distribución por Régimen"),
            dcc.Graph(figure=grafico_boxplot()),
            html.P("""
                El boxplot comparativo permite observar cómo varía la cantidad de afiliados 
                en cada régimen entre los departamentos:
            """),
            html.Ul([
                html.Li("El régimen Contributivo presenta una gran dispersión, con valores muy altos en algunos departamentos urbanos (outliers claros)."),
                html.Li("El régimen Subsidiado muestra mayor concentración en valores medios, reflejando su peso en regiones con población vulnerable."),
                html.Li("El régimen Especial tiene menos afiliados y se distribuye de manera más homogénea, aunque con menor magnitud general."),
            ]),
            html.P("""
                En conjunto, los gráficos resaltan las diferencias estructurales entre regímenes
                y evidencian desigualdades en la cobertura a nivel territorial.
            """)
        ]),
        dcc.Tab(label='Régimen Contributivo', children=[
            html.H3("Mapa Régimen Contributivo"),
            dcc.Graph(figure=mapa_regimen(geo_df_C, "Contributivo"))
        ]),
        dcc.Tab(label='Régimen Subsidiado', children=[
            html.H3("Mapa Régimen Subsidiado"),
            dcc.Graph(figure=mapa_regimen(geo_df_S, "Subsidiado"))
        ]),
        dcc.Tab(label='Régimen Especial', children=[
            html.H3("Mapa Régimen Especial"),
            dcc.Graph(figure=mapa_regimen(geo_df_E, "Especial"))
        ]),
        dcc.Tab(label='Conclusiones', children=[
            html.H3("Conclusiones"),
            html.P("""
                El análisis muestra disparidades claras en la cantidad de afiliados entre departamentos
                y entre regímenes. El régimen contributivo concentra la mayor cantidad de afiliados en
                las principales áreas urbanas, mientras que el subsidiado predomina en regiones con
                mayor vulnerabilidad económica. 
                
                Estos resultados resaltan la necesidad de políticas diferenciadas y focalizadas 
                según el contexto regional, así como la importancia de actualizar continuamente
                los datos para una mejor toma de decisiones.
            """),
            html.P([
                "Fuente: ",
                html.A("Datos Abiertos Colombia", 
                       href="https://www.datos.gov.co/Salud-y-Protecci-n-Social/N-mero-de-afiliados-por-departamento-municipio-y-r/hn4i-593p/about_data",
                       target="_blank")
            ])
        ])
    ])
])

# ======================
# 4. Correr la app
# ======================
if __name__ == '__main__':
    app.run(debug=True)












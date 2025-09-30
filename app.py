import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import geopandas as gpd

# ======================
# 2. Cargar y limpiar datos
# ======================
df = pd.read_csv("Número_de_afiliados_por_departamento,_municipio_y_régimen_20250914.csv")

# Limpieza del dataset
df["NumPersonas"] = df["NumPersonas"].astype(str).str.replace('.', '', regex=False).astype(int)
df = df[df["Municipio"] != "NO APLICA"]

# Agrupaciones por régimen
df_C = pd.read_csv("datos_contributivo.csv", dtype={"CodDepto":"str"})
df_S = pd.read_csv("datos_subsidiado.csv", dtype={"CodDepto":"str"})
df_E = pd.read_csv("datos_especial.csv", dtype={"CodDepto":"str"})


# Cargar shapefile
mapa_col = gpd.read_file("coordenadas/COLOMBIA/COLOMBIA.shp", encoding="latin1")

# Unir con datos por régimen
geo_df_C = mapa_col.merge(df_C, left_on="DPTO_CCDGO", right_on="CodDepto")
geo_df_S = mapa_col.merge(df_S, left_on="DPTO_CCDGO", right_on="CodDepto")
geo_df_E = mapa_col.merge(df_E, left_on="DPTO_CCDGO", right_on="CodDepto")

# ======================
# 3. Funciones para gráficos
# ======================
def grafico_boxplot():
    df_box = pd.DataFrame({
        "Contributivo": geo_df_C["NumPersonas"],
        "Subsidiado": geo_df_S["NumPersonas"],
        "Especial": geo_df_E["NumPersonas"]
    })
    df_long = df_box.melt(var_name="Régimen", value_name="NumPersonas")
    fig = px.box(df_long, x="Régimen", y="NumPersonas", title="Distribución por Régimen")
    return fig

def mapa_regimen(geo_df, nombre, color_scale="Viridis"):
    fig = px.choropleth(
        geo_df,
        geojson=geo_df.geometry.__geo_interface__,
        locations=geo_df.index,
        color="NumPersonas",
        hover_name="Departamento",
        title=f"Afiliados Régimen {nombre}",
        color_continuous_scale=color_scale
    )
    fig.update_geos(fitbounds="locations", visible=False)
    return fig

# ======================
# 4. App con filtros interactivos
# ======================
app = dash.Dash(__name__)
server = app.server

# Paletas de colores disponibles
color_scales = [
    "Viridis", "Plasma", "Cividis", "Inferno", "Magma", "Turbo", "Blues", "Greens", "Reds"
]

app.layout = html.Div([
    html.H1("Análisis Afiliados por Régimen", style={'textAlign': 'center'}),

    dcc.Tabs([
        dcc.Tab(label='Boxplot Comparativo', children=[
            dcc.Graph(figure=grafico_boxplot())
        ]),
        dcc.Tab(label='Régimen Contributivo', children=[
            dcc.Graph(figure=mapa_regimen(geo_df_C, "Contributivo"))
        ]),
        dcc.Tab(label='Régimen Subsidiado', children=[
            dcc.Graph(figure=mapa_regimen(geo_df_S, "Subsidiado"))
        ]),
        dcc.Tab(label='Régimen Especial', children=[
            dcc.Graph(figure=mapa_regimen(geo_df_E, "Especial"))
        ]),
        dcc.Tab(label='Filtro Interactivo', children=[
            html.H3("Selecciona Régimen, Departamento y Color"),
            dcc.Dropdown(
                id='dropdown-regimen',
                options=[
                    {'label': 'Contributivo', 'value': 'C'},
                    {'label': 'Subsidiado', 'value': 'S'},
                    {'label': 'Especial', 'value': 'E'}
                ],
                value='C',
                clearable=False
            ),
            dcc.Dropdown(
                id='dropdown-depto',
                options=[{'label': d, 'value': d} for d in df["Departamento"].unique()],
                value=None,
                placeholder="Selecciona un Departamento (opcional)"
            ),
            dcc.Dropdown(
                id='dropdown-color',
                options=[{'label': c, 'value': c} for c in color_scales],
                value="Viridis",
                clearable=False
            ),
            dcc.Graph(id='mapa-interactivo')
        ])
    ])
])

# ======================
# 5. Callbacks para interactividad
# ======================
@app.callback(
    Output('mapa-interactivo', 'figure'),
    [Input('dropdown-regimen', 'value'),
     Input('dropdown-depto', 'value'),
     Input('dropdown-color', 'value')]
)
def actualizar_mapa(regimen, depto, color_scale):
    if regimen == 'C':
        geo_df = geo_df_C.copy()
        nombre = "Contributivo"
    elif regimen == 'S':
        geo_df = geo_df_S.copy()
        nombre = "Subsidiado"
    else:
        geo_df = geo_df_E.copy()
        nombre = "Especial"

    if depto:
        geo_df = geo_df[geo_df["Departamento"] == depto]

    return mapa_regimen(geo_df, nombre, color_scale)

# ======================
# 6. Ejecutar la app
# ======================
if __name__ == '__main__':
    app.run(debug=True)







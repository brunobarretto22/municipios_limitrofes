# streamlit run .\municipios_limitrofes_publicação2.py

# Instalar bibliotecas necessárias com:
# pip install geopandas
# pip install streamlit
# pip install folium
# pip install streamlit_folium

import geopandas as gpd
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.header('Consulta de municípios limítrofes com mapa interativo')

# Carregar o shapefile dos municípios do Mato Grosso (MT)
gdf_municipios = gpd.read_file('BR_Municipios_2024_MT.shp')
gdf_estado = gpd.read_file('MT_UF_2024.shp')

# Seleção da UF
siglas_uf = gdf_municipios['SIGLA_UF'].drop_duplicates().sort_values()
uf_selecionada = st.selectbox("Selecione o Estado (UF):", siglas_uf)

# Filtra municípios pela UF selecionada
municipios_da_uf = gdf_municipios[gdf_municipios['SIGLA_UF'] == uf_selecionada]
nomes_municipios_da_uf = municipios_da_uf['NM_MUN'].sort_values()

# Seleção do Estado
estado_geom = gdf_estado[gdf_estado['SIGLA_UF'] == uf_selecionada]

# Seleção do município
municipio_selecionado = st.selectbox("Selecione o município:", nomes_municipios_da_uf)
municipio_geom = municipios_da_uf[municipios_da_uf['NM_MUN'] == municipio_selecionado]

if not municipio_geom.empty:
    # Identifica municípios limítrofes
    limitrofes = municipios_da_uf[municipios_da_uf.touches(municipio_geom.geometry.squeeze())]

    # Cálculo do centróide para o mapa
    centroide = municipio_geom.geometry.centroid.iloc[0]
    centroid_y, centroid_x = centroide.y, centroide.x

    # Cria o mapa base com camadas extras
    m = folium.Map(location=[centroid_y, centroid_x], zoom_start=8, tiles=None)

    folium.TileLayer('opentopomap', name='OpenTopoMap',show=False).add_to(m)
    folium.TileLayer('Esri.NatGeoWorldMap', name='Esri.NatGeoWorldMap',show=False).add_to(m)
    folium.TileLayer('NASAGIBS.ViirsEarthAtNight2012', name='VisEarthAtNight2012',show=False).add_to(m)
    folium.TileLayer('Stadia.AlidadeSatellite', name='ImageSatellite',show=False).add_to(m)
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)

    # Polígono do Estado selecionado (destaque cinza)
    folium.GeoJson(
        estado_geom,
        name='Estado Selecionado',
        style_function=lambda x: {'color': 'cinza', 'weight': 2, 'fillOpacity': 0.1},
        control=False
    ).add_to(m)

    # Polígono do município selecionado (destaque vermelho)
    folium.GeoJson(
        municipio_geom,
        name='Município Selecionado',
        style_function=lambda x: {'color': 'red', 'weight': 3, 'fillOpacity': 0.1}
    ).add_to(m)

    # Polígonos dos municípios limítrofes (destaque azul)
    folium.GeoJson(
        limitrofes,
        name='Limítrofes',
        style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0.1}
    ).add_to(m)

    folium.GeoJson(
    municipio_geom,
    name='Município Selecionado',
    style_function=lambda x: {'color': 'red', 'weight': 3, 'fillOpacity': 0.1},
    tooltip=municipio_geom['NM_MUN'].values[0]
    ).add_to(m)

    folium.GeoJson(
    limitrofes,
    name='Limítrofes',
    style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0.1},
    tooltip=folium.GeoJsonTooltip(fields=['NM_MUN'],aliases=[''])
    ).add_to(m)

    # Controle das camadas de fundo
    folium.LayerControl().add_to(m)
    
    # Mostrar mapa interativo no Streamlit
    # st_folium(m, width=700, height=500)
    col1, col2 = st.columns(2)
    with col1:
        st_folium(m, width=None, height=400)
    # m

#     # Exibe a lista dos municípios limítrofes com UF
else:
    st.write("Município selecionado não encontrado na base")

# Quantidade de municípios limítrofes
qtd_limitrofes = len(limitrofes)

# Gera lista com município, UF e contagem de limítrofes
contagem_limitrofes = {}
for idx, row in limitrofes.iterrows():
    geom = row.geometry
    vizinhos = municipios_da_uf[municipios_da_uf.geometry.touches(geom)]
    contagem_limitrofes[row['NM_MUN']] = len(vizinhos)

df_limitrofes = pd.DataFrame(list(contagem_limitrofes.keys()), columns=['Município'])
df_limitrofes['UF'] = uf_selecionada

# Ajusta índice para iniciar em 1
df_limitrofes.index = df_limitrofes.index + 1

with col2:
    st.write(f"O município de **{municipio_selecionado} - {uf_selecionada}** tem **{qtd_limitrofes}** municípios limítrofes, a saber:")
    st.dataframe(df_limitrofes)

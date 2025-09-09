# streamlit run .\municipios_limitrofes_publicação.py

import geopandas as gpd
import streamlit as st
import folium
from streamlit_folium import st_folium

st.header('Consulta de municípios limítrofes com mapa interativo')
gdf_municipios = gpd.read_file('BR_Municipios_2024_MT.shp')
print(gdf_municipios)

# Seleção do estado
siglas_uf = gdf_municipios['SIGLA_UF'].drop_duplicates().sort_values()
uf_selecionada = st.selectbox("Selecione o Estado (UF):", siglas_uf)

# Filtra municípios da UF escolhida
municipios_da_uf = gdf_municipios[gdf_municipios['SIGLA_UF'] == uf_selecionada]
nomes_municipios_da_uf = municipios_da_uf['NM_MUN'].sort_values()

# Seleção do município
municipio_selecionado = st.selectbox("Selecione o município:", nomes_municipios_da_uf)
municipio_geom = municipios_da_uf[municipios_da_uf['NM_MUN'] == municipio_selecionado]

if not municipio_geom.empty:
    limitrofes = municipios_da_uf[municipios_da_uf.touches(municipio_geom.geometry.squeeze())]

    # Centróide para centralizar o mapa
    centroide = municipio_geom.geometry.centroid.iloc[0]
    centroid_y, centroid_x = centroide.y, centroide.x

    # Criar mapa Folium com tile Esri World Imagery
    # m = folium.Map(location=[centroid_y, centroid_x], zoom_start=8, tiles='Esri.WorldImagery')
    m = folium.Map(location=[centroid_y, centroid_x], zoom_start=8, tiles='OpenStreetMap')
    
    # Adiciona polígono do município selecionado em destaque (ex: borda vermelha)
    folium.GeoJson(
        municipio_geom,
        name='Município Selecionado',
        style_function=lambda x: {'color': 'red', 'weight': 3, 'fillOpacity': 0.1}
    ).add_to(m)

    # Adiciona polígonos dos municípios limítrofes (ex: borda azul)
    folium.GeoJson(
        limitrofes,
        name='Limítrofes',
        style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0.1}
    ).add_to(m)

    # Mostrar mapa interativo no Streamlit
    st_folium(m, width=700, height=500)

    # Exibir lista dos municípios limítrofes com UF
    lista_limitrofes = limitrofes.apply(lambda row: f"{row['NM_MUN']} - {row['SIGLA_UF']}", axis=1).tolist()
    st.write("Municípios Limítrofes (Município - UF):", lista_limitrofes)
else:

    st.write("Município selecionado não encontrado na base")
st_data = st_folium(m, width=700, height=500)

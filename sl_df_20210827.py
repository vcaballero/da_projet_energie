#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 21:37:41 2021

@author: vcaballero
"""
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt


from urllib.error import URLError
#import plotly.figure_factory as ff
#import matplotlib.pyplot as plt


@st.cache
def load_data(nrows):
    data = pd.read_csv('df_nettoye_2.csv', sep=';', nrows=nrows)
    return data


st.sidebar.title('Analyses Projet Energie')
page = st.sidebar.radio("", options = [ 'Evolution des Températures', 'Production/Consommation', 'Carte Sources Energies de France', 'Consommation par Secteur'])
st.sidebar.markdown('**_A travers les 4 menus disponibles, nous vous proposons de visualiser de manières interactive quelques tableaux, graphiques et cartes géographiques de notre étude sur le thème des énergies en France._**')


if page == 'Evolution des Températures':
    st.title('Evolution des températures')
    st.markdown('Vous avez la possibilité de visualiser les données brutes des températures relevées de 2016 à 2020.')
    st.markdown('Pour chaque région sélectionnée, vous visualiserez les températures minimale, moyenne et maximale.')
    region_temperature = st.selectbox("Choisissez une Région", ['', 'Bretagne', 'Nouvelle-Aquitaine', 'Île-de-France',
       'Bourgogne-Franche-Comté', 'Auvergne-Rhône-Alpes', 'Normandie',
       'Occitanie', 'Centre-Val de Loire', 'Hauts-de-France', 'Grand Est',
       "Provence-Alpes-Côte d'Azur", 'Pays de la Loire'])
    df_conso_temperatures_regions = pd.read_csv("df_conso_temperatures_regions.csv")
    chart_data = pd.DataFrame(
        df_conso_temperatures_regions[df_conso_temperatures_regions['Région']==region_temperature],
        columns=['tmin', 'tmoy', 'tmax'])

    st.line_chart(chart_data)



if page == 'Production/Consommation':
    st.title('Production et Consommation d\'énergie par Région')
    st.markdown('En choissant une région, vous avez la possibilité de comparer la production et la consommation de chaque région de 2013 à 2020')
    @st.cache
    
    def get_data_consommation():
        df = pd.read_csv('df_streamlit.csv')
        df = df.reset_index()
        return df.set_index("Libellé Région")

    def get_data_production():
        df_prod = pd.read_csv('df_production.csv')
        df_prod = df_prod.reset_index()
        return df_prod.set_index("Libellé Région")

    try:
        df = get_data_consommation()
        df_prod = get_data_production()
        region = st.multiselect(
            "Choisissez vos régions", list(df_prod.index), ["Île-de-France", "Centre-Val de Loire"]
            )
        if not region:
            st.error("Merci de choisir une région.")
        else:
            
            # Traitement de la partie production
            data_prod = df_prod.loc[region]
            st.write("### Production électrique en MW", data_prod.sort_index())

            data_prod = data_prod.T.reset_index()
            data_prod = pd.melt(data_prod, id_vars=["index"]).rename(
                columns={"index": "Annee", "value": "Production (MW)"}
                )
            chart_prod = (alt.Chart(data_prod)
                .mark_area(opacity=0.4)
                .encode(x="Annee:T", y=alt.Y("Production (MW):Q", stack=None), color="Libellé Région:N",))
            st.altair_chart(chart_prod, use_container_width=True)
            
            # Traitement de la partie Consommation
            data = df.loc[region]
            st.write("### Consommations électrique en MW", data.sort_index())

            data = data.T.reset_index()
            data = pd.melt(data, id_vars=["index"]).rename(
                columns={"index": "Annee", "value": "Consommation (MW)"}
                )
            chart = (alt.Chart(data)
                .mark_area(opacity=0.4)
                .encode(x="Annee:T", y=alt.Y("Consommation (MW):Q", stack=None), color="Libellé Région:N",))
            st.altair_chart(chart, use_container_width=True)
            
    except URLError as e:
                st.error(
               """
               **This demo requires internet access.**

                Connection error: %s
                """
            % e.reason
            )


    
if page == 'Carte Sources Energies de France':
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    from urllib.request import urlopen
    import json
    st.title('Sources Energétiques de France en 2020')
    st.markdown('Cette carte vous présente de manière interactive la répartition géographique des différentes sources d\'énergie.')
    st.markdown('Sélectionnez un type de production d’énergie pour voir les volumes de production par région.')
    with urlopen('http://france-geojson.gregoiredavid.fr/repo/regions.geojson') as response:
        regions = json.load(response)

    
    df = pd.read_csv("df_energie_2020.csv",
                   dtype={"Code INSEE région": str})


    type_energie = st.selectbox("Choisissez une source d'énergie",['Thermique (MW)', 'Nucléaire (MW)','Hydraulique (MW)', 'Solaire (MW)', 'Eolien (MW)'])

    fig = px.choropleth_mapbox(df, geojson=regions, locations='Libellé Région',             color=type_energie,
                           featureidkey="properties.nom",
                           color_continuous_scale="Viridis",
                           range_color=(df[type_energie].min(), df[type_energie].max()),
                           mapbox_style="carto-positron",
                           zoom=4.5, center = {"lat": 47.000193, "lon": 2.209667},
                           opacity=0.5,
                           labels=type_energie
                          )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)
    with st.expander("Voir les explications"):
        st.write("""
                 Ici nous pouvons mettre d'autres informations utiles sur la répartition des productions à travers la France.'
                 """)


if page == 'Consommation par Secteur':
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    from urllib.request import urlopen
    import json
    st.title('Consommations par secteur d\'activité')
    st.markdown('Concernant les consommations d\'énergie, vous avez la possibilité d\'étudier les secteurs d\'activité qui consomment le plus d\'énergie en visualisant leur localisation.')
    with urlopen('http://france-geojson.gregoiredavid.fr/repo/regions.geojson') as response:
        regions = json.load(response)

    
    df = pd.read_csv("consommation_secteurs.csv",
                   dtype={"Code INSEE région": str})


    type_energie = st.selectbox("Choisissez un secteur d\'activité",[ 'Consommation Agriculture (MWh)',
       'Consommation Industrie (MWh)', 'Consommation Résidentiel  (MWh)', 
       'Consommation Tertiaire  (MWh)',])

    fig = px.choropleth_mapbox(df, geojson=regions, locations='Libellé Région',             color=type_energie,
                           featureidkey="properties.nom",
                           color_continuous_scale="Viridis",
                           range_color=(df[type_energie].min(), df[type_energie].max()),
                           mapbox_style="carto-positron",
                           zoom=4.5, center = {"lat": 47.000193, "lon": 2.209667},
                           opacity=0.5,
                           labels=type_energie
                          )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)
    
    with st.expander("Informations complémentaires"):
        if type_energie == 'Consommation Agriculture (MWh)':
            st.write("""
                 Ici nous pouvons ajouter des commentaires issus du rapport par exemple.
                 """)
        if type_energie == 'Consommation Industrie (MWh)':
            st.write("""
                 Les régions dont la consommation industrielle est plus forte que les autres secteurs activités sont l’Auvergne- Rhône-Alpes, les Hauts-de-France et le Grand-Est.
                 """)
        if type_energie == 'Consommation Tertiaire  (MWh)':
            st.write("""
                 Les régions dont la consommation tertiaire est plus forte que les autres secteurs activités est l’Ile-de-France, l’Auvergne-Rhône-Alpes et la Provence-Alpes-Côte d’Azur.
                 """)
        if type_energie == 'Consommation Résidentiel  (MWh)':
            st.write("""
                 Les régions dont la consommation résidentielle est plus forte que les autres secteurs activités sont l’Ile-de-France, l’Auvergne-Rhône-Alpes et l’Occitanie.
                 """)

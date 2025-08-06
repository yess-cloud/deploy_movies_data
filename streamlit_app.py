import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import numpy as np

import json
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="movies-project-data")

st.header("Netflix App")

#Leer en un data frame todos los registros de Firestore
@st.cache_data
def load_all_data():
    docs = db.collection("movies").stream()
    data = [doc.to_dict() for doc in docs]
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame()

# Cargar todos los datos al inicio
data = load_all_data()

#Crear sidebar del dashboard
sidebar = st.sidebar

# Componente checkbox para mostrar todos los filmes
agree = sidebar.checkbox("Mostrar todos los filmes")
if agree:
    st.subheader("Todos los filmes")
    if not data.empty:
        st.dataframe(data)
    else:
        st.info("No hay filmes para mostrar.")

# Componente para buscar por título del filme
sidebar.subheader("Buscar filmes por título")
myname = sidebar.text_input('Título del filme')
search_button = sidebar.button("Buscar filmes")

if search_button:
    if myname:
        # Filtrar el DataFrame 'data' directamente
        if not data.empty:
            filtered_data_byname = data[data['name'].str.contains(myname, case=False, na=False)]
            count_row = filtered_data_byname.shape[0]
            st.write(f"Total de filmes encontrados: {count_row}")
            if not filtered_data_byname.empty:
                st.dataframe(filtered_data_byname)
            else:
                sidebar.info("No se encontraron filmes con ese título.")
        else:
            sidebar.info("No hay datos para buscar.")
    else:
        sidebar.warning("Por favor, ingresa un título para buscar.")
        
# Componente para filtrar por director
sidebar.subheader("Filtrar por director")
if not data.empty:
    selected_director = sidebar.selectbox("Seleccionar director:", data['director'].unique())
    btnFilterbyDirector = sidebar.button('Filtrar director')

    if btnFilterbyDirector:
        filtered_data_bydirector = data[data['director'] == selected_director]
        count_row = filtered_data_bydirector.shape[0]
        st.write(f"Total de filmes: {count_row}")
        st.dataframe(filtered_data_bydirector)
else:
    sidebar.info("No hay datos para filtrar por director.")

# Componente para insertar nuevo filme
sidebar.subheader("Insertar nuevo filme")
company = sidebar.text_input("Company")
name = sidebar.text_input("Name")
director = sidebar.text_input("Director")
genre = sidebar.text_input("Genre")

submit = sidebar.button("Crear nuevo filme")

if submit:
    if name and company and genre and director:
        doc_ref = db.collection("movies").document(name)
        doc_ref.set({
            "company": company,
            "name": name,
            "director": director,
            "genre": genre
        })
        sidebar.success(f"El filme '{name}' ha sido agregado correctamente.")
        st.experimental_rerun()
    else:
        sidebar.warning("Por favor, completa todos los campos para crear un nuevo filme.")

import pandas as pd

import demoji

import numpy as np
from collections import Counter

import plotly.express as px
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS

import streamlit as st

###################################
###################################
# Título de la aplicación
st.title('Análisis de nuestro progreso en el GYM ❤️')
###################################
###################################
#Leeremos nuestras tablas
Progreso = pd.read_csv("Libro1.csv",delimiter=';')
Progreso_ind= Progreso.set_index("Dia")
print(Progreso_ind)

#Registro de datos.
# Crear un botón para registrar los datos
if st.button('Registrar datos'):
    # Solicitar información al usuario
    Dia = st.text_input('Ingresa el Dia:')
    Persona = st.multiselect('Su nombre:', ('Carlos', 'Cinthia'))
    Maquina = st.selectbox('Selecciona una maquina:', ('Prensa de Piernas', 'Multipowers', 'Máquina de Extensión de Cuádriceps', 'Máquina de Femorales', 'Máquina de Aductores', 'Máquina de Abductores'))
    Peso = st.slider('Selecciona el peso:', 0, 100, 30)
    Descanso = st.selectbox('Selecciona la cantidad de tiempo:', ('1-2', '2-3', '3-4'))
    Series = st.slider('Selecciona la cantidad de series:', 0, 100, 30)
    Repeticiones = st.slider('Selecciona las repeticiones:', 0, 100, 30)
    # Crear un nuevo registro
    if st.button2('Registrar'):
        Progreso_new = {'Persona': Persona, 'Maquina': Maquina, 'Series': Series, 'Repeticiones': Repeticiones, 'Descanso': Descanso, 'Peso': Peso, 'Dia':Dia}
        # Concatenar con el DataFrame existente (Progreso_ind)
        Progreso_ind = pd.concat([Progreso_ind, pd.DataFrame([Progreso_new])], ignore_index=True) 
    

# Mostrar el DataFrame resultante
st.write('Registro de progreso:')
st.write(Progreso_ind)
print(Progreso_ind)
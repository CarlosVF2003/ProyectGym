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
with st.form(key='mi_formulario'):
    # Tus widgets de entrada aquí
    # ...

    # Botón de envío del formulario
    submit_button = st.form_submit_button(label='Guardar')

# Procesar la información una vez que se envía el formulario
if submit_button:
    # Suponiendo que ya has recogido todos los datos en las variables correspondientes
    Progreso_new = {'Dia': Dia, 'Persona': Persona, 'Maquina': Maquina, 'Peso': Peso, 'Descanso': Descanso, 'Series': Series, 'Repeticiones': Repeticiones}
    
    # Añadir los nuevos datos al DataFrame existente
    Progreso_ind = pd.concat([Progreso, pd.DataFrame([Progreso_new])], ignore_index=True)
    
    # Guardar el DataFrame actualizado en un archivo CSV
    Progreso_ind.to_csv('Libro.csv', index=False)
    
    # Mensaje de éxito
    st.success('¡Datos registrados con éxito!')

# Mostrar el DataFrame resultante
st.write('Registro de progreso:')
st.write(Progreso_ind)
print(Progreso_ind)

#Graficos



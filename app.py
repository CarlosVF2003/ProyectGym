import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS
import streamlit as st

# Título de la aplicación
st.title('Análisis de nuestro progreso en el GYM ❤️')

# Intentar leer el archivo CSV y si no existe, inicializar un DataFrame vacío
try:
    Progreso_ind = pd.read_csv("Libro1.csv", delimiter=';')
except FileNotFoundError:
    Progreso_ind = pd.DataFrame()

# Guardar el DataFrame en el estado de la sesión
st.session_state['Progreso_ind'] = Progreso_ind

# Registro de datos.
with st.form(key='mi_formulario'):
    # Widgets de entrada
    Dia = st.text_input('Ingresa el Dia:')
    Persona = st.selectbox('Su nombre:', ('Carlos', 'Cinthia'))
    Maquina = st.selectbox('Selecciona una maquina:', ('Prensa de Piernas', 'Multipowers', 'Máquina de Extensión de Cuádriceps', 'Máquina de Femorales', 'Máquina de Aductores', 'Máquina de Abductores'))
    Peso = st.slider('Selecciona el peso:', 0, 100, 40)
    Descanso = st.selectbox('Selecciona la cantidad de tiempo:', ('1-2 min', '2-3 min', '3-4 min'))
    Series = st.slider('Selecciona la cantidad de series:', 0, 4, 3)
    Repeticiones = st.slider('Selecciona las repeticiones:', 0, 30, 15)
    # Botón de envío del formulario
    submit_button = st.form_submit_button(label='Guardar')

# Procesar la información una vez que se envía el formulario
if submit_button:
    Progreso_new = {'Dia': Dia, 'Persona': Persona, 'Maquina': Maquina, 'Peso': Peso, 'Descanso': Descanso, 'Series': Series, 'Repeticiones': Repeticiones}
    
    # Añadir los nuevos datos al DataFrame en el estado de la sesión
    st.session_state['Progreso_ind'] = pd.concat([st.session_state['Progreso_ind'], pd.DataFrame([Progreso_new])], ignore_index=False)
    
    # Guardar el DataFrame actualizado en un archivo CSV
    st.session_state['Progreso_ind'].reset_index().to_csv('Libro1.csv', index=False, sep=';')
    
    # Mensaje de éxito
    st.success('¡Datos registrados con éxito!')

# Para depurar o verificar, puedes mostrar el DataFrame actualizado
st.write(st.session_state['Progreso_ind'])




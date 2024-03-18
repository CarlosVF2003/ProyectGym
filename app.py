# Importamos librerias
import pandas as pd
import re

import regex
import demoji

import numpy as np
from collections import Counter

import plotly.express as px
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud, STOPWORDS
import seaborn as sns
import streamlit as st
from pathlib import Path

# Cargar el archivo Libro1.csv si existe
if 'Progreso_ind' not in st.session_state:
    if Path("Progreso.csv").is_file():
        st.session_state['Progreso_ind'] = pd.read_csv("Progreso.csv", sep=';')
    else:
        st.session_state['Progreso_ind'] = pd.DataFrame()

#Definimos las funciones
def formulario_desarrollo_fuerza(sets):
    pesos = [st.number_input(f'💪 Peso para el set {i+1}:', min_value=0, max_value=100, step=1) for i in range(sets)]
    repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return pesos, [repeticiones] * sets, [descanso] * sets  # Las repeticiones y el tiempo de descanso son constantes para el desarrollo de fuerza

def formulario_mejora_resistencia(sets):
    pesos = [st.number_input(f'💪 Peso para el set {i+1}:', min_value=0, max_value=100, step=1) for i in range(sets)]
    repeticiones = [st.number_input(f'🏃 Repeticiones para el set {i+1}:', min_value=1, max_value=30, step=1) for i in range(sets)]
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return pesos, repeticiones, [descanso] * sets

def formulario_hipertrofia_muscular(sets):
    peso = st.number_input('💪 Peso (kg):', min_value=0, max_value=100, step=1)
    repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return [peso] * sets, [repeticiones] * sets, [descanso] * sets  # Tanto el peso, las repeticiones y el tiempo de descanso son constantes para la hipertrofia muscular

st.title('🏋️‍♂️ Nuestro progreso en el Gimnasio 🏋️‍♀️')

# Botón para abrir el formulario principal
if st.button("📝 Abrir Formulario Principal"):
    st.session_state['show_enfoque_form'] = True

# Registro de datos.
if st.session_state.get('show_enfoque_form', False):
    with st.form(key='mi_formulario'):
        # Widgets de entrada
        Dia = st.text_input('Ingresa el Día 📆:')
        Persona = st.selectbox('Selecciona tu nombre 🤵‍♂️🙍:', ('Carlos', 'Cinthia'))
        Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', ('Prensa de Piernas', 'Multipowers', 'Máquina de Extensión de Cuádriceps', 'Máquina de Femorales', 'Máquina de Aductores', 'Máquina de Abductores','Press de pecho','Extension de hombro',
                                                                    'Extension tricep en polea','Extension lateral','Extension frontal'))
        Enfoque = st.selectbox('Selecciona el enfoque de entrenamiento:', ('Desarrollo de Fuerza', 'Mejora de la Resistencia', 'Hipertrofia Muscular'))
        sets = st.number_input('Número de sets:', min_value=1, max_value=10, step=1, value=4)
            
        # Botón de envío del formulario
        guardar_button = st.form_submit_button(label='Guardar 💾')
        if guardar_button:
            if Enfoque == 'Desarrollo de Fuerza':
                pesos, repeticiones, descansos = formulario_desarrollo_fuerza(sets)
            elif Enfoque == 'Mejora de la Resistencia':
                pesos, repeticiones, descansos = formulario_mejora_resistencia(sets)
            else:  # Hipertrofia Muscular
                pesos, repeticiones, descansos = formulario_hipertrofia_muscular(sets)
                    
            # Verificar que ambos formularios estén completos
            form_completo = all(pesos) and all(repeticiones) and all(descansos)
                
            if form_completo:
                for peso, repeticion, descanso in zip(pesos, repeticiones, descansos):
                    Progreso_new = {'Dia': Dia, 'Persona': Persona, 'Maquina': Maquina, 'Peso': peso, 'Descanso': descanso, 'Sets': sets, 'Repeticiones': repeticion}
                    st.session_state['Progreso_ind'] = pd.concat([st.session_state['Progreso_ind'], pd.DataFrame([Progreso_new])], ignore_index=True)
                # Guardar el DataFrame actualizado en un archivo CSV
                # Utiliza transform para agregar la columna de conteo directamente al DataFrame existente
                st.session_state['Progreso_ind']['Sets'] = st.session_state['Progreso_ind'].groupby(['Dia', 'Persona', 'Maquina', 'Peso', 'Descanso', 'Repeticiones'])['Peso'].transform('size')
                st.session_state['show_enfoque_form'] = False
                st.success('¡Datos registrados con éxito!')
                st.session_state['Progreso_ind'].to_csv('Progreso.csv', index= False, sep= ';')
                # Ocultar el formulario
            else:
                st.warning('Por favor completa todos los campos del formulario.')

# Visualización de datos
st.subheader("Visualización de datos registrados")
# Eliminar filas duplicadas basadas en las columnas específicas y actualizar los sets
unique_values = st.session_state['Progreso_ind'].drop_duplicates(subset=['Dia', 'Persona', 'Maquina', 'Peso', 'Descanso', 'Repeticiones'])
st.write(unique_values[['Dia', 'Persona', 'Maquina', 'Peso', 'Descanso', 'Sets', 'Repeticiones']], index=False)

# Gráfico de comparación entre personas
st.subheader("Comparación de progreso entre personas")
avg_peso = st.session_state['Progreso_ind'].groupby('Persona')['Peso'].mean().reset_index()
fig_avg_peso = px.bar(avg_peso, x='Persona', y='Peso', title='Promedio de peso levantado por persona', color='Persona', color_discrete_map={'Carlos': 'black', 'Cinthia': 'skyblue'})
st.plotly_chart(fig_avg_peso)

# Histograma de repeticiones por máquina y persona
st.subheader("Histograma de repeticiones por máquina y persona")
fig_hist_rep = px.histogram(st.session_state['Progreso_ind'], x='Repeticiones', color='Persona', title='Distribución de repeticiones por máquina y persona', color_discrete_map={'Carlos': 'black', 'Cinthia': 'skyblue'})
st.plotly_chart(fig_hist_rep)

# Box plot de pesos por día y persona
st.subheader("Box plot de pesos por día y persona")
fig_box_peso = px.box(st.session_state['Progreso_ind'], x='Dia', y='Peso', color='Persona', title='Distribución de pesos por día y persona', color_discrete_map={'Carlos': 'black', 'Cinthia': 'skyblue'})
st.plotly_chart(fig_box_peso)

# Gráfico de línea de series por día
st.subheader("Gráfico de línea de series por día")
fig_line_sets = px.line(st.session_state['Progreso_ind'], x='Dia', y='Sets', color='Persona', markers=True, title='Número de series por día', color_discrete_map={'Carlos': 'black', 'Cinthia': 'skyblue'})
st.plotly_chart(fig_line_sets)

# Diagrama de dispersión de peso vs repeticiones
st.subheader("Diagrama de dispersión de peso vs repeticiones")
fig_scatter_peso_rep = px.scatter(st.session_state['Progreso_ind'], x='Peso', y='Repeticiones', color='Persona', title='Peso vs Repeticiones', color_discrete_map={'Carlos': 'black', 'Cinthia': 'skyblue'})
st.plotly_chart(fig_scatter_peso_rep)

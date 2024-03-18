# Importar librerias
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np
from pathlib import Path

# Cargar el archivo Progreso.csv si existe
if 'Progreso_ind' not in st.session_state:
    if Path("Progreso.csv").is_file():
        st.session_state['Progreso_ind'] = pd.read_csv("Progreso.csv", sep=';')
    else:
        st.session_state['Progreso_ind'] = pd.DataFrame()

# Definir las funciones
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

# Título de la aplicación
st.title('🏋️‍♂️ Nuestro progreso en el Gimnasio 🏋️‍♀️')

# Registro de datos.
with st.expander("Registrar Sesión de Entrenamiento", expanded=True):
    # Widgets de entrada
    Dia = st.number_input('Día:', min_value=1, max_value=31)
    Persona = st.selectbox('Selecciona tu nombre 🤵‍♂️🙍:', ('Carlos', 'Cinthia'))
    Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', ('Prensa de Piernas', 'Multipowers', 'Máquina de Extensión de Cuádriceps', 'Máquina de Femorales', 'Máquina de Aductores', 'Máquina de Abductores','Press de pecho','Extension de hombro',
                                                                'Extension tricep en polea','Extension lateral','Extension frontal'))
    Enfoque = st.selectbox('Selecciona el enfoque de entrenamiento:', ('Desarrollo de Fuerza', 'Mejora de la Resistencia', 'Hipertrofia Muscular'))
    sets = st.number_input('Número de sets:', min_value=1, max_value=10, step=1, value=4)

    if Enfoque == 'Desarrollo de Fuerza':
        pesos, repeticiones, descansos = formulario_desarrollo_fuerza(sets)
    elif Enfoque == 'Mejora de la Resistencia':
        pesos, repeticiones, descansos = formulario_mejora_resistencia(sets)
    else:  # Hipertrofia Muscular
        pesos, repeticiones, descansos = formulario_hipertrofia_muscular(sets)
        
    # Verificar que ambos formularios estén completos
    form_completo = all(pesos) and all(repeticiones) and all(descansos)
            
    if form_completo:
        Progreso_new = {'Dia': Dia, 'Persona': Persona, 'Maquina': Maquina, 'Peso': pesos, 'Descanso': descansos, 'Sets': sets, 'Repeticiones': repeticiones}
        st.session_state['Progreso_ind'] = pd.concat([st.session_state['Progreso_ind'], pd.DataFrame([Progreso_new])], ignore_index=True)
        st.success('¡Datos registrados con éxito!')
        st.session_state['Progreso_ind'].to_csv('Progreso.csv', index=False, sep=';')
    else:
        st.warning('Por favor completa todos los campos del formulario.')

# Sección del dashboard
st.title('Dashboard de Progreso en el Gimnasio')

# Definir los colores para Carlos y Cinthia
colors = {'Carlos': 'black', 'Cinthia': 'lightblue'}

# Mostrar las tablas de Carlos y Cinthia
st.header('Datos de Carlos')
st.dataframe(st.session_state['Progreso_ind'][st.session_state['Progreso_ind']['Persona'] == 'Carlos'].style.set_caption("Tabla de Carlos").applymap(lambda _: f'color: {colors["Carlos"]}'))

st.header('Datos de Cinthia')
st.dataframe(st.session_state['Progreso_ind'][st.session_state['Progreso_ind']['Persona'] == 'Cinthia'].style.set_caption("Tabla de Cinthia").applymap(lambda _: f'color: {colors["Cinthia"]}'))

# Gráfico de Líneas para Pesos Levantados
st.header('Gráfico de Líneas para Pesos Levantados')
fig_line = px.line(st.session_state['Progreso_ind'], x='Dia', y='Peso', color='Persona', title='Pesos Levantados a lo largo del tiempo', color_discrete_map=colors)
st.plotly_chart(fig_line)

# Gráfico de Barras para Repeticiones o Sets
st.header('Gráfico de Barras para Repeticiones o Sets')
fig_bar = px.bar(st.session_state['Progreso_ind'], x='Dia', y='Sets', color='Persona', title='Número de Sets Realizados', color_discrete_map=colors)
st.plotly_chart(fig_bar)

# Histograma para analizar la distribución de las repeticiones
st.header('Histograma para Repeticiones')
fig_hist = px.histogram(st.session_state['Progreso_ind'], x='Repeticiones', color='Persona', title='Distribución de Repeticiones', color_discrete_map=colors)
st.plotly_chart(fig_hist)

# Diagrama de Dispersión para correlacionar peso y repeticiones
st.header('Diagrama de Dispersión para Peso y Repeticiones')
fig_scatter = px.scatter(st.session_state['Progreso_ind'], x='Peso', y='Repeticiones', color='Persona', title='Correlación entre Peso y Repeticiones', color_discrete_map=colors)
st.plotly_chart(fig_scatter)

# Algoritmo de Machine Learning (Linear Regression)
st.header('Algoritmo de Machine Learning: Regresión Lineal')
X = st.session_state['Progreso_ind'][['Repeticiones', 'Sets']]
y = st.session_state['Progreso_ind']['Peso']

# Entrenar el modelo
model = LinearRegression()
model.fit(X, y)

# Mostrar los coeficientes
st.write(f'Coeficiente de Repeticiones: {model.coef_[0]}')
st.write(f'Coeficiente de Sets: {model.coef_[1]}')
st.write(f'Intercepto: {model.intercept_}')

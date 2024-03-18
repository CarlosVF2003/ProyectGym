# Importamos librerias
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Cargar el archivo Progreso.csv si existe
if 'Progreso_ind' not in st.session_state:
    if Path("Progreso.csv").is_file():
        st.session_state['Progreso_ind'] = pd.read_csv("Progreso.csv", sep=';')
    else:
        st.session_state['Progreso_ind'] = pd.DataFrame()

# Definimos las funciones
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

# Sección del dashboard
st.title('Dashboard de Progreso en el Gimnasio')

# Filtros
st.sidebar.header('Filtros')

# Filtro por Persona
filtro_persona = st.sidebar.selectbox('Selecciona persona:', ['Todos'] + list(st.session_state['Progreso_ind']['Persona'].unique()))

# Filtro por Máquina o Ejercicio
filtro_maquina = st.sidebar.selectbox('Selecciona máquina o ejercicio:', ['Todos'] + list(st.session_state['Progreso_ind']['Maquina'].unique()))

# Filtro por Rango de Fechas
min_fecha = st.sidebar.date_input('Fecha mínima:', min(st.session_state['Progreso_ind']['Dia']))
max_fecha = st.sidebar.date_input('Fecha máxima:', max(st.session_state['Progreso_ind']['Dia']))

# Aplicar filtros
datos_filtrados = st.session_state['Progreso_ind']
if filtro_persona != 'Todos':
    datos_filtrados = datos_filtrados[datos_filtrados['Persona'] == filtro_persona]
if filtro_maquina != 'Todos':
    datos_filtrados = datos_filtrados[datos_filtrados['Maquina'] == filtro_maquina]
datos_filtrados = datos_filtrados[(datos_filtrados['Dia'] >= min_fecha) & (datos_filtrados['Dia'] <= max_fecha)]

# Gráfico de Líneas: Progreso Individual
st.subheader('Gráfico de Líneas: Progreso Individual')
if not datos_filtrados.empty:
    fig_line_individual = px.line(datos_filtrados, x='Dia', y='Peso', color='Persona', title='Progreso Individual')
    st.plotly_chart(fig_line_individual)

# Gráfico de Líneas: Progreso por Máquina
st.subheader('Gráfico de Líneas: Progreso por Máquina')
if not datos_filtrados.empty:
    fig_line_maquina = px.line(datos_filtrados, x='Dia', y='Peso', color='Maquina', title='Progreso por Máquina')
    st.plotly_chart(fig_line_maquina)

# Gráfico de Barras: Comparación por Día
st.subheader('Gráfico de Barras: Comparación por Día')
if not datos_filtrados.empty:
    fig_bar_dia = px.bar(datos_filtrados, x='Dia', y='Peso', color='Dia', title='Comparación de Peso por Día')
    st.plotly_chart(fig_bar_dia)

# Gráfico de Barras: Sets Realizados
st.subheader('Gráfico de Barras: Sets Realizados')
if not datos_filtrados.empty:
    fig_bar_sets = px.bar(datos_filtrados, x='Dia', y='Sets', color='Persona', title='Sets Realizados por Día')
    st.plotly_chart(fig_bar_sets)

# Histograma: Distribución de Repeticiones
st.subheader('Histograma: Distribución de Repeticiones')
if not datos_filtrados.empty:
    fig_hist_rep = px.histogram(datos_filtrados, x='Repeticiones', color='Maquina', title='Distribución de Repeticiones por Ejercicio')
    st.plotly_chart(fig_hist_rep)

# Histograma: Distribución de Descanso
st.subheader('Histograma: Distribución de Descanso')
if not datos_filtrados.empty:
    fig_hist_descanso = px.histogram(datos_filtrados, x='Descanso', color='Maquina', title='Distribución de Descanso por Ejercicio')
    st.plotly_chart(fig_hist_descanso)

# Gráfico de Dispersión: Peso vs. Descanso
st.subheader('Gráfico de Dispersión: Peso vs. Descanso')
if not datos_filtrados.empty:
    fig_scatter_peso_descanso = px.scatter(datos_filtrados, x='Peso', y='Descanso', color='Maquina', title='Peso vs. Descanso')
    st.plotly_chart(fig_scatter_peso_descanso)

# Gráfico de Dispersión: Peso vs. Repeticiones
st.subheader('Gráfico de Dispersión: Peso vs. Repeticiones')
if not datos_filtrados.empty:
    fig_scatter_peso_repeticiones = px.scatter(datos_filtrados, x='Peso', y='Repeticiones', color='Maquina', title='Peso vs. Repeticiones')
    st.plotly_chart(fig_scatter_peso_repeticiones)

# Tabla de Progreso
st.subheader('Tabla de Progreso')
st.write(datos_filtrados)

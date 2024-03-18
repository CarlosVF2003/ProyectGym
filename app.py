# Importar librerias
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

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
if not st.session_state['Progreso_ind'].empty:
    min_fecha = st.sidebar.date_input('Fecha mínima:', min(st.session_state['Progreso_ind']['Dia']))
    max_fecha = st.sidebar.date_input('Fecha máxima:', max(st.session_state['Progreso_ind']['Dia']))
else:
    min_fecha = st.sidebar.date_input('Fecha mínima:', None)
    max_fecha = st.sidebar.date_input('Fecha máxima:', None)

# Aplicar filtros
datos_filtrados = st.session_state['Progreso_ind']
if filtro_persona != 'Todos':
    datos_filtrados = datos_filtrados[datos_filtrados['Persona'] == filtro_persona]
if filtro_maquina != 'Todos':
    datos_filtrados = datos_filtrados[datos_filtrados['Maquina'] == filtro_maquina]
if not datos_filtrados.empty:
    datos_filtrados = datos_filtrados[(datos_filtrados['Dia'] >= min_fecha) & (datos_filtrados['Dia'] <= max_fecha)]

# Mostrar gráficos y tablas si hay datos filtrados
if not datos_filtrados.empty:
    # Gráficos para Visualizar el Progreso
    st.subheader('Gráficos para Visualizar el Progreso:')

    # Gráfico de Línea para Pesos Levantados
    if 'Peso' in datos_filtrados.columns:
        fig_peso_linea = px.line(datos_filtrados, x='Dia', y='Peso', color='Persona', title='Pesos Levantados a lo largo del Tiempo', color_discrete_map={"Carlos": "black", "Cinthia": "lightblue"})
        st.plotly_chart(fig_peso_linea)

    # Gráfico de Barras para Repeticiones o Sets
    if 'Repeticiones' in datos_filtrados.columns:
        fig_repeticiones_barras = px.bar(datos_filtrados, x='Dia', y='Repeticiones', color='Persona', title='Repeticiones Realizadas por Sesión', color_discrete_map={"Carlos": "black", "Cinthia": "lightblue"})
        st.plotly_chart(fig_repeticiones_barras)

    # Gráfico de Progresión General
    if 'Dia' in datos_filtrados.columns:
        fig_progresion_general = px.line(datos_filtrados.groupby('Dia')['Peso'].sum().reset_index(), x='Dia', y='Peso', title='Progresión General de Pesos Levantados', color_discrete_map={"Carlos": "black", "Cinthia": "lightblue"})
        st.plotly_chart(fig_progresion_general)

    # Gráfico de Progresión de Sets y Repeticiones
    if 'Sets' in datos_filtrados.columns and 'Repeticiones' in datos_filtrados.columns:
        fig_sets_repeticiones = px.bar(datos_filtrados, x='Dia', y='Sets', color='Persona', title='Progresión de Sets y Repeticiones por Sesión', barmode='stack', color_discrete_map={"Carlos": "black", "Cinthia": "lightblue"})
        st.plotly_chart(fig_sets_repeticiones)

    # Gráfico de Intensidad
    if 'Peso' in datos_filtrados.columns and 'Repeticiones' in datos_filtrados.columns and 'Sets' in datos_filtrados.columns:
        datos_filtrados['Intensidad'] = datos_filtrados['Peso'] * datos_filtrados['Repeticiones'] * datos_filtrados['Sets']
        fig_intensidad = px.area(datos_filtrados, x='Dia', y='Intensidad', color='Persona', title='Intensidad de Entrenamiento', color_discrete_map={"Carlos": "black", "Cinthia": "lightblue"})
        st.plotly_chart(fig_intensidad)

    # Gráfico de Descanso
    if 'Descanso' in datos_filtrados.columns:
        fig_descanso = px.bar(datos_filtrados.groupby('Dia')['Descanso'].count().reset_index(), x='Dia', y='Descanso', title='Promedio de Duración de Descanso por Sesión', color_discrete_map={"Carlos": "black", "Cinthia": "lightblue"})
        st.plotly_chart(fig_descanso)

    # Gráfico de Variación de Peso
    # Agrega aquí el gráfico de variación de peso si lo deseas

    # Tablas de Datos
    st.subheader('Tablas de Datos:')

    # Tabla de Sesiones de Entrenamiento
    st.write('Tabla de Sesiones de Entrenamiento:')
    st.write(datos_filtrados[['Dia', 'Persona', 'Maquina', 'Peso', 'Descanso', 'Sets', 'Repeticiones']].style.set_caption("Tabla de Sesiones de Entrenamiento"))

    # Tabla de Resumen Semanal
    st.write('Tabla de Resumen Semanal:')
    resumen_semanal = datos_filtrados.groupby(pd.Grouper(key='Dia', freq='W'))[['Peso', 'Repeticiones']].sum().reset_index()
    st.write(resumen_semanal.style.set_caption("Tabla de Resumen Semanal"))

else:
    st.write('No hay datos disponibles para los filtros seleccionados.')

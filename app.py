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
if st.session_state.get('show_enfoque_form', False):
    with st.form(key='mi_formulario'):
        # Widgets de entrada
        Dia = st.text_input('Ingresa el Día 📆:')
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

        guardar_button = st.form_submit_button(label='Guardar 💾')
        if guardar_button:
            form_completo = all(pesos) and all(repeticiones) and all(descansos)
            if form_completo:
                for peso, repeticion, descanso in zip(pesos, repeticiones, descansos):
                    Progreso_new = {'Dia': Dia, 'Persona': Persona, 'Maquina': Maquina, 'Peso': peso, 'Descanso': descanso, 'Sets': sets, 'Repeticiones': repeticion}
                    st.session_state['Progreso_ind'] = pd.concat([st.session_state['Progreso_ind'], pd.DataFrame([Progreso_new])], ignore_index=True)
                st.session_state['Progreso_ind']['Sets'] = st.session_state['Progreso_ind'].groupby(['Dia', 'Persona', 'Maquina', 'Peso', 'Descanso', 'Repeticiones'])['Peso'].transform('size')
                st.session_state['show_enfoque_form'] = False
                st.success('¡Datos registrados con éxito!')
                st.session_state['Progreso_ind'].to_csv('Progreso.csv', index= False, sep= ';')
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
    min_fecha = st.sidebar.number_input('Día mínimo:', min_value=min(st.session_state['Progreso_ind']['Dia']))
    max_fecha = st.sidebar.number_input('Día máximo:', max_value=max(st.session_state['Progreso_ind']['Dia']))
else:
    min_fecha = st.sidebar.number_input('Día mínimo:', min_value=0)
    max_fecha = st.sidebar.number_input('Día máximo:', max_value=0)

# Aplicar filtros
datos_filtrados = st.session_state['Progreso_ind']
if filtro_persona != 'Todos':
    datos_filtrados = datos_filtrados[datos_filtrados['Persona'] == filtro_persona]
if filtro_maquina != 'Todos':
    datos_filtrados = datos_filtrados[datos_filtrados['Maquina'] == filtro_maquina]
if not datos_filtrados.empty:
    datos_filtrados = datos_filtrados[(datos_filtrados['Dia'] >= min_fecha) & (datos_filtrados['Dia'] <= max_fecha)]

# Gráficos para Visualizar el Progreso
st.header('Gráficos para Visualizar el Progreso')

# Gráfico de Línea para Pesos Levantados por Máquina o Ejercicio
if 'Peso' in datos_filtrados.columns and 'Dia' in datos_filtrados.columns and 'Maquina' in datos_filtrados.columns:
    fig_linea_peso = px.line(datos_filtrados, x='Dia', y='Peso', color='Maquina', title='Pesos Levantados por Máquina o Ejercicio')
    st.plotly_chart(fig_linea_peso)

# Gráfico de Barras para Sets Realizados por Día y Máquina
if 'Sets' in datos_filtrados.columns and 'Dia' in datos_filtrados.columns:
    fig_barras_sets = px.bar(datos_filtrados, x='Dia', y='Sets', color='Maquina', title='Sets Realizados por Día y Máquina')
    st.plotly_chart(fig_barras_sets)

# Gráfico de Progresión General de Carga Total Levantada
if 'Peso' in datos_filtrados.columns and 'Repeticiones' in datos_filtrados.columns and 'Dia' in datos_filtrados.columns:
    datos_filtrados['Carga Total'] = datos_filtrados['Peso'] * datos_filtrados['Repeticiones'] * datos_filtrados['Sets']
    fig_progresion_general = px.line(datos_filtrados, x='Dia', y='Carga Total', color='Persona', title='Progresión General de Carga Total Levantada')
    st.plotly_chart(fig_progresion_general)

# Gráfico de Progresión de Sets y Repeticiones
if 'Sets' in datos_filtrados.columns and 'Repeticiones' in datos_filtrados.columns and 'Dia' in datos_filtrados.columns:
    fig_progresion_sets_repeticiones = px.bar(datos_filtrados, x='Dia', y='Sets', color='Maquina', title='Progresión de Sets y Repeticiones')
    fig_progresion_sets_repeticiones.update_traces(barmode='stack')
    fig_progresion_sets_repeticiones.add_bar(x=datos_filtrados['Dia'], y=datos_filtrados['Repeticiones'], name='Repeticiones', marker_color='rgba(255, 0, 0, 0.6)')
    st.plotly_chart(fig_progresion_sets_repeticiones)

# Gráfico de Intensidad de Entrenamiento
if 'Peso' in datos_filtrados.columns and 'Repeticiones' in datos_filtrados.columns and 'Sets' in datos_filtrados.columns and 'Dia' in datos_filtrados.columns:
    datos_filtrados['Intensidad'] = datos_filtrados['Peso'] * datos_filtrados['Repeticiones'] * datos_filtrados['Sets']
    fig_intensidad = px.area(datos_filtrados, x='Dia', y='Intensidad', color='Persona', title='Intensidad de Entrenamiento')
    st.plotly_chart(fig_intensidad)

# Gráfico de Duración Promedio de Descanso por Día y Máquina
if 'Descanso' in datos_filtrados.columns and 'Dia' in datos_filtrados.columns:
    fig_descanso = px.bar(datos_filtrados, x='Dia', y='Descanso', color='Maquina', title='Duración Promedio de Descanso por Día y Máquina')
    st.plotly_chart(fig_descanso)

# Gráfico de Variación de Peso Corporal
if 'Peso' in datos_filtrados.columns and 'Dia' in datos_filtrados.columns:
    fig_variacion_peso = px.line(datos_filtrados, x='Dia', y='Peso', color='Persona', title='Variación de Peso Corporal')
    st.plotly_chart(fig_variacion_peso)

# Tablas de Datos
st.header('Tablas de Datos')

# Tabla de Sesiones de Entrenamiento
st.subheader('Tabla de Sesiones de Entrenamiento')
st.write(datos_filtrados[['Dia', 'Persona', 'Maquina', 'Peso', 'Descanso', 'Sets', 'Repeticiones']])

# Tabla de Resumen Semanal
if not datos_filtrados.empty:
    datos_filtrados['Semana'] = pd.to_datetime(datos_filtrados['Dia']).dt.to_period('W-MON')
    resumen_semanal = datos_filtrados.groupby(['Semana', 'Persona']).agg({'Peso': 'sum', 'Repeticiones': 'sum'}).reset_index()
    st.subheader('Tabla de Resumen Semanal')
    st.write(resumen_semanal)

# Aplicar modelo de machine learning
st.header('Predicción de Progreso')
st.write('Utilizaremos un modelo de Random Forest para predecir el progreso en el gimnasio.')

# Preparar los datos para el modelo
if 'Peso' in datos_filtrados.columns and 'Repeticiones' in datos_filtrados.columns:
    datos_ml = datos_filtrados[['Peso', 'Repeticiones']]
    X = datos_ml.drop('Peso', axis=1)
    y = datos_ml['Peso']

    # Dividir los datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entrenar el modelo
    modelo = RandomForestRegressor()
    modelo.fit(X_train, y_train)

    # Hacer predicciones
    y_pred = modelo.predict(X_test)

    # Calcular el error
    error = mean_squared_error(y_test, y_pred)
    st.write(f'Error cuadrático medio: {error}')

    # Mostrar los resultados
    st.write('¡El modelo ha sido entrenado y evaluado con éxito!')
else:
    st.write('No hay suficientes datos disponibles para realizar la predicción.')

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
    # Gráficos y tablas aquí...
    st.write(datos_filtrados)

    # Gráfico de barras para comparar el rendimiento entre diferentes días
    if 'Dia' in datos_filtrados.columns:
        fig_dia = px.bar(datos_filtrados, x='Dia', color='Persona', title='Rendimiento por Día', barmode='group')
        st.plotly_chart(fig_dia)

    # Gráfico de barras para ver la consistencia en el número de sets realizados
    if 'Sets' in datos_filtrados.columns:
        fig_sets = px.bar(datos_filtrados, x='Sets', color='Persona', title='Consistencia en Sets', barmode='group')
        st.plotly_chart(fig_sets)

    # Gráfico de barras para observar cómo varía el peso levantado en diferentes sesiones
    if 'Peso' in datos_filtrados.columns:
        fig_peso = px.bar(datos_filtrados, x='Dia', y='Peso', color='Persona', title='Variación del Peso Levantado', barmode='group')
        st.plotly_chart(fig_peso)

    # Histograma para ver la distribución de repeticiones por ejercicio
    if 'Repeticiones' in datos_filtrados.columns:
        fig_repeticiones = px.histogram(datos_filtrados, x='Repeticiones', color='Persona', title='Distribución de Repeticiones')
        st.plotly_chart(fig_repeticiones)

    # Histograma para analizar la relación entre el descanso y el rendimiento
    if 'Descanso' in datos_filtrados.columns:
        fig_descanso = px.histogram(datos_filtrados, x='Descanso', color='Persona', title='Relación entre Descanso y Rendimiento')
        st.plotly_chart(fig_descanso)

    # Gráfico de dispersión para correlacionar el peso levantado con el tiempo de descanso
    if 'Peso' in datos_filtrados.columns and 'Descanso' in datos_filtrados.columns:
        fig_peso_descanso = px.scatter(datos_filtrados, x='Peso', y='Descanso', color='Persona', title='Peso vs. Descanso')
        st.plotly_chart(fig_peso_descanso)

    # Gráfico de dispersión para visualizar la relación entre el peso y el número de repeticiones
    if 'Peso' in datos_filtrados.columns and 'Repeticiones' in datos_filtrados.columns:
        fig_peso_repeticiones = px.scatter(datos_filtrados, x='Peso', y='Repeticiones', color='Persona', title='Peso vs. Repeticiones')
        st.plotly_chart(fig_peso_repeticiones)

    # Tabla de progreso para un seguimiento detallado del progreso individual
    st.subheader('Tabla de Progreso')
    st.write(datos_filtrados[['Dia', 'Persona', 'Maquina', 'Peso', 'Descanso', 'Sets', 'Repeticiones']])

    # Aplicar modelo de machine learning
    st.subheader('Predicción de Progreso')
    st.write('Utilizaremos un modelo de Random Forest para predecir el progreso en el gimnasio.')

    # Preparar los datos para el modelo
    datos_ml = datos_filtrados[['Peso', 'Descanso', 'Repeticiones']]
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
    st.write('No hay datos disponibles para los filtros seleccionados.')

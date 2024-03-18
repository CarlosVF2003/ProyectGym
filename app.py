# Importar librerias
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

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

# Tabla de Sesiones de Entrenamiento
st.header('Tabla de Sesiones de Entrenamiento')
st.write(st.session_state['Progreso_ind'][['Dia', 'Persona', 'Maquina', 'Peso', 'Descanso', 'Sets', 'Repeticiones']])

# Tabla de Resumen de Cada 7 días
st.header('Tabla de Resumen de Cada 7 días')
resumen_semanal = st.session_state['Progreso_ind'].groupby((st.session_state['Progreso_ind'].index // 7)).agg({'Peso': 'sum', 'Repeticiones': 'sum'})
st.write(resumen_semanal)

# Filtros
st.sidebar.header('Filtros')

# Filtro por Persona
filtro_persona = st.sidebar.selectbox('Selecciona persona:', ['Todos'] + list(st.session_state['Progreso_ind']['Persona'].unique()))

# Filtro por Máquina o Ejercicio
filtro_maquina = st.sidebar.selectbox('Selecciona máquina o ejercicio:', ['Todos'] + list(st.session_state['Progreso_ind']['Maquina'].unique()))

# Filtro por Rango de Días
min_dia = st.sidebar.number_input('Día mínimo:', min_value=1, max_value=31)
max_dia = st.sidebar.number_input('Día máximo:', min_value=min_dia, max_value=31)

# Aplicar filtros
datos_filtrados = st.session_state['Progreso_ind'].copy()
if filtro_persona != 'Todos':
    datos_filtrados = datos_filtrados[datos_filtrados['Persona'] == filtro_persona]
if filtro_maquina != 'Todos':
    datos_filtrados = datos_filtrados[datos_filtrados['Maquina'] == filtro_maquina]
datos_filtrados = datos_filtrados[(datos_filtrados['Dia'] >= min_dia) & (datos_filtrados['Dia'] <= max_dia)]

# Visualización de datos
if not datos_filtrados.empty:
    # Gráfico de Líneas para Pesos Levantados
    fig_pesos = px.line(datos_filtrados, x='Dia', y='Peso', color='Persona', title='Pesos Levantados por Día')
    fig_pesos.update_traces(line=dict(width=2.5))
    fig_pesos.for_each_trace(lambda t: t.update(name='Carlos' if t.name == 'Carlos' else 'Cinthia'))
    st.plotly_chart(fig_pesos)

    # Gráfico de Barras para Repeticiones
    fig_repeticiones = px.bar(datos_filtrados, x='Dia', y='Repeticiones', color='Persona', title='Repeticiones por Día')
    fig_repeticiones.update_traces(marker_line_width=1, marker_line_color="black")
    fig_repeticiones.for_each_trace(lambda t: t.update(name='Carlos' if t.name == 'Carlos' else 'Cinthia'))
    st.plotly_chart(fig_repeticiones)

    # Histograma de Peso Levantado
    fig_histograma = px.histogram(datos_filtrados, x='Peso', color='Persona', marginal='rug', title='Histograma de Peso Levantado')
    fig_histograma.update_traces(marker_line_width=0.5, marker_line_color="black")
    fig_histograma.for_each_trace(lambda t: t.update(name='Carlos' if t.name == 'Carlos' else 'Cinthia'))
    st.plotly_chart(fig_histograma)

    # Diagrama de Dispersión entre Peso y Repeticiones
    fig_dispersion = px.scatter(datos_filtrados, x='Peso', y='Repeticiones', color='Persona', title='Diagrama de Dispersión: Peso vs Repeticiones')
    fig_dispersion.update_traces(marker=dict(size=8))
    fig_dispersion.for_each_trace(lambda t: t.update(name='Carlos' if t.name == 'Carlos' else 'Cinthia'))
    st.plotly_chart(fig_dispersion)

    # Gráfico de Machine Learning
    st.subheader('Gráfico de Machine Learning')
    
    # Preparar los datos para el modelo de Machine Learning
    X = datos_filtrados[['Peso', 'Repeticiones']]
    y = datos_filtrados['Dia']
    
    # Entrenar el modelo de regresión lineal
    model = LinearRegression()
    model.fit(X, y)
    
    # Predicción de los días
    dias_prediccion = np.arange(X['Peso'].min(), X['Peso'].max()).reshape(-1, 1)
    repeticiones_prediccion = np.arange(X['Repeticiones'].min(), X['Repeticiones'].max()).reshape(-1, 1)
    X_prediccion = np.column_stack((dias_prediccion, repeticiones_prediccion))
    dias_predichos = model.predict(X_prediccion)
    
    # Crear el gráfico
    fig_ml = px.scatter_3d(datos_filtrados, x='Peso', y='Repeticiones', z='Dia', color='Persona', title='Predicción de Días utilizando Machine Learning')
    fig_ml.update_traces(marker=dict(size=4), selector=dict(mode='markers'))
    fig_ml.add_scatter3d(x=dias_prediccion.flatten(), y=repeticiones_prediccion.flatten(), z=dias_predichos, mode='lines', line=dict(color='black', width=2), name='Predicción')
    fig_ml.for_each_trace(lambda t: t.update(name='Carlos' if t.name == 'Carlos' else 'Cinthia'))
    st.plotly_chart(fig_ml)

else:
    st.warning('No hay datos disponibles para los filtros seleccionados.')

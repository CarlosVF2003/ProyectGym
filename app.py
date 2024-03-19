# Importar librerias
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
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
    return pesos, [repeticiones] * sets, [descanso] * sets

def formulario_mejora_resistencia(sets):
    pesos = [st.number_input(f'💪 Peso para el set {i+1}:', min_value=0, max_value=100, step=1) for i in range(sets)]
    repeticiones = [st.number_input(f'🏃 Repeticiones para el set {i+1}:', min_value=1, max_value=30, step=1) for i in range(sets)]
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return pesos, repeticiones, [descanso] * sets

def formulario_hipertrofia_muscular(sets):
    peso = st.number_input('💪 Peso (kg):', min_value=0, max_value=100, step=1)
    repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return [peso] * sets, [repeticiones] * sets, [descanso] * sets

# Título de la aplicación
st.title('🏋️‍♂️ Nuestro Progreso en el Gimnasio 🏋️‍♀️')

# Formulario desplegable y botón de guardar
with st.expander('📝 Registro de Datos'):
    Dia = st.text_input('Ingresa el Día 📆:')
    Persona = st.selectbox('Selecciona tu nombre 🤵‍♂️🙍:', ('Carlos', 'Cinthia'))
    Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', ('Prensa de Piernas', 'Multipowers', 'Máquina de Extensión de Cuádriceps', 'Máquina de Femorales', 'Máquina de Aductores', 'Máquina de Abductores','Press de pecho','Extension de hombro',
                                                                'Extension tricep en polea','Extension lateral','Extension frontal'))
    Enfoque = st.selectbox('Selecciona el enfoque de entrenamiento:', ('Desarrollo de Fuerza', 'Mejora de la Resistencia', 'Hipertrofia Muscular'))
    sets = st.number_input('Número de sets:', min_value=1, max_value=10, step=1, value=4)
    
    # Capturar datos según el enfoque de entrenamiento seleccionado
    if Enfoque == 'Desarrollo de Fuerza':
        pesos, repeticiones, descansos = formulario_desarrollo_fuerza(sets)
    elif Enfoque == 'Mejora de la Resistencia':
        pesos, repeticiones, descansos = formulario_mejora_resistencia(sets)
    else:  # Hipertrofia Muscular
        pesos, repeticiones, descansos = formulario_hipertrofia_muscular(sets)
        
    # Verificar que ambos formularios estén completos
    form_completo = all(pesos) and all(repeticiones) and all(descansos)
    
    # Si el formulario está completo, guardar los datos
    if form_completo:
        if st.button('Guardar'):
            for peso, repeticion, descanso in zip(pesos, repeticiones, descansos):
                Progreso_new = {'Dia': Dia, 'Persona': Persona, 'Maquina': Maquina, 'Peso': peso, 'Repeticiones': repeticion, 'Descanso': descanso, 'Sets': sets}
                st.session_state['Progreso_ind'] = st.session_state['Progreso_ind'].append(Progreso_new, ignore_index=True)
                st.success('Datos guardados exitosamente!')
    else:
        st.warning('Por favor completa todos los campos antes de guardar.')
        
# Mostrar tablas de datos de Carlos y Cinthia
if 'Progreso_ind' in st.session_state:
    st.header('Datos de Carlos')
    df_carlos = st.session_state['Progreso_ind'][st.session_state['Progreso_ind']['Persona'] == 'Carlos'].style.set_caption("Tabla de Carlos").applymap(lambda _: 'color: black')
    st.dataframe(df_carlos)

    st.header('Datos de Cinthia')
    df_cinthia = st.session_state['Progreso_ind'][st.session_state['Progreso_ind']['Persona'] == 'Cinthia'].style.set_caption("Tabla de Cinthia").applymap(lambda _: 'color: lightblue')
    st.dataframe(df_cinthia)

# Gráficos
if 'Progreso_ind' in st.session_state:
    st.header('Gráficos para Visualizar el Progreso')

    # Gráfico de Línea para Pesos Levantados
    fig_linea = px.line(st.session_state['Progreso_ind'], x='Dia', y='Peso', color='Persona', title='Pesos Levantados')
    fig_linea.update_traces(line=dict(color=['black', 'lightblue']), selector=dict(type='scatter'))
    st.plotly_chart(fig_linea)

    # Gráfico de Barras para Repeticiones o Sets
    fig_barras = px.bar(st.session_state['Progreso_ind'], x='Dia', y='Repeticiones', color='Persona', title='Repeticiones')
    fig_barras.update_traces(marker=dict(color=['black', 'lightblue']))
    st.plotly_chart(fig_barras)

    # Histograma de Pesos
    fig_hist = px.histogram(st.session_state['Progreso_ind'], x='Peso', color='Persona', title='Histograma de Pesos')
    fig_hist.update_traces(marker=dict(color=['black', 'lightblue']))
    st.plotly_chart(fig_hist)

    # Diagrama de Dispersión Peso vs Repeticiones
    fig_dispersion = px.scatter(st.session_state['Progreso_ind'], x='Peso', y='Repeticiones', color='Persona', title='Peso vs Repeticiones')
    fig_dispersion.update_traces(marker=dict(color=['black', 'lightblue']))
    st.plotly_chart(fig_dispersion)

# Algoritmo de Machine Learning (Random Forest Regression)
st.header('Algoritmo de Machine Learning: Random Forest Regression')
X = st.session_state['Progreso_ind'][['Repeticiones', 'Sets']]
y = st.session_state['Progreso_ind']['Peso']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
st.write(f'MSE (Error Cuadrático Medio): {mse}')

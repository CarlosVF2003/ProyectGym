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
    Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', ('Press de pecho','Extension de hombro','Extension tricep en polea','Extension lateral','Extension frontal','Peso muerto','Curl femoral','Abducción','Glúteo en maquina'))
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
            Progreso_new = pd.DataFrame({
                'Dia': [Dia] * sets,
                'Persona': [Persona] * sets,
                'Maquina': [Maquina] * sets,
                'Sets' : sets,
                'Peso': pesos,
                'Repeticiones': repeticiones,
                'Descanso': descansos
            })
            st.session_state['Progreso_ind'] = pd.concat([st.session_state['Progreso_ind'], Progreso_new], ignore_index=True)
            # Guardar el DataFrame actualizado en un archivo CSV
            # Utiliza transform para agregar la columna de conteo directamente al DataFrame existente
            if Enfoque != 'Hipertrofia Muscular':
                st.session_state['Progreso_ind']['Sets'] = st.session_state['Progreso_ind'].groupby(['Dia', 'Persona', 'Maquina', 'Peso', 'Descanso', 'Repeticiones'])[['Peso', 'Repeticiones']].transform('size')
            st.success('¡Datos registrados con éxito!')
            st.session_state['show_enfoque_form'] = False 
            st.session_state['Progreso_ind'].to_csv('Progreso.csv', index=False, sep=';')

# Agregar filtros
with st.sidebar:
    fecha_inicio = st.number_input('Selecciona el día de inicio:', min_value=1, max_value=31, step=1, value=1)
    fecha_fin = st.number_input('Selecciona el día de fin:', min_value=fecha_inicio, max_value=31, step=1, value=31)
    persona_filtro = st.multiselect('Selecciona las personas:', st.session_state['Progreso_ind']['Persona'].unique())
    maquina_filtro = st.multiselect('Selecciona las máquinas:', st.session_state['Progreso_ind']['Maquina'].unique())
    enfoque_filtro = st.multiselect('Selecciona el enfoque de entrenamiento:', ['Desarrollo de Fuerza', 'Mejora de la Resistencia', 'Hipertrofia Muscular'])
    peso_min = st.number_input('Peso mínimo (kg):', min_value=0, max_value=100, step=1, value=0)
    peso_max = st.number_input('Peso máximo (kg):', min_value=peso_min, max_value=100, step=1, value=100)
    repeticiones_min = st.number_input('Repeticiones mínimas:', min_value=1, max_value=30, step=1, value=1)
    repeticiones_max = st.number_input('Repeticiones máximas:', min_value=repeticiones_min, max_value=30, step=1, value=30)


with st.expander('📓 Datos Registrados'):
    st.subheader("Visualización de datos registrados")
    # Eliminar filas duplicadas basadas en las columnas específicas y actualizar los sets
    unique_values = st.session_state['Progreso_ind'].drop_duplicates(subset=['Dia', 'Persona', 'Maquina', 'Peso', 'Descanso', 'Repeticiones'])
    st.dataframe(unique_values.reset_index(drop=True))
    @st.cache_data
    def convert_df(unique_values):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return unique_values.to_csv().encode('utf-8')
    
    progreso = convert_df(my_Progreso)
    
    st.download_button(
        label="Download data as CSV",
        data=progreso,
        file_name='Progreso.csv',
        mime='text/csv',
    )
                 
# Mostrar tablas de datos de Carlos y Cinthia
with st.expander('🤵‍♂️ Tabla de datos de Carlos'):
    if 'Progreso_ind' in st.session_state:
        st.header('Datos de Carlos')
        df_carlos = unique_values[unique_values['Persona'] == 'Carlos']
        st.dataframe(df_carlos.reset_index(drop=True))

with st.expander('🙍 Tabla de datos de Cinthia'):
    if 'Progreso_ind' in st.session_state:
        st.header('Datos de Cinthia')
        df_cinthia = unique_values[unique_values['Persona'] == 'Cinthia']
        st.dataframe(df_cinthia.reset_index(drop=True))

# Gráficos
if 'Progreso_ind' in st.session_state:
    st.header('Gráficos para Visualizar el Progreso')

    # Gráfico de Línea para Pesos Levantados
    fig_linea = px.line(st.session_state['Progreso_ind'], x='Dia', y='Peso', color='Persona', title='Pesos Levantados')
    # Actualizar el color de Carlos a negro
    fig_linea.update_traces(line=dict(color='rgb(0,0,0)'), selector=dict(name='Carlos'))
    # Actualizar el color de Cinthia a celeste claro
    fig_linea.update_traces(line=dict(color='rgb(173,216,230)'), selector=dict(name='Cinthia'))
    st.plotly_chart(fig_linea)

    # Gráfico de Barras para Repeticiones o Sets
    fig_barras = px.bar(st.session_state['Progreso_ind'], x='Dia', y='Repeticiones', color='Persona', title='Repeticiones')
    # Actualizar el color de Carlos a negro
    fig_barras.update_traces(marker=dict(color='rgb(0,0,0)'), selector=dict(name='Carlos'))
    # Actualizar el color de Cinthia a celeste claro
    fig_barras.update_traces(marker=dict(color='rgb(173,216,230)'), selector=dict(name='Cinthia'))
    st.plotly_chart(fig_barras)

    # Histograma de Pesos
    fig_hist = px.histogram(st.session_state['Progreso_ind'], x='Peso', color='Persona', title='Histograma de Pesos')
    # Actualizar el color de Carlos a negro
    fig_hist.update_traces(marker=dict(color='rgb(0,0,0)'), selector=dict(name='Carlos'))
    # Actualizar el color de Cinthia a celeste claro
    fig_hist.update_traces(marker=dict(color='rgb(173,216,230)'), selector=dict(name='Cinthia'))
    st.plotly_chart(fig_hist)

    # Diagrama de Dispersión Peso vs Repeticiones
    fig_dispersion = px.scatter(st.session_state['Progreso_ind'], x='Peso', y='Repeticiones', color='Persona', title='Peso vs Repeticiones')
    # Actualizar el color de Carlos a negro
    fig_dispersion.update_traces(marker=dict(color='rgb(0,0,0)'), selector=dict(name='Carlos'))
    # Actualizar el color de Cinthia a celeste claro
    fig_dispersion.update_traces(marker=dict(color='rgb(173,216,230)'), selector=dict(name='Cinthia'))
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

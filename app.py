# Importar librerias
import pandas as pd
import streamlit as st
import altair as alt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from pathlib import Path
from base64 import b64encode

# Cargar el archivo Progreso.csv si existe
if 'Progreso_ind' not in st.session_state:
    if Path("Progreso.csv").is_file():
        st.session_state['Progreso_ind'] = pd.read_csv("Progreso.csv")
    else:
        st.session_state['Progreso_ind'] = pd.DataFrame()

# Definir las funciones
def formulario_desarrollo_fuerza(Sets):
    pesos = []
    for i in range(Sets):
        peso = st.number_input(f'💪 Peso para el Sets {i+1}:', min_value=0.0, step=0.1, format="%.1f")
        pesos.append(peso)

    repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return pesos, [repeticiones] * Sets, [descanso] * Sets

def formulario_mejora_resistencia(Sets):
    pesos = []
    for i in range(Sets):
        peso = st.number_input(f'💪 Peso para el Sets {i+1}:', min_value=0.0, step=0.1, format="%.1f")
        pesos.append(peso)

    repeticiones = [st.number_input(f'🏃 Repeticiones para el Sets {i+1}:', min_value=1, max_value=30, step=1) for i in range(Sets)]
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return pesos, repeticiones, [descanso] * Sets

def formulario_hipertrofia_muscular(Sets):
    peso = st.number_input('💪 Peso (kg):', min_value=0.0, step=0.1, format="%.1f")
    repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return [peso] * Sets, [repeticiones] * Sets, [descanso] * Sets

# Función para descargar DataFrame como CSV
def download_csv(df, filename):
    df = df[['Dia', 'Persona', 'Maquina', 'Peso','Sets','Repeticiones','Descanso']]
    csv = df.to_csv(index=False, sep=',', encoding='utf-8').encode('utf-8')
    href = f'<a href="data:text/csv;base64,{b64encode(csv).decode()}" download="{filename}.csv">Descargar CSV</a>'
    return href

# Función para calcular el promedio de peso por día y máquina
def calcular_promedio(df):
    return df.groupby(['Dia', 'Maquina']).apply(lambda x: (x['Peso'] / x['Repeticiones']).mean()).reset_index(name='Promedio')

# Función para crear gráficos de líneas y barras
def crear_graficos(df_grupo, colores):
    # Filtrar datos para Carlos y Cinthia
    df_carlos = df_grupo[df_grupo['Persona'] == 'Carlos']
    df_cinthia = df_grupo[df_grupo['Persona'] == 'Cinthia']

    # Calcula el promedio de peso levantado por día y máquina
    df_grupo['promedio_peso'] = df_grupo.groupby(['Dia', 'Maquina']).apply(lambda x: (x['Peso'] * x['Sets'] * x['Repeticiones']).sum() / (x['Sets'] * x['Repeticiones']).sum()).reset_index(name='Promedio de Peso')

    # Gráfico de líneas del promedio de peso levantado por día para ambas personas
    line_chart = alt.Chart(df_grupo).mark_line().encode(
        x='Dia:O',
        y=alt.Y('promedio_peso:Q', title='Promedio de Peso'),
        color=alt.Color('Persona:N', scale=alt.Scale(domain=['Carlos', 'Cinthia'], range=['black', 'lightblue'])),
        tooltip=['Persona', 'Dia', 'promedio_peso']
    ).properties(
        title="Promedio de Peso Levantado"
    )
    st.altair_chart(line_chart, use_container_width=True)

    # Gráfico de barras del total de repeticiones por día para ambas personas
    bar_chart = alt.Chart(df_grupo).mark_bar().encode(
        x='Dia:O',
        y=alt.Y('sum(Repeticiones):Q', title='Total de Repeticiones'),
        color=alt.Color('Persona:N', scale=alt.Scale(domain=['Carlos', 'Cinthia'], range=['black', 'lightblue'])),
        tooltip=['Persona', 'Dia', 'sum(Repeticiones)']
    ).properties(
        title="Total de Repeticiones"
    )
    st.altair_chart(bar_chart, use_container_width=True)



# Título de la aplicación
st.title('🏋️‍♂️ Nuestro Progreso en el Gym 🏋️‍♀️')

# Formulario desplegable y botón de guardar
with st.expander('📝 Registro de Datos'):
    Dia = st.text_input('Ingresa el Día 📆:')
    Persona = st.selectbox('Selecciona tu nombre 🤵‍♂️🙍:', ('Carlos', 'Cinthia'))
    Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', ('Press de pecho','Extensión de hombro','Extensión de tríceps en polea','Extensión lateral','Extensión frontal','Jalón polea alta prono','Jalón polea alta supino','Remo sentado con polea','Curl biceps','Curl martillo','Peso muerto','Leg Curl','Abducción'
                                                          ,'Glúteo en maquina','Leg press','Hack squat','Aducción','Leg extension','Hip thrust'))
    Enfoque = st.selectbox('Selecciona el enfoque de entrenamiento:', ('Desarrollo de Fuerza', 'Mejora de la Resistencia', 'Hipertrofia Muscular'))
    Sets = st.number_input('Número de Sets:', min_value=1, max_value=10, step=1, value=4)
    
    # Capturar datos según el enfoque de entrenamiento seleccionado
    if Enfoque == 'Desarrollo de Fuerza':
        pesos, repeticiones, descansos = formulario_desarrollo_fuerza(Sets)
    elif Enfoque == 'Mejora de la Resistencia':
        pesos, repeticiones, descansos = formulario_mejora_resistencia(Sets)
    else:  # Hipertrofia Muscular
        pesos, repeticiones, descansos = formulario_hipertrofia_muscular(Sets)
        
    # Verificar que ambos formularios estén completos
    form_completo = all(pesos) and all(repeticiones) and all(descansos)
    

    # Si el formulario está completo, guardar los datos
    if form_completo:
        if Maquina in ['Press de pecho', 'Extensión de hombro', 'Extensión de tríceps en polea', 'Extensión lateral', 'Extensión frontal','Jalón polea alta prono','Jalón polea alta supino','Remo sentado con polea','Curl biceps','Curl martillo']:
            musculo = 'Brazo'
        elif Maquina in ['Peso muerto', 'Leg Curl','Hip thrust', 'Abducción', 'Glúteo en maquina', 'Leg press', 'Hack squat', 'Aducción', 'Leg extension']:
            musculo = 'Pierna'
        else:
            musculo = 'Desconocido'
        if st.button('Guardar'):
            Progreso_new = pd.DataFrame({
                'Dia': [Dia] * Sets,
                'Persona': [Persona] * Sets,
                'Maquina': [Maquina] * Sets,
                'Musculo': [musculo] * Sets,
                'Sets' : Sets,
                'Peso': pesos,
                'Repeticiones': repeticiones,
                'Descanso': descansos
            })
            st.session_state['Progreso_ind'] = pd.concat([st.session_state['Progreso_ind'], Progreso_new], ignore_index=True)
            # Guardar el DataFrame actualizado en un archivo CSV
            # Utiliza transform para agregar la columna de conteo directamente al DataFrame existente
            if Enfoque != 'Hipertrofia Muscular':
                st.session_state['Progreso_ind']['Sets'] = st.session_state['Progreso_ind'].groupby(['Dia', 'Persona', 'Maquina', 'Peso','Descanso','Repeticiones'])[['Peso', 'Repeticiones']].transform('size')
            st.success('¡Datos registrados con éxito!')
            st.session_state['show_enfoque_form'] = False 
            st.session_state['Progreso_ind'].to_csv('Progreso.csv', index=False)


with st.expander('📓 Datos Registrados'):
    st.subheader("Visualización de datos registrados")
    # Eliminar filas duplicadas basadas en las columnas específicas y actualizar los sets
    unique_values = st.session_state['Progreso_ind'].drop_duplicates(subset=['Dia', 'Persona', 'Maquina', 'Peso','Sets', 'Repeticiones','Descanso'])
    st.dataframe(unique_values.reset_index(drop=True))
    st.markdown(download_csv(unique_values, 'Progreso'), unsafe_allow_html=True)
    df_filtred = unique_values


         
# Mostrar tablas de datos de Carlos y Cinthia
with st.expander('🤵‍♂️ Tabla de datos de Carlos'):
    if 'Progreso_ind' in st.session_state:
        st.header('Datos de Carlos')
        df_carlos = df_filtred[df_filtred['Persona'] == 'Carlos']
        st.dataframe(df_carlos.reset_index(drop=True))

with st.expander('🙍 Tabla de datos de Cinthia'):
    if 'Progreso_ind' in st.session_state:
        st.header('Datos de Cinthia')
        df_cinthia = df_filtred[df_filtred['Persona'] == 'Cinthia']
        st.dataframe(df_cinthia.reset_index(drop=True))
        
# Crear pestañas con los nombres proporcionados
tab1, tab2, tab3, tab4 = st.tabs(["Cuadriceps", "Espalda y Biceps", "Gluteos y femorales", "Pectorales, hombros y triceps"])
    
# Gráficos
if 'Progreso_ind' in st.session_state:
    # Añadir una columna para los músculos
    st.session_state['Progreso_ind'].loc[st.session_state['Progreso_ind']['Maquina'].isin(['Press de pecho', 'Extensión de hombro', 'Extensión de tríceps en polea', 'Extensión lateral', 'Extensión frontal','Jalón polea alta prono','Jalón polea alta supino','Remo sentado con polea','Curl biceps','Curl martillo']), 'Musculo'] = 'Brazo'
    st.session_state['Progreso_ind'].loc[st.session_state['Progreso_ind']['Maquina'].isin(['Peso muerto', 'Leg Curl','Hip thrust', 'Abducción', 'Glúteo en maquina', 'Leg press', 'Hack squat', 'Aducción', 'Leg extension']), 'Musculo'] = 'Pierna'
    # Añadir una columna para los grupos musculares
    st.session_state['Progreso_ind'].loc[st.session_state['Progreso_ind']['Maquina'].isin(['Press de pecho', 'Extensión de hombro', 'Extensión de tríceps en polea', 'Extensión lateral', 'Extensión frontal']), 'GM'] = 'D'
    st.session_state['Progreso_ind'].loc[st.session_state['Progreso_ind']['Maquina'].isin(['Jalón polea alta prono','Jalón polea alta supino','Remo sentado con polea','Curl biceps','Curl martillo']), 'GM'] = 'B'
    
    st.session_state['Progreso_ind'].loc[st.session_state['Progreso_ind']['Maquina'].isin(['Peso muerto', 'Leg Curl','Hip thrust', 'Abducción', 'Glúteo en maquina']), 'GM'] = 'C'
    st.session_state['Progreso_ind'].loc[st.session_state['Progreso_ind']['Maquina'].isin(['Leg press', 'Hack squat', 'Aducción', 'Leg extension']), 'GM'] = 'A'
       
    colores = {'Carlos': 'black', 'Cinthia': 'lightblue'}
    # Suponiendo que 'st.session_state['Progreso_ind']' ya contiene el DataFrame con los datos necesarios
    df = st.session_state['Progreso_ind']

    with tab1:
        st.header("Cuadriceps (A)")
        df_cuadriceps = df[df['GM'] == 'A']
        crear_graficos(df_cuadriceps, colores)
    
    with tab2:
        st.header("Espalda y Biceps (B)")
        df_espalda_biceps = df[df['GM'] == 'B']
        crear_graficos(df_espalda_biceps, colores)
    
    with tab3:
        st.header("Gluteos y femorales (C)")
        df_gluteos_femorales = df[df['GM'] == 'C']
        crear_graficos(df_gluteos_femorales, colores)
    
    with tab4:
        st.header("Hombro, tricep y pecho (D)")
        df_pectoral_hombros_triceps = df[df['GM'] == 'D']
        crear_graficos(df_pectoral_hombros_triceps, colores)
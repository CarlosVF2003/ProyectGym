# Importar bibliotecas necesarias
import pandas as pd
import streamlit as st
import plotly as px
from pathlib import Path
from base64 import b64encode

# Configuración inicial y carga de datos
def cargar_datos():
    if 'Progreso' not in st.session_state:
        if Path("Progreso.csv").exists():
            st.session_state['Progreso'] = pd.read_csv("Progreso.csv")
        else:
            st.session_state['Progreso'] = pd.DataFrame()

# Funciones para formularios según el enfoque de entrenamiento
def formulario_desarrollo_fuerza(Sets):
    pesos = []
    repeticiones = []
    for i in range(Sets):
        peso = st.number_input(f'💪 Peso para el Set {i + 1}:', min_value=0.0, step=0.1, format="%.1f")
        rep = st.number_input(f'Repeticiones para el Set {i + 1}:', min_value=1, max_value=30, step=1)
        pesos.append(peso)
        repeticiones.append(rep)
    descanso = st.selectbox('Tiempo de descanso:', ['1-2 min', '2-3 min', '3-4 min'])
    return pesos, repeticiones, [descanso] * Sets

def formulario_mejora_resistencia(Sets):
    pesos = []
    repeticiones = []
    for i in range(Sets):
        peso = st.number_input(f'💪 Peso para el Set {i + 1}:', min_value=0.0, step=0.1, format="%.1f")
        rep = st.number_input(f'Repeticiones para el Set {i + 1}:', min_value=1, max_value=30, step=1)
        pesos.append(peso)
        repeticiones.append(rep)
    descanso = st.selectbox('Tiempo de descanso:', ['1-2 min', '2-3 min', '3-4 min'])
    return pesos, repeticiones, [descanso] * Sets

def formulario_hipertrofia_muscular(Sets):
    peso = st.number_input('💪 Peso (kg):', min_value=0.0, step=0.1, format="%.1f")
    repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    descanso = st.selectbox('Tiempo de descanso:', ['1-2 min', '2-3 min', '3-4 min'])
    return [peso] * Sets, [repeticiones] * Sets, [descanso] * Sets

# Función para calcular el peso ajustado
def calcular_peso_ajustado(pesos, maquina, unidad_peso):
    # Convertir de libras a kg si es necesario
    if unidad_peso == 'lb':
        pesos = [peso * 0.453592 for peso in pesos]
    
    # Lista de máquinas que requieren multiplicar el peso por 2
    maquinas_multiplicar_peso = [
        'Extensión lateral', 'Extensión frontal', 'Curl biceps',
        'Curl martillo', 'Glúteo en maquina', 'Hack squat', 'Hip thrust', 'Leg press'
    ]
    
    if maquina in maquinas_multiplicar_peso:
        pesos = [peso * 2 for peso in pesos]
    
    return pesos

# Función para descargar DataFrame como CSV
def download_csv(df, filename):
    csv = df.to_csv(index=False, sep=',').encode('utf-8')
    b64 = b64encode(csv).decode()
    href = f'<a href="data:text/csv;base64,{b64}" download="{filename}.csv">Descargar CSV</a>'
    return href

# Función para calcular el promedio de peso por día
def calcular_promedio(df):
    df['Peso_Total'] = df['Peso'] * df['Repeticiones']
    promedio_df = df.groupby(['Persona', 'Dia']).apply(
        lambda x: x['Peso_Total'].sum() / x['Repeticiones'].sum()
    ).reset_index(name='Promedio_Ponderado')
    return promedio_df

# Función para crear gráficos de cascada
def crear_grafico_cascada(df, colores):
    # Calcular el promedio de peso levantado por día
    promedio_df = calcular_promedio(df)
    
    # Crear gráfico de cascada usando Plotly
    fig = px.waterfall(
        promedio_df,
        x='Dia',
        y='Promedio_Ponderado',
        base=0,
        color='Persona',
        title='Gráfico de Cascada del Promedio de Peso Levantado',
        labels={'Persona': 'Persona', 'Dia': 'Día', 'Promedio_Ponderado': 'Promedio de Peso (kg)'},
        color_discrete_map=colores,
    )
    
    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

# Título de la aplicación
st.title('🏋️‍♂️ Análisis de Progreso en el Gimnasio 🏋️‍♀️')

# Cargar datos
cargar_datos()

# Registro de datos de entrenamiento
with st.expander('📝 Registro de Datos'):
    Dia = st.text_input('Ingresa el Día 📆:')
    Persona = st.selectbox('Selecciona tu nombre 🤵‍♂️🙍:', ['Carlos', 'Cinthia'])
    Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', [
        'Press de pecho', 'Extensión de hombro', 'Extensión de tríceps en polea', 'Extensión lateral', 'Extensión frontal',
        'Jalón polea alta prono', 'Jalón polea alta supino', 'Remo sentado con polea', 'Curl biceps', 'Curl martillo',
        'Peso muerto', 'Leg Curl', 'Abducción', 'Glúteo en maquina', 'Leg press', 'Hack squat', 'Aducción', 'Leg extension', 'Hip thrust'
    ])
    
    Enfoque = st.selectbox('Selecciona el enfoque de entrenamiento:', ['Desarrollo de Fuerza', 'Mejora de la Resistencia', 'Hipertrofia Muscular'])

    Sets = st.number_input('Número de Sets:', min_value=1, max_value=10, step=1)
    unidad_peso = st.selectbox('Unidad de Peso:', ['kg', 'lb'])

    # Capturar datos según el enfoque de entrenamiento
    if Enfoque == 'Desarrollo de Fuerza':
        pesos, repeticiones, descansos = formulario_desarrollo_fuerza(Sets)
    elif Enfoque == 'Mejora de la Resistencia':
        pesos, repeticiones, descansos = formulario_mejora_resistencia(Sets)
    elif Enfoque == 'Hipertrofia Muscular':
        pesos, repeticiones, descansos = formulario_hipertrofia_muscular(Sets)

    # Calcular peso ajustado
    pesos = calcular_peso_ajustado(pesos, Maquina, unidad_peso)

    # Verificar que los formularios estén completos
    form_completo = all(pesos) and all(repeticiones) and all(descansos)

    # Si el formulario está completo, guardar los datos
    if form_completo:
        if st.button('Guardar'):
            # Crear un DataFrame con los nuevos datos
            nuevos_datos = pd.DataFrame({
                'Dia': [Dia] * Sets,
                'Persona': [Persona] * Sets,
                'Maquina': [Maquina] * Sets,
                'Sets': Sets,
                'Peso': pesos,
                'Repeticiones': repeticiones,
                'Descanso': descansos,
            })
            
            # Concatenar DataFrames y guardar en archivo CSV
            st.session_state['Progreso'] = pd.concat([st.session_state['Progreso'], nuevos_datos])
            st.session_state['Progreso'].to_csv("Progreso.csv", index=False)
            st.success('Datos guardados correctamente.')

# Gráfico de cascada
with st.expander('📈 Gráfico de Cascada'):
    # Definir colores para cada persona
    colores = {'Carlos': 'blue', 'Cinthia': 'pink'}
    
    # Crear y mostrar gráfico de cascada
    crear_grafico_cascada(st.session_state['Progreso'], colores)

# Expander para descarga de datos
with st.expander('📥 Descarga de Datos'):
    if 'Progreso' in st.session_state:
        df = st.session_state['Progreso']
        download_link = download_csv(df, 'Progreso')
        st.markdown(download_link, unsafe_allow_html=True)

# %%
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

# %%
# Crear pestañas con los nombres proporcionados
tab1, tab2, tab3, tab4 = st.tabs(["Cuadriceps", "Espalda y Biceps", "Gluteos y femorales", "Pectorales, hombros y triceps"])

# %%
# Etiquetar los grupos musculares
df.loc[df['Maquina'].isin(['Press de pecho', 'Extensión de hombro', 'Extensión de tríceps en polea', 'Extensión lateral', 'Extensión frontal']), 'GM'] = 'D'
df.loc[df['Maquina'].isin(['Jalón polea alta prono', 'Jalón polea alta supino', 'Remo sentado con polea', 'Curl biceps', 'Curl martillo']), 'GM'] = 'B'
df.loc[df['Maquina'].isin(['Peso muerto', 'Leg Curl', 'Hip thrust', 'Abducción', 'Glúteo en maquina']), 'GM'] = 'C'
df.loc[df['Maquina'].isin(['Leg press', 'Hack squat', 'Aducción', 'Leg extension']), 'GM'] = 'A'

# %%
# Gráficos
if 'Progreso_ind' in st.session_state:
    colores = {'Carlos': 'black', 'Cinthia': 'lightblue'}
    
    with tab1:
        st.header("Cuadriceps (A)")
        df_cuadriceps = df[df['GM'] == 'A']
        df_cuadriceps = df_cuadriceps.reset_index(drop=True)
        crear_grafico_cascada(df_cuadriceps, colores)

    with tab2:
        st.header("Espalda y Biceps (B)")
        df_espalda_biceps = df[df['GM'] == 'B']
        df_espalda_biceps = df_espalda_biceps.reset_index(drop=True)
        crear_grafico_cascada(df_espalda_biceps, colores)

    with tab3:
        st.header("Gluteos y femorales (C)")
        df_gluteos_femorales = df[df['GM'] == 'C']
        df_gluteos_femorales = df_gluteos_femorales.reset_index(drop=True)
        crear_grafico_cascada(df_gluteos_femorales, colores)

    with tab4:
        st.header("Pectorales, hombros y triceps (D)")
        df_pectoral_hombros_triceps = df[df['GM'] == 'D']
        df_pectoral_hombros_triceps = df_pectoral_hombros_triceps.reset_index(drop=True)
        crear_grafico_cascada(df_pectoral_hombros_triceps, colores)

# %%
# Importamos librerías
import pandas as pd
import streamlit as st
from pathlib import Path
from base64 import b64encode
import altair as alt

# %%
# Cargar datos solo una vez
if 'Progreso_ind' not in st.session_state:
    if Path("Progreso.csv").exists():
        st.session_state['Progreso_ind'] = pd.read_csv("Progreso.csv")
    else:
        st.session_state['Progreso_ind'] = pd.DataFrame()

# Funciones de formularios de entrenamiento
def formulario_desarrollo_fuerza(Sets):
    pesos = []
    for i in range(Sets):
        peso = st.number_input(f'💪 Peso para el Sets {i + 1}:', min_value=0.0, step=0.1, format="%.1f")
        pesos.append(peso)

    repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return pesos, [repeticiones] * Sets, [descanso] * Sets

def formulario_mejora_resistencia(Sets):
    pesos = []
    for i in range(Sets):
        peso = st.number_input(f'💪 Peso para el Sets {i + 1}:', min_value=0.0, step=0.1, format="%.1f")
        pesos.append(peso)

    repeticiones = [st.number_input(f'🏃 Repeticiones para el Sets {i + 1}:', min_value=1, max_value=30, step=1) for i in range(Sets)]
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return pesos, repeticiones, [descanso] * Sets

def formulario_hipertrofia_muscular(Sets):
    peso = st.number_input('💪 Peso (kg):', min_value=0.0, step=0.1, format="%.1f")
    repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return [peso] * Sets, [repeticiones] * Sets, [descanso] * Sets

def calcular_peso_ajustado(pesos, maquina, unidad_peso):
    # Convertir el peso de lb's a kg si es necesario
    if unidad_peso == 'lb':
        pesos = [peso * 0.453592 for peso in pesos]

    # Multiplicar el peso si la máquina está en la lista específica
    maquinas_multiplicar_peso = [
        'Extensión lateral', 'Extensión frontal', 'Curl biceps',
        'Curl martillo', 'Glúteo en maquina', 'Hack squat', 'Hip thrust', 'Leg press'
    ]
    
    if maquina in maquinas_multiplicar_peso:
        pesos = [peso * 2 for peso in pesos]

    return pesos

# Función para descargar DataFrame como CSV
def download_csv(df, filename):
    required_columns = ['Dia', 'Persona', 'Maquina', 'Peso', 'Descanso', 'Sets', 'Repeticiones']
    
    # Verificar si todas las columnas requeridas están presentes en el DataFrame
    if all(col in df.columns for col in required_columns):
        df_subset = df[required_columns]
        csv = df_subset.to_csv(index=False, sep=',', encoding='utf-8').encode('utf-8')
        href = f'<a href="data:text/csv;base64,{b64encode(csv).decode()}" download="{filename}.csv">Descargar</a>'
        return href
    else:
        return "No se pueden descargar los datos debido a columnas faltantes."

# Función para calcular el promedio de peso levantado por día
def calcular_promedio(df):
    df['Sets_x_Reps'] = df['Sets'] * df['Repeticiones']
    df['Peso_Total'] = df['Peso'] * df['Sets_x_Reps']
    
    # Agrupar datos por persona y día, calculando el promedio ponderado
    promedio_ponderado = df.groupby(['Persona', 'Dia']).apply(
        lambda x: (x['Peso_Total'].sum() / x['Sets_x_Reps'].sum())
    ).reset_index(name='Promedio_Ponderado')
    
    # Combinar con datos originales para obtener el total de repeticiones
    df_agrupado = df.groupby(['Persona', 'Dia']).agg({'Repeticiones': 'sum'}).reset_index()
    df_agrupado.rename(columns={'Repeticiones': 'Suma_Repeticiones'}, inplace=True)
    
    # Combinar resultados finales
    resultado_final = promedio_ponderado.merge(df_agrupado, on=['Persona', 'Dia'])
    resultado_final['Dia_ordenado'] = resultado_final.groupby('Persona').cumcount() + 1
    
    return resultado_final

# Función para crear gráficos de líneas
def crear_graficos(df_grupo, colores):
    # Calcular el promedio de peso levantado por día
    resultado_final = calcular_promedio(df_grupo)
    
    # Gráfico de líneas del promedio de peso levantado por día
    line_chart = alt.Chart(resultado_final).mark_line().encode(
        x=alt.X('Dia_ordenado:O', title='Día'),  # Categorizar días como ordinales
        y=alt.Y('Promedio_Ponderado:Q', title='Promedio de Peso Levantado (kg)'),
        color=alt.Color('Persona:N', scale=alt.Scale(range=[colores['Carlos'], colores['Cinthia']]), title='Persona'),
        tooltip=['Persona', 'Dia_ordenado', 'Promedio_Ponderado']
    ).properties(
        title="Promedio de Peso Levantado por Día"
    )
    st.altair_chart(line_chart, use_container_width=True)

    # Gráfico de barras del total de repeticiones por día
    bar_chart = alt.Chart(resultado_final).mark_bar().encode(
        x=alt.X('Dia_ordenado:O', title='Día'),  # Categorizar días como ordinales
        y=alt.Y('Suma_Repeticiones:Q', title='Total de Repeticiones'),
        color=alt.Color('Persona:N', scale=alt.Scale(range=[colores['Carlos'], colores['Cinthia']]), title='Persona'),
        tooltip=['Persona', 'Dia_ordenado', 'Suma_Repeticiones']
    ).properties(
        title="Total de Repeticiones por Día"
    )
    st.altair_chart(bar_chart, use_container_width=True)

# Función para crear gráfico de cascada
def crear_grafico_cascada(df_grupo, colores):
    # Calcular el promedio de peso levantado por día
    resultado_final = calcular_promedio(df_grupo)
    
    # Calcular la diferencia acumulada del promedio de peso levantado
    resultado_final['Diferencia_Acumulada'] = resultado_final.groupby('Persona')['Promedio_Ponderado'].cumsum()
    
    # Crear gráfico de cascada
    cascada_chart = alt.Chart(resultado_final).mark_bar().encode(
        x=alt.X('Dia_ordenado:O', title='Día'),  # Categorizar días como ordinales
        y='Diferencia_Acumulada:Q',
        color=alt.Color('Persona:N', scale=alt.Scale(range=[colores['Carlos'], colores['Cinthia']]), title='Persona'),
        tooltip=['Persona', 'Dia_ordenado', 'Diferencia_Acumulada', 'Promedio_Ponderado']
    ).properties(
        title="Gráfico de Cascada del Promedio de Peso Levantado"
    )
    
    # Mostrar gráfico en Streamlit
    st.altair_chart(cascada_chart, use_container_width=True)

# %%
# Título de la aplicación
st.title('🏋️‍♂️ Nuestro Progreso en el Gym 🏋️‍♀️')

with st.expander('📝 Registro de Datos'):
    Dia = st.text_input('Ingresa el Día 📆:')
    Persona = st.selectbox('Selecciona tu nombre 🤵‍♂️🙍:', ('Carlos', 'Cinthia'))
    Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', ('Press de pecho', 'Extensión de hombro', 'Extensión de tríceps en polea',
                                                         'Extensión lateral', 'Extensión frontal', 'Jalón polea alta prono',
                                                         'Jalón polea alta supino', 'Remo sentado con polea', 'Curl biceps',
                                                         'Curl martillo', 'Peso muerto', 'Leg Curl', 'Abducción',
                                                         'Glúteo en maquina', 'Leg press', 'Hack squat', 'Aducción', 'Leg extension', 'Hip thrust'))

    Enfoque = st.selectbox('Selecciona el enfoque de entrenamiento:', ('Desarrollo de Fuerza', 'Mejora de la Resistencia', 'Hipertrofia Muscular'))

    # Define Sets, pesos, repeticiones, y descanso basados en el enfoque
    Sets = st.number_input('Número de Sets:', min_value=1, max_value=10, step=1, value=4)
    unidad_peso = st.selectbox('Unidad de Peso:', ('kg', 'lb'))

    # Capturar datos según el enfoque de entrenamiento seleccionado
    if Enfoque == 'Desarrollo de Fuerza':
        pesos, repeticiones, descanso = formulario_desarrollo_fuerza(Sets)
    elif Enfoque == 'Mejora de la Resistencia':
        pesos, repeticiones, descanso = formulario_mejora_resistencia(Sets)
    else:
        pesos, repeticiones, descanso = formulario_hipertrofia_muscular(Sets)

    # Calcular peso ajustado
    pesos = calcular_peso_ajustado(pesos, Maquina, unidad_peso)

    # Verificar que los formularios estén completos
    form_completo = all(pesos) and all(repeticiones) and all(descanso)

    # Si el formulario está completo, guardar los datos
    if form_completo:
        if st.button('Guardar'):
            # Crea un DataFrame con los nuevos datos
            Progreso_new = pd.DataFrame({
                'Dia': [Dia] * Sets,
                'Persona': [Persona] * Sets,
                'Maquina': [Maquina] * Sets,
                'Sets': Sets,
                'Peso': pesos,
                'Repeticiones': repeticiones,
                'Descanso': descanso
            })
            
            # Concatenar DataFrames y reiniciar el índice
            st.session_state['Progreso_ind'] = pd.concat([st.session_state['Progreso_ind'], Progreso_new], ignore_index=True)
            st.session_state['Progreso_ind'].to_csv('Progreso.csv', index=False)
            
            # Mostrar mensaje de éxito
            st.success('¡Datos registrados con éxito!')

# %%
# Datos generales registrados
with st.expander('📓 Datos Registrados'):
    st.subheader("Visualización de datos registrados")
    # Eliminar filas duplicadas basadas en las columnas específicas y actualizar los sets
    unique_values = st.session_state['Progreso_ind'].drop_duplicates(subset=['Dia', 'Persona', 'Maquina', 'Peso', 'Sets', 'Repeticiones', 'Descanso'])
    st.dataframe(unique_values.reset_index(drop=True))
    st.markdown(download_csv(unique_values, "Progreso"), unsafe_allow_html=True)

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

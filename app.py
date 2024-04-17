# Importamos librerías
import pandas as pd
import streamlit as st
from pathlib import Path
from base64 import b64encode
import altair as alt

# Cargar datos solo una vez
if 'Progreso_ind' not in st.session_state:
    if Path("Progreso.csv").exists():
        st.session_state['Progreso_ind'] = pd.read_csv("Progreso.csv")
    else:
        st.session_state['Progreso_ind'] = pd.DataFrame()

def formulario_desarrollo_fuerza(Sets):
    pesos = []
    for i in range(Sets):
        peso = st.number_input(f'💪 Peso para el Sets {i + 1}:', min_value=0.0, step=0.1, format="%.1f")
        pesos.append(peso)

    repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return pesos, [repeticiones] * Sets, [descansos] * Sets

def formulario_mejora_resistencia(Sets):
    pesos = []
    for i in range(Sets):
        peso = st.number_input(f'💪 Peso para el Sets {i + 1}:', min_value=0.0, step=0.1, format="%.1f")
        pesos.append(peso)

    repeticiones = [st.number_input(f'🏃 Repeticiones para el Sets {i + 1}:', min_value=1, max_value=30, step=1) for i in range(Sets)]
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return pesos, repeticiones, [descansos] * Sets

def formulario_hipertrofia_muscular(Sets):
    peso = st.number_input('💪 Peso (kg):', min_value=0.0, step=0.1, format="%.1f")
    repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return [peso] * Sets, [repeticiones] * Sets, [descansos] * Sets

def calcular_peso_ajustado(pesos, maquina, unidad_peso):
    # Convertir el peso de lb's a kg si es necesario
    if unidad_peso == 'lb':
        pesos = [peso * 0.453592 for peso in pesos]

    # Duplicar el peso si la máquina está en la lista específica
    maquinas_multiplicar_peso = [
        'Extensión lateral', 'Extensión frontal', 'Curl biceps',
        'Curl martillo', 'Glúteo en maquina', 'Hack squat', 'Hip thrust','Leg press'
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

# Función para calcular el promedio de peso por día y máquina
def calcular_promedio(df):    
    df['Sets_x_Reps'] = df['Sets'] * df['Repeticiones']
    df['Peso_Total'] = df['Peso'] * df['Sets'] * df['Repeticiones']
    
    # Calcula la suma de repeticiones por persona y día
    df['Suma_Repeticiones'] = df.groupby(['Persona', 'Dia'])['Repeticiones'].transform('sum')
        
    # Agrupa por persona y día, y calcula el promedio ponderado
    promedio_ponderado_por_persona = df.groupby(['Persona', 'Dia']).apply(
        lambda x: (x['Peso_Total'].sum() / x['Sets_x_Reps'].sum())
    ).reset_index(name='Promedio_Ponderado')
        
    # Une los resultados con la suma de repeticiones
    resultado_final = df[['Persona', 'Dia', 'Suma_Repeticiones']].drop_duplicates().merge(
    promedio_ponderado_por_persona, on=['Persona', 'Dia'])
    return resultado_final

def crear_graficos(df_grupo, colores):
    # Calcular el promedio de peso por día y máquina
    resultado_final = calcular_promedio(df_grupo)
    
    # Gráfico de líneas del promedio de peso levantado por día para ambas personas
    line_chart = alt.Chart(resultado_final).mark_line().encode(
        x=alt.X('Dia:T', title='Día'),
        y=alt.Y('Promedio_Ponderado', title='Promedio de Peso (kg)'),
        color=alt.Color('Persona:N', scale=alt.Scale(range=[colores['Carlos'], colores['Cinthia']]), title='Persona'),
        tooltip=['Persona', 'Dia', 'Promedio_Ponderado']
    ).properties(
        title="Promedio de Peso Levantado por Día"
    )

    # Gráfico de barras del total de repeticiones por día para ambas personas
    bar_chart = alt.Chart(resultado_final).mark_bar().encode(
        x=alt.X('Dia:T', title='Día'),
        y=alt.Y('Suma_Repeticiones', title='Total de Repeticiones'),
        color=alt.Color('Persona:N', scale=alt.Scale(range=[colores['Carlos'], colores['Cinthia']]), title='Persona'),
        tooltip=['Persona', 'Dia', 'Suma_Repeticiones']
    ).properties(
        title="Total de Repeticiones por Día"
    )

    # Mostrar los gráficos en Streamlit
    st.altair_chart(line_chart, use_container_width=True)
    st.altair_chart(bar_chart, use_container_width=True)

# Función para crear un gráfico de cascada por grupo muscular
def crear_grafico_cascada(df_grupo, colores):
    # Agrupar datos por 'Dia' y 'Persona', sumando 'Peso_Total'
    df_cascada = df_grupo.groupby(['Dia', 'Persona'])['Peso_Total'].sum().reset_index()
    
    # Calcular la diferencia acumulada por persona
    df_cascada['Diferencia'] = df_cascada.groupby('Persona')['Peso_Total'].cumsum()
    
    # Crear un gráfico de cascada
    cascada_chart = alt.Chart(df_cascada).mark_bar().encode(
        x=alt.X('Dia:T', title='Día'),
        y=alt.Y('Diferencia:Q', title='Diferencia Acumulada'),
        color=alt.Color('Persona:N', scale=alt.Scale(range=[colores['Carlos'], colores['Cinthia']]), title='Persona'),
        tooltip=['Dia:T', 'Diferencia:Q', 'Persona']
    ).properties(
        title="Gráfico de Cascada por Grupo Muscular (Carlos y Cinthia)"
    )

    # Mostrar el gráfico en Streamlit
    st.altair_chart(cascada_chart, use_container_width=True)

# Título de la aplicación
st.title('🏋️‍♂️ Nuestro Progreso en el Gym 🏋️‍♀️')

# Registro de datos
with st.expander('📝 Registro de Datos'):
    Dia = st.text_input('Ingresa el Día 📆:')
    Persona = st.selectbox('Selecciona tu nombre 🤵‍♂️🙍:', ('Carlos', 'Cinthia'))
    Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', ('Press de pecho', 'Extensión de hombro', 'Extensión de tríceps en polea', 'Extensión lateral', 'Extensión frontal', 'Jalón polea alta prono', 'Jalón polea alta supino', 'Remo sentado con polea', 'Curl biceps', 'Curl martillo', 'Peso muerto', 'Leg Curl', 'Abducción', 'Glúteo en maquina', 'Leg press', 'Hack squat', 'Aducción', 'Leg extension', 'Hip thrust'))

    Enfoque = st.selectbox('Selecciona el enfoque de entrenamiento:', ('Desarrollo de Fuerza', 'Mejora de la Resistencia', 'Hipertrofia Muscular'))

    # Define Sets, pesos, repeticiones, y descansos basados en el enfoque
    Sets = st.number_input('Número de Sets:', min_value=1, max_value=10, step=1, value=4)
    unidad_peso = st.selectbox('Unidad de Peso:', ('kg', 'lb'))

    # Capturar datos según el enfoque de entrenamiento seleccionado
    if Enfoque == 'Desarrollo de Fuerza':
        pesos, repeticiones, descansos = formulario_desarrollo_fuerza(Sets)
    elif Enfoque == 'Mejora de la Resistencia':
        pesos, repeticiones, descansos = formulario_mejora_resistencia(Sets)
    else:
        pesos, repeticiones, descansos = formulario_hipertrofia_muscular(Sets)

    # Calcular peso ajustado
    pesos = calcular_peso_ajustado(pesos, Maquina, unidad_peso)

    # Verificar que los formularios estén completos
    form_completo = all(pesos) and all(repeticiones) and all(descansos)

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
                'Descanso': descansos
            })
            
            # Concatenar DataFrames y reiniciar el índice
            st.session_state['Progreso_ind'] = pd.concat([st.session_state['Progreso_ind'], Progreso_new], ignore_index=True)
            st.session_state['Progreso_ind'].to_csv('Progreso.csv', index=False)
            
            # Mostrar mensaje de éxito
            st.success('¡Datos registrados con éxito!')

# Visualización de datos registrados
with st.expander('📓 Datos Registrados'):
    st.subheader("Visualización de datos registrados")
    # Eliminar filas duplicadas basadas en las columnas específicas y actualizar los sets
    unique_values = st.session_state['Progreso_ind'].drop_duplicates(subset=['Dia', 'Persona', 'Maquina','Peso','Sets', 'Repeticiones','Descanso'])
    st.dataframe(unique_values.reset_index(drop=True))
    st.markdown(download_csv(unique_values, "Progreso"), unsafe_allow_html=True)

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

# Crear pestañas con los nombres proporcionados
tab1, tab2, tab3, tab4 = st.tabs(["Cuadriceps", "Espalda y Biceps", "Gluteos y femorales", "Pectorales, hombros y triceps"])

# Definir grupo muscular para cada máquina
unique_values['GM'] = unique_values['Maquina'].map({
    'Press de pecho': 'D', 'Extensión de hombro': 'D', 'Extensión de tríceps en polea': 'D',
    'Extensión lateral': 'D', 'Extensión frontal': 'D', 'Jalón polea alta prono': 'B',
    'Jalón polea alta supino': 'B', 'Remo sentado con polea': 'B', 'Curl biceps': 'B',
    'Curl martillo': 'B', 'Peso muerto': 'C', 'Leg Curl': 'C', 'Abducción': 'C',
    'Glúteo en maquina': 'C', 'Leg press': 'A', 'Hack squat': 'A', 'Aducción': 'A',
    'Leg extension': 'A', 'Hip thrust': 'C'
})

# Gráficos
if 'Progreso_ind' in st.session_state:       
    colores = {'Carlos': 'black', 'Cinthia': 'lightblue'}

    with tab1:
        st.header("Cuadriceps (A)")
        df_cuadriceps = unique_values[unique_values['GM'] == 'A']
        crear_grafico_cascada(df_cuadriceps, colores)

    with tab2:
        st.header("Espalda y Biceps (B)")
        df_espalda_biceps = unique_values[unique_values['GM'] == 'B']
        crear_grafico_cascada(df_espalda_biceps, colores)

    with tab3:
        st.header("Gluteos y femorales (C)")
        df_gluteos_femorales = unique_values[unique_values['GM'] == 'C']
        crear_grafico_cascada(df_gluteos_femorales, colores)

    with tab4:
        st.header("Pectorales, hombros y triceps (D)")
        df_pectoral_hombros_triceps = unique_values[unique_values['GM'] == 'D']
        crear_grafico_cascada(df_pectoral_hombros_triceps, colores)

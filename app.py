# Importar las librerías necesarias
import pandas as pd
import streamlit as st
from pathlib import Path
from base64 import b64encode
import altair as alt
import waterfall_chart

# Cargar los datos solo una vez
if 'Progreso_ind' not in st.session_state:
    if Path("Progreso.csv").exists():
        st.session_state['Progreso_ind'] = pd.read_csv("Progreso.csv")
    else:
        st.session_state['Progreso_ind'] = pd.DataFrame()

# Función para registrar datos de entrenamiento
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

# Función para calcular el peso ajustado basado en la máquina y la unidad de peso
def calcular_peso_ajustado(pesos, maquina, unidad_peso):
    # Convertir el peso de libras a kilogramos si es necesario
    if unidad_peso == 'lb':
        pesos = [peso * 0.453592 for peso in pesos]
    # Multiplicar el peso por 2 para ciertas máquinas
    maquinas_multiplicar_peso = ['Extensión lateral', 'Extensión frontal', 'Curl biceps', 'Curl martillo', 'Glúteo en maquina', 'Hack squat', 'Hip thrust', 'Leg press']
    if maquina in maquinas_multiplicar_peso:
        pesos = [peso * 2 for peso in pesos]
    return pesos

# Función para calcular el promedio ponderado de peso levantado
def calcular_promedio(df):
    df['Sets_x_Reps'] = df['Sets'] * df['Repeticiones']
    df['Peso_Total'] = df['Peso'] * df['Sets'] * df['Repeticiones']
    # Calcular la suma de repeticiones por persona y día
    df['Suma_Repeticiones'] = df.groupby(['Persona', 'Dia'])['Repeticiones'].transform('sum')
    # Agrupar por persona y día y calcular el promedio ponderado
    promedio_ponderado_por_persona = df.groupby(['Persona', 'Dia']).apply(
        lambda x: (x['Peso_Total'].sum() / x['Sets_x_Reps'].sum())
    ).reset_index(name='Promedio_Ponderado')
    # Combinar resultados con la suma de repeticiones
    resultado_final = df[['Persona', 'Dia', 'Suma_Repeticiones']].drop_duplicates().merge(
        promedio_ponderado_por_persona, on=['Persona', 'Dia'])
    return resultado_final

# Función para crear gráficos de cascada usando waterfall_chart
def crear_grafico_cascada(df_grupo, colores):
    # Calcular el promedio ponderado de peso levantado por día
    resultado_final = calcular_promedio(df_grupo)
    # Calcular las diferencias acumuladas de peso levantado para cada persona
    resultado_final['Diferencia_Acumulada'] = resultado_final.groupby('Persona')['Promedio_Ponderado'].cumsum()
    # Calcular diferencias por cada día para crear el gráfico de cascada
    diferencias = resultado_final.groupby('Persona')['Promedio_Ponderado'].apply(lambda x: x.diff().fillna(x))
    # Crear gráficos de cascada separados para Carlos y Cinthia usando waterfall_chart
    for persona in ['Carlos', 'Cinthia']:
        df_persona = resultado_final[resultado_final['Persona'] == persona]
        deltas = diferencias.loc[persona]
        dias = df_persona['Dia']
        st.subheader(f"Gráfico de Cascada para {persona}")
        waterfall_chart.plot(dias, deltas, title=f"Progreso de {persona}", xlabel='Días', ylabel='Cambio en Peso Levantado (kg)')

# Título de la aplicación
st.title('🏋️‍♂️ Nuestro Progreso en el Gym 🏋️‍♀️')

# Sección para registrar datos
with st.expander('📝 Registro de Datos'):
    Dia = st.text_input('Ingresa el Día 📆:')
    Persona = st.selectbox('Selecciona tu nombre 🤵‍♂️🙍:', ('Carlos', 'Cinthia'))
    Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', ('Press de pecho', 'Extensión de hombro', 'Extensión de tríceps en polea',
                                                        'Extensión lateral', 'Extensión frontal', 'Jalón polea alta prono',
                                                        'Jalón polea alta supino', 'Remo sentado con polea', 'Curl biceps',
                                                        'Curl martillo', 'Peso muerto', 'Leg Curl', 'Abducción',
                                                        'Glúteo en maquina', 'Leg press', 'Hack squat', 'Aducción', 'Leg extension', 'Hip thrust'))

    Enfoque = st.selectbox('Selecciona el enfoque de entrenamiento:', ('Desarrollo de Fuerza', 'Mejora de la Resistencia', 'Hipertrofia Muscular'))

    # Define Sets, pesos, repeticiones y descansos basados en el enfoque
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

# Sección de visualización de datos registrados
with st.expander('📓 Datos Registrados'):
    st.subheader("Visualización de datos registrados")
    # Eliminar filas duplicadas basadas en columnas específicas y actualizar los sets
    unique_values = st.session_state['Progreso_ind'].drop_duplicates(subset=['Dia', 'Persona', 'Maquina', 'Peso', 'Sets', 'Repeticiones', 'Descanso'])
    st.dataframe(unique_values)

# Sección de visualización de gráficos
if st.button('Generar gráficos de progreso'):
    # Ordenar datos por día para visualización
    df = st.session_state['Progreso_ind'].copy()
    df['Dia'] = pd.to_numeric(df['Dia'])
    df = df.sort_values('Dia')
    
    # Definir los colores de los gráficos para Carlos y Cinthia
    colores = {'Carlos': 'blue', 'Cinthia': 'red'}

    # Dividir los datos por grupo muscular
    tab1, tab2, tab3, tab4 = st.tabs(['Cuadriceps (A)', 'Espalda y Biceps (B)', 'Gluteos y femorales (C)', 'Pectorales, hombros y triceps (D)'])

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

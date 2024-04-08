# %%
# Importamos librerias
import pandas as pd
import streamlit as st
from pathlib import Path
from base64 import b64encode
import altair as alt

# %%
# Cargar el archivo Progreso.csv si existe
if 'Progreso_ind' not in st.session_state and Path("Progreso.csv").exists():
    gym_original = st.session_state['Progreso_ind'] = pd.read_csv("Progreso.csv")
else:
    gym_original = st.session_state['Progreso_ind'] = pd.DataFrame()


# %%
# Definiremos las funciones 
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
    df = df[['Dia', 'Persona', 'Maquina', 'Peso', 'Sets', 'Repeticiones', 'Descanso']]
    csv = df.to_csv(index=False, sep=',', encoding='utf-8').encode('utf-8')
    href = f'<a href="data:text/csv;base64,{b64encode(csv).decode()}" download="{filename}.csv">Descargar</a>'
    return href

# Función para calcular el promedio de peso por día y máquina
def calcular_promedio(df):    
    df['Peso_Total'] = df['Peso'] * df['Sets'] * df['Repeticiones']
    df['Sets_x_Reps'] = df['Sets'] * df['Repeticiones']    
    promedio_ponderado_por_dia = df.groupby(['Persona', 'Dia']).apply(
    lambda x: x['Peso_Total'].sum() / x['Sets_x_Reps'].sum()
    )
    return promedio_ponderado_por_dia

# %%
# Función para crear gráficos de líneas y barras
def crear_graficos(df_grupo, colores):
    # Reiniciar el índice para evitar problemas con Altair
    df_grupo = df_grupo.reset_index(drop=True)
    
    # Verificar si hay suficientes datos para crear gráficos
    if len(df_grupo) == 0:
        st.warning("No hay suficientes datos disponibles para mostrar los gráficos.")
        return
    
    # Calcular el promedio de peso por día y máquina
    df_grupo = calcular_promedio(df_grupo).reset_index()
    
    # Calcular el orden de los días dentro de cada grupo muscular usando rank
    df_grupo['Dia_ordenado'] = df_grupo.groupby('Dia').cumcount() + 1
    
    # Gráfico de líneas del promedio de peso levantado por día para ambas personas
    line_chart = alt.Chart(df_grupo).mark_line().encode(
        x='Dia_ordenado:O',  # Utiliza el tipo de dato 'ordinal' para el eje X
        y=alt.Y('promedio_peso:Q', title='Promedio de Peso'),  # Utiliza el promedio de peso para el eje Y
        color=alt.Color('Persona:N', scale=alt.Scale(domain=['Carlos', 'Cinthia'], range=['black', 'lightblue']), title='Persona'),  # Diferenciar las líneas por persona
        tooltip=['Persona', 'Dia', 'promedio_peso']  # Utiliza el promedio de peso para la etiqueta del tooltip
    ).properties(
        title="Promedio de Peso Levantado"
    )
    st.altair_chart(line_chart, use_container_width=True)

# %%
# Título de la aplicación
st.title('🏋️‍♂️ Nuestro Progreso en el Gym 🏋️‍♀️')

# %%
# Formulario desplegable y botón de guardar
with st.expander('📝 Registro de Datos'):
    Dia = st.text_input('Ingresa el Día 📆:')
    Persona = st.selectbox('Selecciona tu nombre 🤵‍♂️🙍:', ('Carlos', 'Cinthia'))
    Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', ('Press de pecho','Extensión de hombro','Extensión de tríceps en polea','Extensión lateral'
                                                            ,'Extensión frontal','Jalón polea alta prono','Jalón polea alta supino','Remo sentado con polea'
                                                            ,'Curl biceps','Curl martillo','Peso muerto','Leg Curl','Abducción','Glúteo en maquina','Leg press'
                                                            ,'Hack squat','Aducción','Leg extension','Hip thrust'))
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
        if st.button('Guardar'):
            Progreso_new = pd.DataFrame({
                'Dia': [Dia] * Sets,
                'Persona': [Persona] * Sets,
                'Maquina': [Maquina] * Sets,
                'Sets' : Sets,
                'Peso': pesos,
                'Repeticiones': repeticiones,
                'Descanso': descansos
            })
            gym_original = pd.concat([gym_original, Progreso_new], ignore_index=True)
            # Guardar el DataFrame actualizado en un archivo CSV
            # Utiliza transform para agregar la columna de conteo directamente al DataFrame existente
            if Enfoque != 'Hipertrofia Muscular':
                gym_original['Sets'] = gym_original.groupby(['Dia', 'Persona', 'Maquina', 'Peso','Descanso','Repeticiones'])[['Peso', 'Repeticiones']].transform('size')
            st.success('¡Datos registrados con éxito!')
            st.session_state['show_enfoque_form'] = False 
            st.session_state['Progreso_ind'].to_csv('Progreso.csv', index=False)

# %%
# Datos generales registrados
with st.expander('📓 Datos Registrados'):
    st.subheader("Visualización de datos registrados")
    # Eliminar filas duplicadas basadas en las columnas específicas y actualizar los sets
    unique_values = gym_original.drop_duplicates(subset=['Dia', 'Persona', 'Maquina','Peso','Sets', 'Repeticiones','Descanso'])
    st.dataframe(unique_values.reset_index(drop=True))
    df= unique_values


# %%
# Gráficos
if 'Progreso_ind' in st.session_state:       
    colores = {'Carlos': 'black', 'Cinthia': 'lightblue'}
    # Suponiendo que 'st.session_state['Progreso_ind']' ya contiene el DataFrame con los datos necesarios

    df = df.sort_values(by='Dia')
    
    
    with tab1:
        st.header("Cuadriceps (A)")
        df_cuadriceps = df[df['GM'] == 'A']
        df_cuadriceps = df_cuadriceps.reset_index(drop=True)  # Resetear el índice para evitar problemas con Altair
        crear_graficos(df_cuadriceps, colores)

    with tab2:
        st.header("Espalda y Biceps (B)")
        df_espalda_biceps = df[df['GM'] == 'B']
        df_espalda_biceps = df_espalda_biceps.reset_index(drop=True)  # Resetear el índice para evitar problemas con Altair
        crear_graficos(df_espalda_biceps, colores)

    with tab3:
        st.header("Gluteos y femorales (C)")
        df_gluteos_femorales = df[df['GM'] == 'C']
        df_gluteos_femorales = df_gluteos_femorales.reset_index(drop=True)  # Resetear el índice para evitar problemas con Altair
        crear_graficos(df_gluteos_femorales, colores)

    with tab4:
        st.header("Pectorales, hombros y triceps (D)")
        df_pectoral_hombros_triceps = df[df['GM'] == 'D']
        df_pectoral_hombros_triceps = df_pectoral_hombros_triceps.reset_index(drop=True)  # Resetear el índice para evitar problemas con Altair
        crear_graficos(df_pectoral_hombros_triceps, colores)



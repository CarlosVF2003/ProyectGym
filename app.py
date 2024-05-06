# Importamos librerias
import pandas as pd
import streamlit as st
from pathlib import Path
from base64 import b64encode
import altair as alt

# Cargar los dataframes desde los archivos CSV
df_progreso = pd.read_csv("Progreso.csv")
df_usuarios = pd.read_csv("Usuarios.csv")

# Unir el dataframe de progreso con el dataframe de usuarios utilizando 'Id_Usuario' como clave de unión
df_merged = pd.merge(df_progreso, df_usuarios, on='Id_Usuario', how='left')

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
    df = df[['Dia', 'Nombre', 'Maquina', 'Peso', 'Sets', 'Repeticiones', 'Medida']]
    csv = df.to_csv(index=False, sep=',', encoding='utf-8').encode('utf-8')
    href = f'<a href="data:text/csv;base64,{b64encode(csv).decode()}" download="{filename}.csv">Descargar</a>'
    return href

# Función para calcular el promedio de peso por día y máquina
def calcular_promedio(df):    
    df['Sets_x_Reps'] = df['Sets'] * df['Repeticiones']
    df['Peso_Total'] = df['Peso'] * df['Sets'] * df['Repeticiones']
    
    # Calcula la suma de repeticiones por persona y día
    df['Suma_Repeticiones'] = df.groupby(['Nombre', 'Dia'])['Repeticiones'].transform('sum')
        
    # Agrupa por persona y día, y calcula el promedio ponderado
    promedio_ponderado_por_persona = df.groupby(['Nombre', 'Dia']).apply(
    lambda x: (x['Peso_Total'].sum() / x['Sets_x_Reps'].sum())
    ).reset_index(name='Promedio_Ponderado')
        
    # Une los resultados con la suma de repeticiones
    resultado_final = df[['Nombre', 'Dia', 'Suma_Repeticiones']].drop_duplicates().merge(
    promedio_ponderado_por_persona, on=['Nombre', 'Dia'])
    return resultado_final

# Función para crear gráficos de líneas y barras
def crear_graficos(df_grupo, colores):
    # Reiniciar el índice para evitar problemas con Altair
    df_grupo = df_grupo.reset_index(drop=True)
    
    # Verificar si hay suficientes datos para crear gráficos
    if len(df_grupo) == 0:
        st.warning("No hay suficientes datos disponibles para mostrar los gráficos.")
        return
    
    # Calcular el promedio de peso por día y máquina
    resultado_final = calcular_promedio(df_grupo)
    
    # Calcular el orden de los días dentro de cada grupo muscular usando rank
    resultado_final['Dia_ordenado'] = resultado_final.groupby('Dia').cumcount() + 1
    
    # Gráfico de líneas del promedio de peso levantado por día para ambas personas
    line_chart = alt.Chart(resultado_final).mark_line().encode(
        x='Dia_ordenado:T',  # Utiliza el tipo de dato 'temporal' para el eje X
        y=alt.Y('Promedio_Ponderado', title='Promedio de Peso'),  # Utiliza el promedio de peso para el eje Y
        color=alt.Color('Nombre:N', scale=alt.Scale(domain=['Carlos', 'Cinthia'], range=['black', 'lightblue']), title='Nombre'),  # Diferenciar las líneas por persona
        tooltip=['Nombre', 'Dia', 'Promedio_Ponderado']  # Utiliza el promedio de peso para la etiqueta del tooltip
    ).properties(
        title="Promedio de Peso Levantado"
    )
    st.altair_chart(line_chart, use_container_width=True)

    # Gráfico de barras del total de repeticiones por día para ambas personas
    bar_chart = alt.Chart(resultado_final).mark_bar().encode(
        x='Dia_ordenado:T',  # Utiliza el tipo de dato 'temporal' para el eje X
        y=alt.Y('Suma_Repeticiones', title='Total de Repeticiones'),
        color=alt.Color('Nombre:N', scale=alt.Scale(domain=['Carlos', 'Cinthia'], range=['black', 'lightblue']), title='Nombre'),  # Diferenciar las barras por persona
        tooltip=['Nombre', 'Dia', 'Suma_Repeticiones']
    ).properties(
        title="Total de Repeticiones"
    )
    st.altair_chart(bar_chart, use_container_width=True)

# Título de la aplicación
st.title('🏋️‍♂️ Nuestro Progreso en el Gym 🏋️‍♀️')

# Formulario desplegable y botón de guardar
with st.expander('📝 Registro de Datos'):
    Dia = st.text_input('Ingresa el Día 📆:')
    usuario = st.selectbox('Selecciona tu nombre 🤵‍♂️🙍:', df_merged['Nombre'].unique())
    Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', df_merged['Maquina'].unique())
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
                'Nombre': [usuario] * Sets,
                'Maquina': [Maquina] * Sets,
                'Sets' : Sets,
                'Peso': pesos,
                'Repeticiones': repeticiones,
                'Medida': [descansos[0]] * Sets
            })
            df_progreso = pd.concat([df_progreso, Progreso_new], ignore_index=True)
            # Guardar el DataFrame actualizado en un archivo CSV
            # Utiliza transform para agregar la columna de conteo directamente al DataFrame existente
            if Enfoque != 'Hipertrofia Muscular':
                df_progreso['Sets'] = df_progreso.groupby(['Dia', 'Nombre', 'Maquina', 'Peso','Medida','Repeticiones'])[['Peso', 'Repeticiones']].transform('size')
            st.success('¡Datos registrados con éxito!')
            df_progreso.to_csv('Progreso.csv', index=False)

# Datos generales registrados
with st.expander('📓 Datos Registrados'):
    st.subheader("Visualización de datos registrados")
    # Eliminar filas duplicadas basadas en las columnas específicas y actualizar los sets
    unique_values = df_progreso.drop_duplicates(subset=['Dia', 'Nombre', 'Maquina','Peso','Sets', 'Repeticiones','Medida'])
    st.dataframe(unique_values.reset_index(drop=True))
    df= unique_values

# Mostrar tablas de datos de cada usuario
for usuario in df['Nombre'].unique():
    with st.expander(f'🤵‍♂️ Tabla de datos de {usuario}'):
        st.header(f'Datos de {usuario}')
        df_usuario = df[df['Nombre'] == usuario]
        st.dataframe(df_usuario.reset_index(drop=True))

# Crear pestañas con los nombres proporcionados
tab1, tab2, tab3, tab4 = st.tabs(["Cuadriceps", "Espalda y Biceps", "Gluteos y femorales", "Pectorales, hombros y triceps"])

# Gráficos
if 'Progreso_ind' in st.session_state:       
    colores = {'Carlos': 'black', 'Cinthia': 'lightblue'}
    # Suponiendo que 'st.session_state['Progreso_ind']' ya contiene el DataFrame con los datos necesarios

    df = df.sort_values(by='Dia')
    
    with tab1:
        st.header("Cuadriceps (A)")
        df_cuadriceps = df[df['Maquina'].isin(['Leg press', 'Hack squat', 'Aducción', 'Leg extension'])]
        df_cuadriceps = df_cuadriceps.reset_index(drop=True)  # Resetear el índice para evitar problemas con Altair
        crear_graficos(df_cuadriceps, colores)

    with tab2:
        st.header("Espalda y Biceps (B)")
        df_espalda_biceps = df[df['Maquina'].isin(['Jalón polea alta prono','Jalón polea alta supino','Remo sentado con polea','Curl biceps','Curl martillo'])]
        df_espalda_biceps = df_espalda_biceps.reset_index(drop=True)  # Resetear el índice para evitar problemas con Altair
        crear_graficos(df_espalda_biceps, colores)

    with tab3:
        st.header("Gluteos y femorales (C)")
        df_gluteos_femorales = df[df['Maquina'].isin(['Peso muerto', 'Leg Curl','Hip thrust', 'Abducción', 'Glúteo en maquina'])]
        df_gluteos_femorales = df_gluteos_femorales.reset_index(drop=True)  # Resetear el índice para evitar problemas con Altair
        crear_graficos(df_gluteos_femorales, colores)

    with tab4:
        st.header("Pectorales, hombros y triceps (D)")
        df_pectoral_hombros_triceps = df[df['Maquina'].isin(['Press de pecho', 'Extensión de hombro', 'Extensión de tríceps en polea', 'Extensión lateral', 'Extensión frontal'])]
        df_pectoral_hombros_triceps = df_pectoral_hombros_triceps.reset_index(drop=True)  # Resetear el índice para evitar problemas con Altair
        crear_graficos(df_pectoral_hombros_triceps, colores)

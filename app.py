# %%
# Importamos librerias
import pandas as pd
import streamlit as st
from pathlib import Path
from base64 import b64encode
import altair as alt


# %%
# Cargar los archivos CSV si existen
df_usuarios = pd.read_csv("Usuarios.csv")
df_grupo_muscular = pd.read_csv("Grupo_muscular.csv")
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
    resultado_final = calcular_promedio(df_grupo)
    
    # Calcular el orden de los días dentro de cada grupo muscular usando rank
    resultado_final['Dia_ordenado'] = resultado_final.groupby('Dia').cumcount() + 1
    
    # Gráfico de líneas del promedio de peso levantado por día para ambas personas
    line_chart = alt.Chart(resultado_final).mark_line().encode(
        x='Dia_ordenado:T',  # Utiliza el tipo de dato 'temporal' para el eje X
        y=alt.Y('Promedio_Ponderado', title='Promedio de Peso'),  # Utiliza el promedio de peso para el eje Y
        color=alt.Color('Nombre:N', scale=alt.Scale(domain=df_usuarios['Nombre'].tolist(), range=df_usuarios['Color'].tolist()), title='Persona'),  # Diferenciar las líneas por persona
        tooltip=['Nombre', 'Dia', 'Promedio_Ponderado']  # Utiliza el promedio de peso para la etiqueta del tooltip
    ).properties(
        title="Promedio de Peso Levantado"
    )
    st.altair_chart(line_chart, use_container_width=True)

    # Gráfico de barras del total de repeticiones por día para ambas personas
    bar_chart = alt.Chart(resultado_final).mark_bar().encode(
        x='Dia_ordenado:T',  # Utiliza el tipo de dato 'temporal' para el eje X
        y=alt.Y('Suma_Repeticiones', title='Total de Repeticiones'),
        color=alt.Color('Nombre:N', scale=alt.Scale(domain=df_usuarios['Nombre'].tolist(), range=df_usuarios['Color'].tolist()), title='Persona'),  # Diferenciar las barras por persona
        tooltip=['Nombre', 'Dia', 'Suma_Repeticiones']
    ).properties(
        title="Total de Repeticiones"
    )
    st.altair_chart(bar_chart, use_container_width=True)

# %%
# Título de la aplicación
st.title('🏋️‍♂️ Nuestro Progreso en el Gym 🏋️‍♀️')

# %%
# Formulario desplegable y botón de guardar
with st.expander('📝 Registro de Datos'):
    Dia = st.text_input('Ingresa el Día 📆:')
    Nombre_usuario = st.selectbox('Selecciona tu nombre 🤵‍♂️🙍:', df_usuarios['Nombre'].tolist())
    Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', df_grupo_muscular['Maquina'].tolist())
    Sets = st.number_input('Número de Sets:', min_value=1, max_value=10, step=1, value=4)
    Peso = st.number_input('Peso (kg):', min_value=0.0, step=0.1, format="%.1f")
    Repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    Medida = st.text_input('Medida:', value='kg')

    # Guardar los datos
    if st.button('Guardar'):
        Progreso_new = pd.DataFrame({
            'Dia': [Dia] * Sets,
            'Nombre': [Nombre_usuario] * Sets,
            'Maquina': [Maquina] * Sets,
            'Peso': [Peso] * Sets,
            'Sets': [Sets] * Sets,
            'Repeticiones': [Repeticiones] * Sets,
            'Medida': [Medida] * Sets
        })
        gym_original = pd.concat([gym_original, Progreso_new], ignore_index=True)
        st.success('¡Datos registrados con éxito!')
        st.session_state['Progreso_ind'].to_csv('Progreso.csv', index=False)

# %%
# Datos generales registrados
with st.expander('📓 Datos Registrados'):
    st.subheader("Visualización de datos registrados")
    st.dataframe(gym_original.reset_index(drop=True))

# %%
# Mostrar tablas de datos de cada usuario
for usuario in df_usuarios['Nombre']:
    with st.expander(f'🤵‍♂️ Tabla de datos de {usuario}'):
        st.header(f'Datos de {usuario}')
        df_usuario = gym_original[gym_original['Nombre'] == usuario]
        st.dataframe(df_usuario.reset_index(drop=True))

# %%
# Crear pestañas con los grupos musculares
tab_dict = {}
for grupo in df_grupo_muscular['Grupo_Muscular'].unique():
    df_grupo_muscular_filtrado = df_grupo_muscular[df_grupo_muscular['Grupo_Muscular'] == grupo]
    tab_dict[grupo] = st.tab_item(label=grupo)
    df_maquinas = df_grupo_muscular_filtrado[['Maquina']]
    df_maquinas['GM'] = grupo[0]
    df_maquinas.columns = ['Maquina', 'GM']
    df = pd.merge(df, df_maquinas, on='Maquina', how='left')
    
    df.loc[df['GM'].isnull(), 'GM'] = grupo[0]

# %%
# Gráficos
if 'Progreso_ind' in st.session_state:       
    colores = {'Carlos': 'black', 'Cinthia': 'lightblue'}
    df = df.sort_values(by='Dia')
    
    for grupo, tab in tab_dict.items():
        with tab:
            st.header(f"{grupo} ({grupo[0]})")
            df_grupo = df[df['GM'] == grupo[0]]
            df_grupo = df_grupo.reset_index(drop=True)  # Resetear el índice para evitar problemas con Altair
            crear_graficos(df_grupo, colores)

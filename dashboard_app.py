# librerias principales del dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# configuración de la página: título, ícono y layout ancho
st.set_page_config(
    page_title="NexaPlay Analytics",
    page_icon="🎮",
    layout="wide"
)

# ── LOGIN ─────────────────────────────────────────────────────────────────────
# credenciales hardcodeadas para demo en clase
USUARIO_VALIDO = "admin"
CLAVE_VALIDA   = "12345"

# st.session_state: diccionario persistente entre reruns de Streamlit
# permite recordar si el usuario ya se autenticó en esta sesión
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# si no está autenticado, mostrar formulario y detener ejecución
if not st.session_state["autenticado"]:
    st.title("NexaPlay Analytics")
    st.subheader("Iniciar sesión")

    # text_input con type="password" oculta el texto mientras se escribe
    usuario_input = st.text_input("Usuario")
    clave_input   = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if usuario_input == USUARIO_VALIDO and clave_input == CLAVE_VALIDA:
            st.session_state["autenticado"] = True
            # st.rerun: vuelve a ejecutar el script desde el inicio con el nuevo estado
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

    # st.stop: detiene la ejecución del script en este punto
    # todo lo que viene después no se ejecuta si el usuario no está autenticado
    st.stop()

# ── CARGA DE DATOS ────────────────────────────────────────────────────────────
# construir ruta absoluta al CSV, independiente del directorio desde donde se corra
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "games_clean.csv")

# @st.cache_data: decorador que guarda el resultado en caché
# la función solo corre una vez; en reruns devuelve el resultado guardado
@st.cache_data
def cargar_datos(path):
    # pd.read_csv: lee el archivo CSV y lo convierte en DataFrame
    videojuegos = pd.read_csv(path)
    return videojuegos

# variable principal del dataset completo (sin filtros aún)
videojuegos = cargar_datos(DATA_PATH)

# ── ENCABEZADO ────────────────────────────────────────────────────────────────
st.title("NexaPlay Analytics Dashboard")

# st.markdown: renderiza texto con formato Markdown (negrita, cursiva, encabezados, etc.)
st.markdown("Estrategia de mercado basada en datos históricos de la industria del videojuego.")

# st.divider: dibuja una línea horizontal de separación visual entre secciones
st.divider()

# ── SIDEBAR: FILTROS ──────────────────────────────────────────────────────────
st.sidebar.header("Filtros")

# extraer el año mínimo y máximo del dataset para los extremos del slider
anio_min = int(videojuegos['year_of_release'].min())
anio_max = int(videojuegos['year_of_release'].max())

# st.sidebar.slider: widget deslizante en el panel lateral
# min_value / max_value: límites del rango posible en el slider
# value: tupla con el rango seleccionado por defecto al cargar la app
rango_anios = st.sidebar.slider(
    "Rango de años",
    min_value=anio_min,
    max_value=anio_max,
    value=(2000, anio_max)
)

# lista de plataformas disponibles sin nulos, ordenadas alfabéticamente
plataformas_disponibles = sorted(videojuegos['platform'].dropna().unique())

# st.sidebar.multiselect: selector múltiple en el panel lateral
# default: valores preseleccionados al cargar (aquí todas las plataformas)
plataformas_seleccionadas = st.sidebar.multiselect(
    "Plataforma",
    options=plataformas_disponibles,
    default=plataformas_disponibles
)

# diccionario que mapea la etiqueta visible del selectbox al nombre real de columna en el CSV
region_opciones = {
    'Total global': 'total_sales',
    'Norteamérica': 'na_sales',
    'Europa':       'eu_sales',
    'Japón':        'jp_sales'
}

# st.sidebar.selectbox: menú desplegable de selección única
region_seleccionada = st.sidebar.selectbox(
    "Región (Guerra de Géneros)",
    options=list(region_opciones.keys())
)

# obtener el nombre de columna correspondiente a la región elegida
columna_region = region_opciones[region_seleccionada]

# aplicar los tres filtros al dataset y guardar el resultado en videojuegos_filtrado
videojuegos_filtrado = videojuegos[
    (videojuegos['year_of_release'] >= rango_anios[0]) &
    (videojuegos['year_of_release'] <= rango_anios[1]) &
    (videojuegos['platform'].isin(plataformas_seleccionadas))
]

# ── KPIs GLOBALES (se recalculan con cada cambio en los filtros) ──────────────
# st.columns(4): divide el ancho disponible en 4 columnas iguales
col1, col2, col3, col4 = st.columns(4)

with col1:
    # nunique: cuenta valores únicos; evita duplicar juegos que salieron en múltiples plataformas
    st.metric("Títulos únicos", f"{videojuegos_filtrado['videogame_names'].nunique():,}")

with col2:
    # sum sobre total_sales del dataset filtrado
    st.metric("Ventas globales (M)", f"{videojuegos_filtrado['total_sales'].sum():.1f}")

with col3:
    st.metric("Géneros únicos", videojuegos_filtrado['genre'].nunique())

with col4:
    # idxmax: devuelve el índice (año) con el valor de suma más alto
    anio_pico = videojuegos_filtrado.groupby('year_of_release')['total_sales'].sum().idxmax()
    st.metric("Año pico de la industria", int(anio_pico))

st.divider()

# ── PESTAÑAS PRINCIPALES ──────────────────────────────────────────────────────
# st.tabs: crea pestañas navegables; la lista define los nombres en orden
tab1, tab2, tab3, tab4 = st.tabs([
    "Guerra de Géneros",
    "Calidad vs. Ventas",
    "Estrategia Geográfica",
    "Pronóstico"
])

# =============================================================================
# PESTAÑA 1: GUERRA DE GÉNEROS
# =============================================================================
with tab1:
    st.header("Guerra de Géneros")
    st.caption("¿Qué géneros crecen y cuáles están en declive?")

    # calcular top 3 sobre el dataset ya filtrado por el sidebar
    top3_generos = (
        videojuegos_filtrado.groupby('genre')[columna_region].sum()
        .nlargest(3).index.tolist()
    )

    # multiselect con top 3 preseleccionados; el usuario puede agregar o quitar géneros
    generos_grafico = st.multiselect(
        "Géneros a mostrar",
        options=sorted(videojuegos_filtrado['genre'].unique()),
        default=top3_generos,
        key="selector_guerra"
    )

    # recalcular el top 3 activo solo sobre los géneros actualmente seleccionados
    # si el usuario quita uno del top 3, el siguiente en ventas sube y toma su color
    if generos_grafico:
        top3_activo = (
            videojuegos_filtrado[videojuegos_filtrado['genre'].isin(generos_grafico)]
            .groupby('genre')[columna_region].sum()
            .nlargest(3).index.tolist()
        )
    else:
        top3_activo = []

    # agrupar ventas por año y género para los géneros actualmente seleccionados
    ventas_por_anio_genero = (
        videojuegos_filtrado[videojuegos_filtrado['genre'].isin(generos_grafico)]
        .groupby(['year_of_release', 'genre'])[columna_region]
        .sum().reset_index()
    )

    # paleta de 3 colores fijos para los géneros destacados; el resto va en gris semitransparente
    COLORES_TOP3 = ['#FF6B35', '#00B4D8', '#06D6A0']
    color_map = {}
    for i, genero in enumerate(top3_activo):
        color_map[genero] = COLORES_TOP3[i]
    for genero in generos_grafico:
        if genero not in top3_activo:
            color_map[genero] = 'rgba(180, 180, 180, 0.35)'

    # px.line: gráfico de líneas de Plotly Express
    # color: columna que genera una línea por cada valor único
    # color_discrete_map: asigna colores específicos por categoría en lugar de la paleta automática
    # labels: renombra los ejes y leyenda que aparecen en el gráfico
    fig_lineas = px.line(
        ventas_por_anio_genero,
        x='year_of_release',
        y=columna_region,
        color='genre',
        color_discrete_map=color_map,
        title='Ventas por género a lo largo del tiempo',
        labels={
            'year_of_release': 'Año',
            columna_region:    f'Ventas {region_seleccionada} (M)',
            'genre':           'Género'
        }
    )

    # ajustar grosor de línea: más gruesas para el top 3 activo, más delgadas para el resto
    for trace in fig_lineas.data:
        trace.update(line=dict(width=3 if trace.name in top3_activo else 1))

    # agregar anotación en el punto de pico de cada uno de los 3 géneros destacados
    # ax/ay: desplazamiento en píxeles del bloque de texto respecto al punto señalado
    OFFSETS = [(-60, -50), (70, -40), (0, -65)]
    for i, genero in enumerate(top3_activo):
        if genero not in generos_grafico:
            continue
        df_gen = ventas_por_anio_genero[ventas_por_anio_genero['genre'] == genero]
        if df_gen.empty:
            continue
        fila_pico = df_gen.loc[df_gen[columna_region].idxmax()]
        fig_lineas.add_annotation(
            x=fila_pico['year_of_release'],
            y=fila_pico[columna_region],
            text=f'<b>{genero}</b><br>{int(fila_pico["year_of_release"])}: {fila_pico[columna_region]:.1f}M',
            showarrow=True, arrowhead=2, arrowwidth=2,
            arrowcolor=COLORES_TOP3[i],
            font=dict(color=COLORES_TOP3[i], size=11),
            bgcolor='rgba(0,0,0,0.6)',
            bordercolor=COLORES_TOP3[i],
            ax=OFFSETS[i][0], ay=OFFSETS[i][1]
        )

    # use_container_width: expande el gráfico al ancho total del contenedor de la pestaña
    st.plotly_chart(fig_lineas, use_container_width=True)

# =============================================================================
# PESTAÑA 2: CALIDAD VS VENTAS
# =============================================================================
with tab2:
    st.header("Calidad vs. Ventas")
    st.caption("¿La crítica especializada predice el éxito comercial mejor que los usuarios?")

    # slider para controlar el percentil de corte de outliers de ventas
    percentil = st.slider(
        "Excluir outliers: mostrar hasta el percentil",
        min_value=80, max_value=100, value=95, step=1,
        # help: texto de ayuda que aparece al pasar el cursor sobre el widget
        help="100 muestra todos los juegos. 95 excluye el 5% con más ventas."
    )

    # quantile: calcula el valor de ventas en el percentil indicado (escala 0.0 a 1.0)
    techo_ventas = videojuegos_filtrado['total_sales'].quantile(percentil / 100)
    df_scores = videojuegos_filtrado[videojuegos_filtrado['total_sales'] <= techo_ventas].copy()

    # dos columnas para mostrar los scatter plots en paralelo
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        # px.scatter: gráfico de dispersión; cada punto representa un juego
        # hover_name: campo que aparece como título en el tooltip al pasar el cursor
        # hover_data: campos adicionales en el tooltip; False oculta el eje ya visible en el gráfico
        # opacity: transparencia de los puntos (0.0 invisible, 1.0 sólido)
        fig_criticos = px.scatter(
            df_scores,
            x='critic_score',
            y='total_sales',
            hover_name='videogame_names',
            hover_data={
                'total_sales':  ':.2f',
                'critic_score': False,
                'user_score':   True,
                'genre':        True
            },
            title='Critic Score vs Ventas globales',
            opacity=0.5,
            labels={
                'critic_score': 'Puntuación de críticos',
                'total_sales':  'Ventas globales (M)',
                'user_score':   'User Score',
                'genre':        'Género'
            }
        )
        st.plotly_chart(fig_criticos, use_container_width=True)

    with col_s2:
        fig_usuarios = px.scatter(
            df_scores,
            x='user_score',
            y='total_sales',
            hover_name='videogame_names',
            hover_data={
                'total_sales':  ':.2f',
                'user_score':   False,
                'critic_score': True,
                'genre':        True
            },
            title='User Score vs Ventas globales',
            opacity=0.5,
            labels={
                'user_score':   'Puntuación de usuarios',
                'total_sales':  'Ventas globales (M)',
                'critic_score': 'Critic Score',
                'genre':        'Género'
            }
        )
        st.plotly_chart(fig_usuarios, use_container_width=True)

    st.markdown("**Top 10 juegos en el rango visible**")

    top10 = (
        df_scores[['videogame_names', 'genre', 'platform', 'total_sales', 'critic_score', 'user_score']]
        .sort_values('total_sales', ascending=False)
        .head(10)
        .rename(columns={
            'videogame_names': 'Juego',
            'genre':           'Género',
            'platform':        'Plataforma',
            'total_sales':     'Ventas (M)',
            'critic_score':    'Critic Score',
            'user_score':      'User Score'
        })
        .reset_index(drop=True)
    )

    # sumar 1 al índice para que la numeración empiece en 1 y no en 0
    top10.index = top10.index + 1

    # style.format: aplica formato de visualización a columnas específicas
    # no modifica los datos, solo el texto que se muestra en pantalla
    st.dataframe(
        top10.style.format({"Ventas (M)": "${:.2f}"}),
        use_container_width=True
    )

# =============================================================================
# PESTAÑA 3: ESTRATEGIA GEOGRÁFICA
# =============================================================================
with tab3:
    st.header("Estrategia Geográfica")
    st.caption("¿Occidente y Japón consumen los mismos géneros?")

    # st.checkbox: interruptor booleano; devuelve True cuando está marcado
    vista_proporcional = st.checkbox("Ver como porcentaje del total por género")

    # agrupar ventas por región para cada género
    ventas_regionales = (
        videojuegos_filtrado.groupby('genre')[['na_sales', 'eu_sales', 'jp_sales']]
        .sum().reset_index()
        .rename(columns={
            'na_sales': 'Norteamérica',
            'eu_sales': 'Europa',
            'jp_sales': 'Japón'
        })
    )

    # columna auxiliar con el total de las tres regiones por género
    ventas_regionales['_total'] = ventas_regionales[['Norteamérica', 'Europa', 'Japón']].sum(axis=1)

    # ordenar por ventas en Norteamérica y conservar solo el top 10
    ventas_regionales = ventas_regionales.sort_values('Norteamérica', ascending=False).head(10)

    if vista_proporcional:
        # convertir valores absolutos a porcentaje sobre el total del género
        for col in ['Norteamérica', 'Europa', 'Japón']:
            ventas_regionales[col] = (ventas_regionales[col] / ventas_regionales['_total'] * 100).round(1)
        etiqueta_y, modo_barras = 'Proporción del total (%)', 'stack'
    else:
        etiqueta_y, modo_barras = 'Ventas (M)', 'group'

    # px.bar: gráfico de barras; y acepta lista de columnas para barras múltiples por grupo
    # barmode 'group': barras lado a lado; 'stack': barras apiladas sobre el mismo eje
    # color_discrete_map: asigna un color fijo a cada región
    fig_barras = px.bar(
        ventas_regionales,
        x='genre',
        y=['Norteamérica', 'Europa', 'Japón'],
        title='Top 10 géneros por región',
        barmode=modo_barras,
        labels={'genre': 'Género', 'value': etiqueta_y, 'variable': 'Región'},
        color_discrete_map={
            'Norteamérica': '#00B4D8',
            'Europa':       '#0077B6',
            'Japón':        '#FF6B35'
        }
    )

    # solo agregar anotación cuando no está en vista proporcional
    if not vista_proporcional:
        # calcular ratio Japón / Occidente para encontrar el género donde Japón es más competitivo
        ventas_regionales['_occidente'] = ventas_regionales['Norteamérica'] + ventas_regionales['Europa']
        ventas_regionales['_ratio_jp']  = (
            ventas_regionales['Japón'] /
            ventas_regionales['_occidente'].replace(0, float('nan'))
        )

        # idxmax: devuelve la etiqueta del índice con el valor más alto de la columna
        idx_mejor_jp = ventas_regionales['_ratio_jp'].idxmax()

        if pd.notna(idx_mejor_jp):
            fila_mejor = ventas_regionales.loc[idx_mejor_jp]
            genero_jp  = fila_mejor['genre']
            jp_val     = fila_mejor['Japón']

            # ay dinámico: si la barra es alta el texto se desplaza más arriba
            # evita que la etiqueta tape la barra o quede fuera del área visible del gráfico
            max_ventas  = ventas_regionales['Japón'].max()
            ay_dinamico = -30 - int((jp_val / max_ventas) * 50)

            fig_barras.add_annotation(
                x=genero_jp,
                y=jp_val,
                text=f'Japón más competitivo aquí<br>({genero_jp}: {jp_val:.1f}M)',
                showarrow=True, arrowhead=2, arrowcolor='#FF6B35',
                font=dict(color='#FF6B35', size=11),
                bgcolor='rgba(0,0,0,0.6)',
                bordercolor='#FF6B35',
                ax=90, ay=ay_dinamico
            )

    st.plotly_chart(fig_barras, use_container_width=True)

# =============================================================================
# PESTAÑA 4: PRONÓSTICO (en construcción)
# =============================================================================
with tab4:
    st.header("Pronóstico")
    st.caption("Predicción de ventas basada en modelos de machine learning.")

    # st.info: cuadro informativo en azul, sin nivel de alerta
    st.info("Esta sección está en construcción. Se habilitará en una próxima sesión.")

# NexaPlay Analytics — Seminario UniAndes 2026

Producto analítico completo construido en el Seminario de Analítica con Python (UniAndes, 2026). El caso de negocio: NexaPlay Studios enfrenta su primer lanzamiento con $50M en juego y cero datos propios. La junta directiva está fracturada por opiniones sin evidencia empírica. Este proyecto convierte datos históricos de la industria del videojuego en software interactivo para tomar decisiones.

---

## El problema de negocio

NexaPlay necesita responder tres preguntas antes del Q3 2025 o entra en parálisis ejecutiva:

- El Director de Producto apuesta todo a Acción y Shooters. El Director de Innovación cree que hay géneros creciendo en silencio. **¿Qué géneros muestran crecimiento real y sostenido en los últimos 10 años?**
- La Directora de Marketing destina el 40% del presupuesto a PR bajo la hipótesis de que un 90 en Metacritic garantiza las ventas. El CFO dice que Reddit y Twitch generan más impacto. **¿Qué predice mejor las ventas: la crítica especializada o los usuarios?**
- El Director de Expansión quiere una sola campaña global. El equipo de Japón advierte que el mercado asiático consume diferente. **¿Son Occidente y Japón mercados con preferencias radicalmente opuestas?**

---

## El dataset

`games_clean.csv` — 8,296 registros de videojuegos (1980–2016), sin valores nulos.

| Columna | Descripción |
|---|---|
| `videogame_names` | Nombre del juego |
| `platform` | Plataforma (PS4, Xbox, Wii, etc.) |
| `year_of_release` | Año de lanzamiento |
| `genre` | Género (Action, Sports, RPG, etc.) |
| `na_sales` | Ventas Norteamérica (millones) |
| `eu_sales` | Ventas Europa (millones) |
| `jp_sales` | Ventas Japón (millones) |
| `other_sales` | Ventas otras regiones (millones) |
| `critic_score` | Puntuación crítica especializada |
| `user_score` | Puntuación de usuarios |
| `rating_esrb` | Clasificación ESRB |
| `total_sales` | Ventas globales (variable objetivo) |
| `gen_platform` | Generación de plataforma |
| `classification_user_score` | Clasificación categórica del user score |

---

## Arquitectura del producto

```
games_clean.csv
      |
      v
  notebooks/          <- EDA + entrenamiento del modelo (CatBoost)
      |
      v
  train_model.py      <- Pipeline de producción: preprocesa, entrena y guarda
      |
      v
  models/             <- catboost_regressor.joblib + onehot_encoder.joblib
      |
      v
  api_app.py          <- Backend FastAPI con /health y /predict
      |
      v (HTTP POST /predict)
  dashboard_app.py    <- Frontend Streamlit con 4 pestañas
```

La arquitectura separa el modelo del frontend: el dashboard no carga los `.joblib` directamente, sino que hace llamadas HTTP a la API. Eso permite actualizar el modelo sin tocar el dashboard, y viceversa.

---

## Estructura del repositorio

```
nexaplay-seminario-uniandes/
├── data/
│   └── games_clean.csv
├── models/
│   ├── catboost_regressor.joblib
│   └── onehot_encoder.joblib
├── notebooks/
│   └── nexaplay_ml.ipynb
├── scripts/
│   ├── __init__.py
│   ├── model_preprocessing.py
│   ├── model_training.py
│   └── model_saving.py
├── api_app.py
├── dashboard_app.py
├── train_model.py
└── requirements.txt
```

---

## Instalación local

```bash
git clone https://github.com/juanfenajera93/nexaplay-seminario-uniandes.git
cd nexaplay-seminario-uniandes
pip install -r requirements.txt
```

---

## Correr el proyecto localmente

Primero levantar la API (en una terminal):

```bash
uvicorn api_app:app --reload
```

Luego abrir el dashboard (en otra terminal):

```bash
streamlit run dashboard_app.py
```

La API queda disponible en `http://localhost:8000`. La documentación automática de FastAPI en `http://localhost:8000/docs`.

---

## Endpoints de la API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Verifica que el servidor está activo |
| POST | `/predict` | Recibe características de un juego y devuelve predicción de ventas globales |

Ejemplo de petición a `/predict`:

```json
{
  "platform": "PS4",
  "genre": "Action",
  "rating_esrb": "M",
  "gen_platform": "8th",
  "classification_user_score": "High",
  "year_of_release": 2015,
  "critic_score": 85.0,
  "user_score": 8.2
}
```

Respuesta:

```json
{
  "prediccion_ventas": 1.4732
}
```

---

## Deploy en la nube

| Servicio | Plataforma | URL |
|---|---|---|
| API (FastAPI) | Render | https://nexaplay-seminario-uniandes.onrender.com |
| Dashboard (Streamlit) | Streamlit Cloud | https://nexaplay-seminario-uniandes-dbp6ejaffslvnqtjt9lcev.streamlit.app |

---

## Stack tecnológico

Python · Streamlit · Plotly · FastAPI · CatBoost · scikit-learn · joblib · pandas · Render · Streamlit Cloud

---

## Contexto académico

Seminario de Analítica con Python · Universidad de los Andes · 2026

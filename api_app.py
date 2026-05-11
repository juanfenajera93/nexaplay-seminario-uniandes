import os
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

from scripts.model_preprocessing import COLUMNAS_CATEGORICAS, COLUMNAS_NUMERICAS

# ── carga de modelos ───────────────────────────────────────────────────────────
# los joblib se cargan una sola vez cuando el servidor arranca,
# no en cada petición; cargarlos cada vez sería innecesariamente lento
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH   = os.path.join(BASE_DIR, 'models', 'catboost_regressor.joblib')
ENCODER_PATH = os.path.join(BASE_DIR, 'models', 'onehot_encoder.joblib')

modelo  = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

# ── instancia de la aplicación ─────────────────────────────────────────────────
# FastAPI() crea el servidor; title aparece en la documentación automática (/docs)
app = FastAPI(title='NexaPlay Predictor API')


# ── esquema de entrada ─────────────────────────────────────────────────────────
# BaseModel define exactamente qué campos acepta el endpoint /predict y de qué tipo
# si la petición llega sin alguno de estos campos, o con un tipo incorrecto,
# FastAPI rechaza la petición automáticamente antes de que llegue al modelo
class JuegoInput(BaseModel):
    platform:                  str
    genre:                     str
    rating_esrb:               str
    gen_platform:              str
    classification_user_score: str
    year_of_release:           int
    critic_score:              float
    user_score:                float


# ── endpoint de salud ─────────────────────────────────────────────────────────
# /health no hace nada útil para el modelo; sirve para verificar que el servidor
# está corriendo antes de conectar el dashboard o cualquier otro cliente
@app.get('/health')
def health():
    return {'status': 'ok'}


# ── endpoint de predicción ─────────────────────────────────────────────────────
# recibe los datos de un juego en formato json y devuelve la predicción de ventas
# el decorador @app.post indica que esta ruta acepta peticiones de tipo POST
@app.post('/predict')
def predict(juego: JuegoInput):

    # construir un dataframe de una sola fila con las variables categóricas
    # el encoder espera un dataframe con las columnas en el mismo orden del entrenamiento
    juego_cat = pd.DataFrame([[
        juego.platform,
        juego.genre,
        juego.rating_esrb,
        juego.gen_platform,
        juego.classification_user_score
    ]], columns=COLUMNAS_CATEGORICAS)

    # lo mismo para las numéricas
    juego_num = pd.DataFrame([[
        juego.year_of_release,
        juego.critic_score,
        juego.user_score
    ]], columns=COLUMNAS_NUMERICAS)

    # transform
    # el encoder ya aprendió las categorías durante el entrenamiento,
    # aquí solo transforma; si usaras fit_transform, reescribirías lo aprendido
    juego_cat_enc = encoder.transform(juego_cat)
    nombres_ohe   = encoder.get_feature_names_out(COLUMNAS_CATEGORICAS)
    juego_cat_df  = pd.DataFrame(juego_cat_enc, columns=nombres_ohe)

    # ensamblar X con el mismo orden que se usó en el entrenamiento:
    # primero las numéricas, después las columnas del ohe
    X = pd.concat([juego_num.reset_index(drop=True), juego_cat_df], axis=1)

    # predict devuelve un array; [0] extrae el único valor que contiene
    # float() convierte el resultado de numpy a un tipo json-serializable
    prediccion = modelo.predict(X)[0]

    return {'prediccion_ventas': round(float(prediccion), 4)}

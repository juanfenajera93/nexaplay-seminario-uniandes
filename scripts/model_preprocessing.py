import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split

# variables categóricas, numéricas y target del dataset
COLUMNAS_CATEGORICAS = ['platform', 'genre', 'rating_esrb', 'gen_platform', 'classification_user_score']
COLUMNAS_NUMERICAS   = ['year_of_release', 'critic_score', 'user_score']
TARGET               = 'total_sales'

# constantes a usar 
PERCENTIL_CORTE = 95
RANDOM_STATE    = 50
TEST_SIZE       = 0.25


def preprocesar(df):
    """
    recibe el dataframe completo y devuelve los arrays del split más el encoder entrenado.
    no modifica el dataframe original.
    """

    # el top 5% de ventas (wii sports, gta v, etc.) distorsiona el entrenamiento
    # se crea una copia temporal; el csv no se modifica
    techo     = df[TARGET].quantile(PERCENTIL_CORTE / 100)
    df_modelo = df[df[TARGET] <= techo].copy().reset_index(drop=True)

    print(f'  filas originales : {len(df):,}')
    print(f'  filas en df_modelo: {len(df_modelo):,}  (techo en {techo:.2f}M)')

    # separar en features y target antes de cualquier transformación
    X_categoricas = df_modelo[COLUMNAS_CATEGORICAS]
    X_numericas   = df_modelo[COLUMNAS_NUMERICAS]
    y             = df_modelo[TARGET]

    # fit_transform aprende las categorías y las transforma en el mismo paso
    # handle_unknown='ignore' hace que la api no falle si llega una plataforma nueva
    encoder       = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    X_cat_encoded = encoder.fit_transform(X_categoricas)

    # convertir el array del ohe a dataframe para poder concatenar con las numéricas
    nombres_ohe = encoder.get_feature_names_out(COLUMNAS_CATEGORICAS)
    X_cat_df    = pd.DataFrame(X_cat_encoded, columns=nombres_ohe)

    # reset_index antes del concat para que los índices estén alineados
    X = pd.concat([X_numericas.reset_index(drop=True), X_cat_df], axis=1)

    print(f'  features totales después del ohe: {X.shape[1]}')

    # random_state=50 fija la semilla; la división es siempre la misma
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE
    )

    return X_train, X_test, y_train, y_test, encoder

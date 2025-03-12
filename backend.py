from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def filtrar_top_porcentaje(df, porcentaje=0.2):
    df_filtrado = df.copy()
    columnas_usuario = [col for col in df.columns if col != 'padre']
    
    # Agrupamos por la columna 'padre'
    for padre, grupo in df.groupby('padre'):
        indices_grupo = grupo.index  # Índices de este grupo
        
        for col in columnas_usuario:
            # Contamos cuántos valores ha puntuado cada usuario dentro del grupo (valores > 0)
            conteo_puntuaciones = (grupo[col] > 0).sum()
            
            # Calculamos cuántos elementos debemos conservar en base al porcentaje
            n_items = max(1, int(conteo_puntuaciones * porcentaje))
            
            if n_items > 0:
                # Seleccionamos los índices de los mayores valores puntuados por cada usuario
                indices_top = grupo[col].nlargest(n_items).index
                # El resto se pone a 0
                indices_no_top = grupo.index.difference(indices_top)
                df_filtrado.loc[indices_no_top, col] = 0
                
    return df_filtrado

def obtener_historial(usuarios_historico):
    """
    Convierte el DataFrame de histórico en un diccionario {usuario_id: lista de ítems visitados}
    """
    return usuarios_historico.groupby('id_user')['id_item'].apply(list).to_dict()

def get_data():
    preferencias = pd.read_csv("data/usuarios_preferencias.csv", sep = ",", header = 0)
    preferencias.columns = ['id_user', 'id_preferencia', 'score']
    matriz_preferencias = preferencias.pivot(index='id_user', columns='id_preferencia', values='score')
    columnas_deseadas = list(range(1, 116))
    matriz_preferencias = matriz_preferencias.reindex(columns=columnas_deseadas, fill_value=0)
    matriz_preferencias = matriz_preferencias.fillna(0)
    matriz_preferencias = matriz_preferencias.T

    padres = pd.read_csv("data/preferencias.csv")
    padres.index = range(1,116)

    matriz_preferencias['padre'] = padres['parent']

    # Aplicamos la función con el porcentaje deseado (ejemplo 20%)
    matriz_filtrada = filtrar_top_porcentaje(matriz_preferencias, porcentaje=0.2)

    items = pd.read_csv("data/clasificacion_items.csv", sep = ";", header = None)
    items.columns = ['id_item', 'id_preferencia', 'score']
    items = items.groupby(['id_item', 'id_preferencia'], as_index=False).mean()
    matriz_items = items.pivot(index='id_item', columns='id_preferencia', values='score')
    columnas_deseadas = list(range(1, 116))
    matriz_items = matriz_items.reindex(columns=columnas_deseadas, fill_value=0)
    matriz_items = matriz_items.fillna(0)

    matriz_filtradaT= matriz_filtrada.T
    matriz_similitud_items = cosine_similarity(matriz_items.values, matriz_filtradaT.values) #coinciden en las columnas

    matriz_similitud_items_df = pd.DataFrame(matriz_similitud_items, 
                                            index=matriz_items.index, 
                                            columns=matriz_filtradaT.index)

    matriz_similitud_items_df = matriz_similitud_items_df.T 

    items_names = pd.read_csv("data/items.csv", header = 0, sep = ",")
    items_names.columns = ['id_item', 'name_item', 'visitas']

    usuarios_historico = pd.read_csv("data/puntuaciones_usuario_base.csv", sep = ",", header = 0)
    usuarios_historico.columns = ['id_user', 'id_item', 'valoracion', "valoracion_norm"]
    usuarios_historico = usuarios_historico.drop("valoracion_norm", axis=1)
    historial_usuarios = obtener_historial(usuarios_historico)

    return (
            matriz_preferencias, 
            padres, 
            matriz_filtrada, 
            matriz_items, 
            matriz_similitud_items_df, 
            items_names, 
            usuarios_historico,
            historial_usuarios
            )


def recomendar_items(user_id, matriz_similitud, items_names, historial_usuarios, N=5):
    """
    Recomienda los N ítems más similares a los que el usuario ha visitado, 
    evitando recomendar ítems ya vistos.
    Returns a list of dictionaries, each with 'name' and 'similarity'.
    """
    items_visitados = historial_usuarios.get(user_id, [])

    if not items_visitados:
        similar_items = matriz_similitud
    else:
        similar_items = matriz_similitud.loc[user_id].drop(index=items_visitados, errors='ignore')

    top_items = similar_items.nlargest(N)

    # Create an array of objects
    recommendations = []
    for item, ratio in top_items.items():
        if item in items_names['id_item'].values:
            name = items_names.loc[items_names['id_item'] == item, 'name_item'].values[0]
            recommendations.append({
                'name': name,
                'similarity': round(ratio, 4)
            })

    return recommendations

#############################################################################

(
matriz_preferencias, 
padres, 
matriz_filtrada, 
matriz_items, 
matriz_similitud_items_df, 
items_names, 
usuarios_historico,
historial_usuarios
) = get_data()

################################################################################

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/get_title")
def get_title():
    title = "My Valencia Travel Guide - From Backend!"
    return jsonify({"title": title})

@app.route("/recommendations", methods=["POST"])
def get_recommendations():
    try:
        data = request.get_json()
        user_id = int(data.get("userId"))
        num_recommendations = data.get("num_recommendations")
        if not isinstance(num_recommendations, int):
            num_recommendations = int(num_recommendations)
        recommendations = recomendar_items(user_id, matriz_similitud_items_df, items_names, historial_usuarios, num_recommendations)
        return jsonify({"recommendations": recommendations})
    except Exception as e:
        print(e)
        return jsonify({"error": "Error getting recommendations"}), 500



@app.route("/")
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True)

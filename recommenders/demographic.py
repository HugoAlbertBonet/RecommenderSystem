import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def get_demographic_recommendations(target_user, datos_personales, grupos_preferencias, 
                                   items_clasificacion, items_names, top_n=10):
    """
    Genera recomendaciones basadas en características demográficas del usuario.
    
    El proceso consta de tres etapas principales:
    1. Clasificación del usuario en un grupo demográfico según edad, género y situación familiar.
    2. Obtención del vector de preferencias típicas del grupo asignado.
    3. Cálculo de similitud coseno entre las preferencias del grupo y los ítems disponibles.

    Retorna un diccionario {id_item: score} y el número de ítems recomendados.
    """
    # Convertir items_clasificacion a matriz
    items_group = items_clasificacion.groupby(['id_item', 'id_preferencia'], as_index=False).mean()
    matriz_items = items_group.pivot(index='id_item', columns='id_preferencia', values='score')
    columnas_deseadas = list(range(1, 116))
    matriz_items = matriz_items.reindex(columns=columnas_deseadas, fill_value=0).fillna(0)
    
    # Asignar vector demográfico (función interna)
    def asignar_vector(id_usuario):
        usuario = datos_personales[datos_personales["id"] == id_usuario]
        if usuario.empty:
            print(f"Usuario {id_usuario} no encontrado en datos demográficos.")
            return pd.Series([0]*115)
        
        matriz_grupos = grupos_preferencias.set_index("padre").T
        
        usuario = usuario.iloc[0]
        edad = usuario["age"]
        hijos = usuario["children"]
        genero = usuario["gender"]
        
        # Reglas de asignación
        if edad <= 25 and hijos == 0:
            grupo = "Menores de 25 sin hijos"
        elif edad >= 60:
            grupo = "Jubilados (>60)"
        elif edad <= 40 and hijos == 1:
            grupo = "menores de 40 con hijos"
        elif 25 <= edad <= 40 and hijos == 0:
            grupo = "25/40 sin hijos"
        elif 40 <= edad <= 60 and genero == "F":
            grupo = "mujeres entre 40 y 60"
        elif 40 <= edad <= 60 and genero == "M":
            grupo = "hombres entre 40 y 60"
        else:
            return pd.Series([0]*matriz_grupos.shape[0], index=matriz_grupos.index)
        # Devuelve el vector de preferencias o ceros si no encuentra el grupo
        return grupos_preferencias.get(grupo, pd.Series([0]*matriz_grupos.shape[0], index=matriz_grupos.index)).values
    
    vector_usuario = asignar_vector(target_user)
    if vector_usuario.sum() == 0:  # No se encontró grupo
        return {}, 0
    
    # Calcular similitud coseno
    similitudes = cosine_similarity(matriz_items, vector_usuario.reshape(1, -1)).flatten()
    scores = pd.Series(similitudes, index=matriz_items.index)
    
    # Ordenar y devolver top N
    top_items = scores.sort_values(ascending=False).head(top_n)
    return top_items.to_dict(), len(top_items)
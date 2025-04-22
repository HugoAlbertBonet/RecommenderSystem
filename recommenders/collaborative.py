import numpy as np
import pandas as pd
from scipy.stats import pearsonr


def compute_user_similarity(user_item_matrix, min_intersection=3):
    """
    Calcula la matriz de similitud entre usuarios usando el coeficiente de Pearson.
    Si la cantidad de ítems en común es menor que min_intersection, se usa la unión
    (rellenando con 0 los faltantes).
    """
    users = user_item_matrix.index.tolist()
    n_users = len(users)
    sim_matrix = pd.DataFrame(index=users, columns=users, dtype=float)
    
    for i in range(n_users):
        for j in range(i, n_users):
            u1 = users[i]
            u2 = users[j]
            v1 = user_item_matrix.loc[u1]
            v2 = user_item_matrix.loc[u2]
            inter_mask = v1.notna() & v2.notna()
            
            if inter_mask.sum() >= min_intersection:
                try:
                    sim = pearsonr(v1[inter_mask], v2[inter_mask])[0]
                except Exception:
                    sim = np.nan
            else:
                union_mask = v1.notna() | v2.notna()
                v1_union = v1[union_mask].fillna(0)
                v2_union = v2[union_mask].fillna(0)
                try:
                    sim = pearsonr(v1_union, v2_union)[0]
                except Exception:
                    sim = np.nan
            
            sim_matrix.loc[u1, u2] = sim
            sim_matrix.loc[u2, u1] = sim
    return sim_matrix

def get_collaborative_recommendations(user_item_matrix, sim_matrix, target_user, n_neighbors=20, min_threshold=0.7):
    """
    Obtiene recomendaciones colaborativas:
      - Se buscan los vecinos (usuarios) similares que cumplan un umbral mínimo.
      - Se acumulan scores para cada ítem (excluyendo los ya valorados por el usuario).
      - Se devuelve un diccionario {id_item: score} y la cantidad total de vecinos utilizados.
    """
    neighbors = sim_matrix.loc[target_user].drop(target_user).dropna()
    valid_neighbors = neighbors[neighbors >= min_threshold].sort_values(ascending=False)
    top_neighbors = valid_neighbors.iloc[:n_neighbors]
    
    target_items = user_item_matrix.loc[target_user].dropna().index.tolist()
    rec_scores = {}
    rec_weights = {}
    neighbor_count = {}
    
    
    for neighbor, sim in top_neighbors.items():
        neighbor_ratings = user_item_matrix.loc[neighbor]
        # Umbral dinámico: promedio de ratings del vecino
        dynamic_threshold = neighbor_ratings.mean()
        favorable_items = neighbor_ratings[neighbor_ratings > dynamic_threshold].dropna()
        
        for item, rating in favorable_items.items():
            if item in target_items:
                continue
            rec_scores[item] = rec_scores.get(item, 0) + sim * rating
            rec_weights[item] = rec_weights.get(item, 0) + abs(sim)
            neighbor_count[item] = neighbor_count.get(item, 0) + 1
            
    # Definir una escala para normalizar (score mínimo y máximo esperado)
    min_ratio = 1
    max_ratio = 7 + np.log(n_neighbors + 1)
    final_scores = {item: ((rec_scores[item] / rec_weights[item]) + np.log(1 + neighbor_count[item]) - min_ratio) / (max_ratio - min_ratio)
                    for item in rec_scores if rec_weights[item] != 0}
    
    total_neighbors = len(top_neighbors)
    return final_scores, len(final_scores)*(total_neighbors/n_neighbors)

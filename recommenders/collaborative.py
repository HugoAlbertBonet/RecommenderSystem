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

# collaborative.py
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

def get_collaborative_recommendations(user_item_matrix, sim_matrix, target_user,
                                    n_neighbors=20, min_threshold=0.7):
    # Obtener vecinos
    sim_series = sim_matrix.loc[target_user].drop(target_user).dropna()
    top_neighbors = sim_series[sim_series >= min_threshold].nlargest(n_neighbors)

    target_items = user_item_matrix.loc[target_user].dropna().index.tolist()

    rec_scores = {}
    rec_weights = {}
    neighbor_count = {}
    neighbor_sum_ratings = {}

    for neighbor, sim in top_neighbors.items():
        ratings = user_item_matrix.loc[neighbor]
        threshold = ratings.mean()
        favorable = ratings[ratings > threshold].dropna()
        for item, rating in favorable.items():
            if item in target_items:
                continue
            rec_scores[item] = rec_scores.get(item, 0) + sim * rating
            rec_weights[item] = rec_weights.get(item, 0) + abs(sim)
            neighbor_count[item] = neighbor_count.get(item, 0) + 1
            neighbor_sum_ratings[item] = neighbor_sum_ratings.get(item, 0) + rating

    # Normalizar scores
    min_ratio = 1
    max_ratio = 7 + np.log(n_neighbors + 1)
    final_scores = {}
    for itm, score in rec_scores.items():
        weight = rec_weights.get(itm, 0)
        count = neighbor_count.get(itm, 0)
        if weight == 0:
            continue
        raw = (score / weight) + np.log(1 + count)
        final_scores[itm] = (raw - min_ratio) / (max_ratio - min_ratio)

    # Calcular media de rating de vecinos
    neighbor_mean = {itm: neighbor_sum_ratings[itm] / neighbor_count[itm]
                     for itm in neighbor_sum_ratings}

    # Devolver: scores normalizados, número de vecinos, medias
    return final_scores, len(top_neighbors), neighbor_mean

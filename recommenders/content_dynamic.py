import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def get_content_recommendations(usuarios_historico, items_names, preferencias, padres, items_clasificacion,
                                target_user, N=10, alpha=0.33, beta=0.33, gamma=0.34, dynamic_threshold_factor=0.9):
    """
    Genera recomendaciones basadas en contenido mediante un enfoque aditivo.
    Se construyen las matrices de preferencias y de ítems, se calcula la similitud
    y se combina la similitud con el historial y la popularidad (visitas).

    Ahora, en lugar de devolver siempre N recomendaciones, se aplica un umbral dinámico
    (por defecto el percentil 80) sobre el score final; si se obtienen pocas, se usa
    el fallback a las N mejores.
    
    Retorna un diccionario {id_item: score} y el número de ítems recomendados.
    """
    # Matriz de preferencias
    matriz_preferencias = preferencias.pivot(index='id_user', columns='id_preferencia', values='score')
    columnas_deseadas = list(range(1, 116))
    matriz_preferencias = matriz_preferencias.reindex(columns=columnas_deseadas, fill_value=0).fillna(0)
    matriz_preferencias = matriz_preferencias.T  # filas: id_preferencia, columnas: id_user
    matriz_preferencias['padre'] = padres.set_index('id').loc[matriz_preferencias.index, 'name']
    
    # Filtrado: conservar el top porcentaje de puntuaciones en cada categoría
    def filtrar_top_porcentaje(df, porcentaje=0.2):
        df_filtrado = df.copy()
        columnas_usuario = [col for col in df.columns if col != 'padre']
        for padre, grupo in df.groupby('padre'):
            for col in columnas_usuario:
                conteo = (grupo[col] > 0).sum()
                n_items = max(1, int(conteo * porcentaje))
                if n_items > 0:
                    indices_top = grupo[col].nlargest(n_items).index
                    indices_no_top = grupo.index.difference(indices_top)
                    df_filtrado.loc[indices_no_top, col] = 0
        return df_filtrado
    
    matriz_filtrada = filtrar_top_porcentaje(matriz_preferencias, porcentaje=0.2)
    
    # Matriz de ítems a partir de clasificacion_items
    items_group = items_clasificacion.groupby(['id_item', 'id_preferencia'], as_index=False).mean()
    matriz_items = items_group.pivot(index='id_item', columns='id_preferencia', values='score')
    matriz_items = matriz_items.reindex(columns=columnas_deseadas, fill_value=0).fillna(0)
    
    # Similitud entre ítems y preferencias filtradas
    matriz_filtradaT = matriz_filtrada.drop(columns=['padre']).T
    similitud_items = cosine_similarity(matriz_items.values, matriz_filtradaT.values)
    matriz_similitud_items_df = pd.DataFrame(similitud_items, index=matriz_items.index,
                                             columns=matriz_filtradaT.index).T
    
    # Histórico de interacciones y popularidad
    interacciones = pd.merge(usuarios_historico, items_names[['id_item', 'visitas']],
                             on='id_item', how='left')
    interacciones['visitas'] = interacciones['visitas'].fillna(0)
    interacciones['weighted_rating'] = interacciones.apply(
        lambda row: row['valoracion'] if row['valoracion'] >= 4 else -row['valoracion'], axis=1)
    
    matriz_interacciones = interacciones.pivot(index='id_user', columns='id_item', values='weighted_rating').fillna(0)
    
    # Vector del usuario por categoría
    items_clasificacion_cp = items_clasificacion.copy()
    items_clasificacion_cp.columns = ['id_item', 'id_padre', 'score']
    interacciones_con_padre = pd.merge(interacciones, items_clasificacion_cp[['id_item', 'id_padre', 'score']],
                                       on='id_item', how='left')
    interacciones_con_padre['total_score'] = interacciones_con_padre.groupby('id_item')['score'].transform('sum')
    interacciones_con_padre['weighted_rating_final'] = interacciones_con_padre['weighted_rating'] * \
        (interacciones_con_padre['score'] / interacciones_con_padre['total_score'])
    agrupado = interacciones_con_padre.groupby(['id_user', 'id_padre'])['weighted_rating_final'].sum().reset_index()
    vector_por_usuario = agrupado.pivot(index='id_user', columns='id_padre', values='weighted_rating_final').fillna(0)
    vector_por_usuario = vector_por_usuario.reindex(columns=columnas_deseadas, fill_value=0)
    
    matriz_similitud_interacciones = cosine_similarity(vector_por_usuario, matriz_items)
    df_similitud_interacciones = pd.DataFrame(matriz_similitud_interacciones,
                                              index=vector_por_usuario.index,
                                              columns=matriz_items.index)
    # Transponer para tener items en el índice
    matriz_similitud_items_df = matriz_similitud_items_df.T

    if target_user not in matriz_similitud_items_df.columns or target_user not in df_similitud_interacciones.index:
        return {}, 0
    score_pref = matriz_similitud_items_df[target_user]
    score_hist = df_similitud_interacciones.loc[target_user]
    score_vis = items_names.set_index('id_item')['visitas'].apply(lambda x: np.log(1 + x))
    
    common_items = score_pref.index.intersection(score_hist.index).intersection(score_vis.index)
    score_pref = score_pref.loc[common_items]
    score_hist = score_hist.loc[common_items]
    score_vis = score_vis.loc[common_items]
    
    # Normalización de cada score
    def normalize_series(s):
        if s.max() == s.min():
            return s
        return (s - s.min()) / (s.max() - s.min())
    
    score_pref_norm = normalize_series(score_pref)
    score_hist_norm = normalize_series(score_hist)
    score_vis_norm = normalize_series(score_vis)
    
    final_score = alpha * score_pref_norm + beta * score_hist_norm + gamma * score_vis_norm
    
    # Excluir ítems ya visitados
    historial = usuarios_historico.groupby('id_user')['id_item'].apply(list).to_dict()
    items_visitados = historial.get(target_user, [])
    final_score = final_score.drop(labels=items_visitados, errors='ignore')
    
    # Aplicar un umbral dinámico basado en el percentil 80
    dynamic_threshold = final_score.quantile(dynamic_threshold_factor)
    dynamic_recs = final_score[final_score >= dynamic_threshold].sort_values(ascending=False)
    
    # Si se obtienen pocas recomendaciones, se hace fallback a las top N
    if len(dynamic_recs) < N:
        dynamic_recs = final_score.nlargest(N)
    
    num_recs = len(dynamic_recs)
    return dynamic_recs.to_dict(), num_recs
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def get_content_recommendations(
    usuarios_historico: pd.DataFrame,
    items_names: pd.DataFrame,
    preferencias: pd.DataFrame,
    padres: pd.DataFrame,
    items_clasificacion: pd.DataFrame,
    target_user: int,
    N: int = 10,
    alpha: float = 0.33,
    beta: float = 0.33,
    gamma: float = 0.34,
    dynamic_threshold_factor: float = 0.8
) -> (dict, dict, int):
    # 1) Preferencias por usuario×categoría
    mat_pref = preferencias.pivot(
        index='id_user', columns='id_preferencia', values='score'
    ).reindex(columns=range(1,116), fill_value=0).fillna(0)

    # Map categoría→padre
    cat_to_padre = padres.set_index('id')['name'].to_dict()

    # 2) Filtrar top 20% en cada 'padre'
    mat_pref_T = mat_pref.T
    mat_pref_T['padre'] = mat_pref_T.index.map(cat_to_padre)

    def filtrar_top_porcentaje(df: pd.DataFrame, pct: float = 0.2):
        df_f = df.copy()
        usuarios = [c for c in df.columns if c != 'padre']
        for padre, sub in df.groupby('padre'):
            pref_ids = sub.index
            for u in usuarios:
                user_scores = df.loc[pref_ids, u]
                cnt = (user_scores > 0).sum()
                top_n = max(1, int(cnt * pct))
                top_prefs = user_scores.nlargest(top_n).index
                to_zero = pref_ids.difference(top_prefs)
                df_f.loc[to_zero, u] = 0
        return df_f

    mat_filt = filtrar_top_porcentaje(mat_pref_T, pct=0.2).drop(columns=['padre']).T

    # 3) Matriz de ítems×categoría
    items_grp = items_clasificacion.groupby(
        ['id_item','id_preferencia'], as_index=False
    )['score'].mean()
    mat_items = items_grp.pivot(
        index='id_item', columns='id_preferencia', values='score'
    ).reindex(columns=range(1,116), fill_value=0).fillna(0)

    # 4) Cosine similarity usuario_prefs→item_prefs
    sim_pref = cosine_similarity(mat_filt.values, mat_items.values)
    df_sim_pref = pd.DataFrame(
        sim_pref,
        index=mat_filt.index,
        columns=mat_items.index
    )

    # 5) Historial ponderado y popularidad
    inter = usuarios_historico.merge(
        items_names[['id_item','visitas']], on='id_item', how='left'
    ).fillna({'visitas':0})
    inter['weighted_rating'] = inter['valoracion'].where(
        inter['valoracion']>=4, -inter['valoracion']
    )

    clas_cp = items_clasificacion.rename(
        columns={'id_preferencia':'id_padre'}
    )[['id_item','id_padre','score']]
    inter_cp = inter.merge(clas_cp, on='id_item', how='left')
    inter_cp['tot_score'] = inter_cp.groupby('id_item')['score'].transform('sum')
    inter_cp['wr_final'] = inter_cp['weighted_rating'] * (
        inter_cp['score'] / inter_cp['tot_score']
    )

    vec_usr = inter_cp.groupby(['id_user','id_padre'])['wr_final'] \
                     .sum().unstack(fill_value=0) \
                     .reindex(index=mat_filt.index, columns=range(1,116), fill_value=0)
    sim_hist = cosine_similarity(vec_usr.values, mat_items.values)
    df_sim_hist = pd.DataFrame(
        sim_hist,
        index=vec_usr.index,
        columns=mat_items.index
    )

    # 6) Extraer series para target_user o usar ceros
    all_items = mat_items.index
    score_pref = df_sim_pref.loc[target_user] if target_user in df_sim_pref.index \
                 else pd.Series(0, index=all_items)
    score_hist = df_sim_hist.loc[target_user] if target_user in df_sim_hist.index \
                 else pd.Series(0, index=all_items)
    score_vis  = items_names.set_index('id_item')['visitas'] \
                    .apply(np.log1p).reindex(all_items).fillna(0)

    # 7) Normalizar con reemplazo de ptp→max-min
    def normalize(s: pd.Series) -> pd.Series:
        rng = s.max() - s.min()
        return (s - s.min())/rng if rng>0 else s

    pref_n = normalize(score_pref)
    hist_n = normalize(score_hist)
    vis_n  = normalize(score_vis)

    # 8) Score aditivo
    final_score = alpha*pref_n + beta*hist_n + gamma*vis_n

    # 9) Excluir visitados y aplicar umbral/fallback
    visited = usuarios_historico.groupby('id_user')['id_item'] \
                 .apply(list).to_dict().get(target_user, [])
    final_score = final_score.drop(labels=visited, errors='ignore')
    thresh = final_score.quantile(dynamic_threshold_factor)
    dyn = final_score[final_score>=thresh].sort_values(ascending=False)
    if len(dyn)<N:
        dyn = final_score.nlargest(N)

    # 10) Detalles explicativos
    details = {
        itm: {
            'sim_score':  float(pref_n.loc[itm]),
            'hist_score': float(hist_n.loc[itm]),
            'vis_score':  float(vis_n.loc[itm])
        }
        for itm in dyn.index
    }

    return dyn.to_dict(), details, len(dyn)

from recommenders.collaborative import get_collaborative_recommendations
from recommenders.content_dynamic import get_content_recommendations
from recommenders.demographic   import get_demographic_recommendations

def compute_dynamic_weights(collab_neighbors, content_count, demo_count, base_weights):
    expected = collab_neighbors + min(20, content_count)
    f_collab  = min(1, collab_neighbors  / expected) if expected>0 else 1
    f_content = min(1, min(20, content_count) / expected) if expected>0 else 1
    f_demo    = 0.2

    w = {
        'collaborative': base_weights['collaborative'] * f_collab,
        'content':       base_weights['content']       * f_content,
        'demographic':   base_weights['demographic']   * f_demo
    }
    total = sum(w.values())
    if total>0:
        for k in w: w[k] /= total
    else:
        w = {k: 1/3 for k in w}
    return w




def hybrid_recommender(
    target_user,
    user_item_matrix, sim_matrix,
    usuarios_historico, items_names,
    preferencias, padres, items_clasificacion,
    datos_personales, grupos_preferencias,
    base_weights={'collaborative':0.33,'content':0.33,'demographic':0.34},
    top_n=10,
    set_weights=None,
    content_alpha=0.33,
   content_beta=0.33,
   content_gamma=0.34
):

    # ─── 1) Pesos finales ───────────────────────────────────────────
    if set_weights is not None:
        w = set_weights
    else:
        # counts para dynamic weights
        _, _, content_count = get_content_recommendations(
            usuarios_historico, items_names, preferencias, padres,
            items_clasificacion, target_user, N=top_n, alpha = content_alpha,
            beta = content_beta, gamma = content_gamma
        )
        _, collab_count, _ = get_collaborative_recommendations(
            user_item_matrix, sim_matrix, target_user
        )
        demo_list = get_demographic_recommendations(
            target_user, datos_personales, grupos_preferencias,
            items_clasificacion, items_names, top_n=top_n
        ) or []
        demo_count = len(demo_list)

        w = compute_dynamic_weights(collab_count, content_count, demo_count, base_weights)

    # ─── 2) Collaborative ──────────────────────────────────────────
    rec_collab, collab_count, collab_mean = \
        (get_collaborative_recommendations(user_item_matrix, sim_matrix, target_user)
         if w['collaborative']>0 else ({},0,{}))

    # ─── 3) Content‑Based ──────────────────────────────────────────
    if w['content'] > 0:
        rec_content, content_details, content_count = get_content_recommendations(
            usuarios_historico, items_names, preferencias, padres,
            items_clasificacion, target_user, N=top_n, alpha=content_alpha,
            beta=content_beta,
            gamma=content_gamma
        )
    else:
        rec_content, content_details, content_count = {}, {}, 0

    # ─── 4) Demográfico ────────────────────────────────────────────
    if w['demographic'] > 0:
        demo_list = get_demographic_recommendations(
            target_user, datos_personales, grupos_preferencias,
            items_clasificacion, items_names, top_n=top_n
        ) or []
        demo_count  = len(demo_list)
        rec_demo    = {d['id_item']: d['demo_score'] for d in demo_list}
        demo_detail = {d['id_item']: d for d in demo_list}
    else:
        rec_demo, demo_detail, demo_count = {}, {}, 0

    # ─── 5) Combinar ──────────────────────────────────────────────
    all_items   = set(rec_collab)|set(rec_content)|set(rec_demo)
    hybrid_list = []

    for item in all_items:
        score_h = (w['collaborative']*rec_collab.get(item,0) +
                   w['content']      *rec_content.get(item,0) +
                   w['demographic']  *rec_demo.get(item,0))

        entry = {'id_item': item, 'hybrid_score': score_h}

        if item in rec_collab:
            entry['neighbor_count']       = collab_count
            entry['neighbor_mean_rating'] = collab_mean.get(item,0)

        if item in rec_content:
            det = content_details[item]
            entry.update({
                'sim_score': det['sim_score'],
                'hist_score':det['hist_score'],
                'vis_score': det['vis_score']
            })

        if item in rec_demo:
            ddet = demo_detail[item]
            entry.update({
                'demo_score': ddet['demo_score'],
                'group':      ddet['group'],
                'explanation':ddet['explanation']
            })

        hybrid_list.append(entry)

    hybrid_list.sort(key=lambda x: x['hybrid_score'], reverse=True)
    print(hybrid_list)
    return hybrid_list[:top_n]

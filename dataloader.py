import pandas as pd
import json

# =============================================================================
# FUNCIONES DE CARGA DE DATOS
# =============================================================================
def load_data(root = "data"):
    """
    Carga los datasets necesarios:
      - Histórico de valoraciones de usuarios.
      - Información de ítems (nombre, visitas, etc.).
      - Preferencias de usuarios.
      - Información de categorías (padres).
      - Clasificación de ítems según preferencias.
    """
    usuarios_historico = pd.read_csv(f"{root}/puntuaciones_usuario_base.csv", sep=";", header=None)
    usuarios_historico.columns = ['id_user', 'id_item', 'valoracion']
    
    items_names = pd.read_csv(f"{root}/items.csv", sep=";", header=None, encoding="latin-1")
    items_names.columns = ['id_item', 'name_item', 'visitas']
    
    preferencias = pd.read_csv(f"{root}/usuarios_preferencias.csv", sep=";", header=None)
    preferencias.columns = ['id_user', 'id_preferencia', 'score']
    
    padres = pd.read_csv(f"{root}/preferencias.csv", encoding="latin-1", sep = ";", header = None)
    if 'id' not in padres.columns:
        padres.rename(columns={padres.columns[0]: 'id', padres.columns[1]: 'name'}, inplace=True)
    
    items_clasificacion = pd.read_csv(f"{root}/clasificacion_items.csv", sep=";", header=None)
    items_clasificacion.columns = ['id_item', 'id_preferencia', 'score']

    datos_personales = pd.read_csv(f"{root}/usuarios_datos_personales.csv", sep=";")
    datos_personales.columns = ['id', 'name', 'age','gender','job','children','younger','older']
    
    grupos_preferencias = pd.read_csv(f"{root}/preferencias_gpt_v1.csv", sep=";")
    
    return usuarios_historico, items_names, preferencias, padres, items_clasificacion, datos_personales, grupos_preferencias


def check_exists(userid):
    file = pd.read_csv("data/usuarios_datos_personales.csv", sep=";", header=None)
    if userid in file.iloc[:, 0]:
        return 0
    return 1

def add_user_data(userid, 
                  user_name, 
                  userAge, 
                  userGender, 
                  userJob, 
                  userChildren, 
                  userChildrenOld, 
                  userChildrenYoung):
  file = pd.read_csv("data/usuarios_datos_personales.csv", sep=";", header=None)
  new_user = [
      userid,
      user_name,
      userAge,
      userGender,
      userJob,
      userChildren,
      userChildrenOld,
      userChildrenYoung
  ]

  # Add a single row using the append() method
  try:
    file.loc[len(file)] = new_user
    file.to_csv("data/usuarios_datos_personales.csv", sep=";", index=False, header=False)
    return 1
  except:
      return 0
  
def add_user_preferences(userid, ratings):
    try:
      file = pd.read_csv("data/usuarios_preferencias.csv", sep=";", header=None)
      for k, v in ratings.items():
          if v > 0:
              file.loc[len(file)] = [userid, int(k), v]
      file.to_csv("data/usuarios_preferencias.csv", sep=";", index=False, header=False)
      return 1
    except:
        return 0
    
    
def get_individual_users():
    try:
        file =  pd.read_csv("data/usuarios_datos_personales.csv", sep=";", header=None)
        # Return a list of dictionaries username: userid
        users = []
        for i in range(len(file)):
            users.append({"name": str(file.iloc[i, 1]), "user_id": int(file.iloc[i, 0])})
        return users
    except:
        return None
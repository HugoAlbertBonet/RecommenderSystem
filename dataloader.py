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
    
    return usuarios_historico, items_names, preferencias, padres, items_clasificacion


def add_user_password(userid, password):
    with open("data/credentials.json", "r") as file:
        credentials = json.load(file)
    if userid in credentials:
        return 0
    credentials[userid] = password
    with open("data/credentials.json", "w") as file:
        json.dump(credentials, file)
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
    return 1
  except:
      return 0
import pandas as pd

with open("data/usuarios_datos_personales.txt", "r") as f:
    text = f.read()

# read them and creat a pandas dataframe with columns id, name, parent
list_of_lines = text.split("\n")
d = {"id": [], "name": [], "age": [], "gender": [], "job": [], "children": [], "younger": [], "older": []}
for i in range(0, len(list_of_lines)-len(d), len(d)):
    idx = list_of_lines[i]
    name = list_of_lines[i+1]
    age = list_of_lines[i+2]
    gender = list_of_lines[i+3]
    job = list_of_lines[i+4]
    children = list_of_lines[i+5]
    younger = list_of_lines[i+6]
    older = list_of_lines[i+7]
    d["id"].append(idx)
    d["name"].append(name)
    d["age"].append(age)
    d["gender"].append(gender)
    d["job"].append(job)
    d["children"].append(children)
    d["younger"].append(younger)
    d["older"].append(older)

df = pd.DataFrame(d)
df.to_csv("data/usuarios_datos_personales.csv", index=False)



with open("data/usuarios_preferencias.txt", "r") as f:
    text = f.read()

# read them and creat a pandas dataframe with columns id, name, parent
list_of_lines = text.split("\n")
d = {"id": [], "preference": [], "interest": []}
for i in range(0, len(list_of_lines)-len(d), len(d)):
    idx = list_of_lines[i]
    preference = list_of_lines[i+1]
    interest = list_of_lines[i+2]
    d["id"].append(idx)
    d["preference"].append(preference)
    d["interest"].append(interest)

df = pd.DataFrame(d)
df.to_csv("data/usuarios_preferencias.csv", index=False)

with open("data/puntuaciones_usuario_base.txt", "r") as f:
    text = f.read()

# read them and creat a pandas dataframe with columns id, name, parent
list_of_lines = text.split("\n")
d = {"id": [], "place": [], "mark": [], "mark_norm": []}
for i in range(0, len(list_of_lines)-3, 3):
    idx = list_of_lines[i]
    place = list_of_lines[i+1]
    mark = int(list_of_lines[i+2])
    d["id"].append(idx)
    d["place"].append(place)
    d["mark"].append(mark)
    d["mark_norm"].append(round((mark/7)*100))


df = pd.DataFrame(d)
df.to_csv("data/puntuaciones_usuario_base.csv", index=False)

with open("data/puntuaciones_usuario_test.txt", "r") as f:
    text = f.read()

# read them and creat a pandas dataframe with columns id, name, parent
list_of_lines = text.split("\n")
d = {"id": [], "place": [], "mark": [], "mark_norm": []}
for i in range(0, len(list_of_lines)-3, 3):
    idx = list_of_lines[i]
    place = list_of_lines[i+1]
    mark = int(list_of_lines[i+2])
    d["id"].append(idx)
    d["place"].append(place)
    d["mark"].append(mark)
    d["mark_norm"].append(round((mark/7)*100))


df = pd.DataFrame(d)
df.to_csv("data/puntuaciones_usuario_test.csv", index=False)

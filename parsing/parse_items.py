import pandas as pd

with open("data/items.txt", "r") as f:
    text = f.read()

# read them and creat a pandas dataframe with columns id, name, parent
list_of_lines = text.split("\n")
d = {"id": [], "name": [], "visits": []}
for i in range(0, len(list_of_lines)-3, 3):
    idx = list_of_lines[i]
    name = list_of_lines[i + 1]
    visits = list_of_lines[i + 2]
    d["id"].append(idx)
    d["name"].append(name)
    d["visits"].append(visits)

df = pd.DataFrame(d)
df.to_csv("data/items.csv", index=False)

with open("data/clasificacion_items.txt", "r") as f:
    text = f.read()

# read them and creat a pandas dataframe with columns id, name, parent
list_of_lines = text.split("\n")
d = {"id": [], "preference": [], "level": []}
for i in range(0, len(list_of_lines)-3, 3):
    idx = list_of_lines[i]
    preference = list_of_lines[i + 1]
    level = list_of_lines[i + 2]
    d["id"].append(idx)
    d["preference"].append(preference)
    d["level"].append(level)

df = pd.DataFrame(d)
df.to_csv("data/clasificacion_items.csv", index=False)
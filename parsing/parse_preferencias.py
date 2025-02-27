import pandas as pd

with open("data/preferencias.txt", "r") as f:
    text = f.read()

# read them and creat a pandas dataframe with columns id, name, parent
list_of_lines = text.split("\n")
d = {"id": [], "name": [], "parent": []}
for i in range(0, len(list_of_lines)-3, 3):
    idx = list_of_lines[i]
    name = list_of_lines[i + 1]
    parent = list_of_lines[i + 2]
    d["id"].append(idx)
    d["name"].append(name)
    d["parent"].append(parent)

df = pd.DataFrame(d)
df.to_csv("data/preferencias.csv", index=False)


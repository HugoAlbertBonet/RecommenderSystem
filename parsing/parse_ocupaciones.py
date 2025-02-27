import pandas as pd

with open("data/ocupaciones.txt", "r") as f:
    text = f.read()

# read them and creat a pandas dataframe with columns id, name, parent
list_of_lines = text.split("\n")
d = {"id": [], "description": []}
for i in range(0, len(list_of_lines)-2, 2):
    idx = list_of_lines[i]
    name = list_of_lines[i + 1]
    d["id"].append(idx)
    d["description"].append(name)

df = pd.DataFrame(d)
df.to_csv("data/ocupaciones.csv", index=False)

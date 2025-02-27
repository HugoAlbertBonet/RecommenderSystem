import os
import json 
import requests 
from bs4 import BeautifulSoup 
import pandas as pd
from tqdm import tqdm

GOOGLE_IMAGE = \
    'https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&'

# The User-Agent request header contains a characteristic string 
# that allows the network protocol peers to identify the application type, 
# operating system, and software version of the requesting software user agent.
# needed for google search
usr_agent = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
}

i=0
SAVE_FOLDER = 'images'


def main():
    if not os.path.exists(SAVE_FOLDER):
        print("Making Directory")
        os.mkdir(SAVE_FOLDER)
    print("Directory exists")
    download_images()
    
def download_images():
    df = pd.read_csv('data/items.csv')
    idnames = list(zip(df["id"], df["name"]))
    print(len(idnames))
    for name in tqdm(idnames):
        id, data = name
        #print('Start searching...')
        
        searchurl = GOOGLE_IMAGE + 'q=' + data
        #print(searchurl)

        # request url, without usr_agent the permission gets denied
        response = requests.get(searchurl, headers=usr_agent)
        html = response.text
        
        #Parsing HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        #Retrieveing number of files present in the folder
        global i
        imagelinks= []
        lista = os.listdir(SAVE_FOLDER) # dir is your directory path
        i = len(lista)
        #print(i)
        
        #Search for Class "img" and eventually obtain links in "data-src" 
        for link in soup.find_all('img'):
            #print(link)
            op = link.get('src')
            if not op or "http" not in op:
                continue
            else:
                response = requests.get(op)
                os.mkdir(SAVE_FOLDER + '/' + str(id))
                imagename = SAVE_FOLDER + '/' + str(id) + "/" + data + str(i+1) + '.jpg'
                with open(imagename, 'wb') as file:
                    file.write(response.content)
                break
                print("IMAGE LINKS:", link.get('src'))

    print('Done Downloading')

if __name__ == '__main__':
    main()
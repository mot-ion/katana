import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO


def is_valid_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException:
        return False


def scrape_gifs(query, count):
    search_url = f"https://tenor.com/search/{query}-gifs"
    response = requests.get(search_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    gifs = []
    gif_tags = soup.find_all('img',
                             limit=count * 2)  # Erhöhen der Anzahl der gefundenen Bilder, um mehr Auswahl zu haben

    for tag in gif_tags:
        gif_url = tag['src']
        if gif_url.endswith('.gif') and is_valid_url(gif_url):
            # Überprüfen der Bilddimensionen
            img_response = requests.get(gif_url)
            img = Image.open(BytesIO(img_response.content))
            width, height = img.size

            if width / height >= 1.5:
                gifs.append(gif_url)
                if len(gifs) >= count:
                    break

    return gifs


# Beispielaufruf der Funktion mit gewünschter GIF-Anzahl
query = "wave anime"
anzahl_gifs = 50
gif_list = scrape_gifs(query, count=anzahl_gifs)

print("Gefundene GIF-URLs im Querformat mit Mindestbreite:")
for gif in gif_list:
    print(gif)

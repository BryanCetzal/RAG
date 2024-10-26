import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import requests.compat

# Función para extraer enlaces de carpetas
def ExtraerURLsCarpetas(url, headers):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    carpetas = soup.find_all('div', class_='list-lead')
    
    urls_carpetas = []
    for carpeta in carpetas:
        enlace = carpeta.find('a')['href']
        enlace_completo = requests.compat.urljoin(url, enlace)
        urls_carpetas.append(enlace_completo)

    return urls_carpetas

# Función para extraer el contenido de cada artículo, junto con videos, imágenes, listas y enlaces
def ExtraerContenidoArticulo(enlace, headers):
    response = requests.get(enlace, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    contenedorArticulo = soup.find('article', class_='article-body')

    if contenedorArticulo: 
        textoArticulo = contenedorArticulo.get_text(separator=' ').strip()

        # Extraer metadatos
        fecha = soup.find('time')['datetime'] if soup.find('time') else 'Fecha no disponible'
        categoria = soup.find('div', class_='categoria').text if soup.find('div', class_='categoria') else 'Categoría no disponible'

        # Extraer videos (iframes)
        videos = soup.find_all('iframe')
        enlacesVideos = [video['src'] for video in videos]

        # Extraer imágenes
        imagenes = soup.find_all('img')
        enlacesImagenes = [imagen['src'] for imagen in imagenes]

        # Extraer listas y enlaces usando la nueva función
        listas, enlaces_internos, enlaces_externos = extraer_datos_articulo(soup, enlace)

        return (textoArticulo, fecha, categoria, enlacesVideos, enlacesImagenes, listas, enlaces_internos, enlaces_externos)
    else:
        return "", "", "", [], [], [], [], []

def extraer_datos_articulo(soup, enlace_completo):
    try:
        # Extraer listas (si existen)
        listas = []
        for lista in soup.find_all(['ul', 'ol']):
            items = [item.get_text(strip=True) for item in lista.find_all('li')]
            listas.append(items)

        # Extraer enlaces internos y externos
        enlaces_internos = []
        enlaces_externos = []
        for enlace in soup.find_all('a', href=True):
            url_enlace = requests.compat.urljoin(enlace_completo, enlace['href'])
            print(f"Procesando enlace: {url_enlace}")
            if "soporte" in url_enlace: 
                enlaces_internos.append(url_enlace)
            else:
                enlaces_externos.append(url_enlace)

        return listas, enlaces_internos, enlaces_externos
    except Exception as e:
        print(f"Error al extraer datos del artículo: {e}")
        return [], [], []

# Scraper principal que extrae los artículos dentro de cada carpeta
def ScraperPrincipal(url, headers, carpeta_base):
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        articulos = soup.find_all('div', class_='ellipsis article-title')

        for articulo in articulos:
            titulo = articulo.text.strip()
            enlace = articulo.find('a')['href']
            enlace_completo = requests.compat.urljoin(url, enlace)
            print(f"Artículo encontrado: {titulo}, Enlace completo: {enlace_completo}")

            # Extraer el contenido del artículo
            texto, fecha, categoria, videos, imagenes, listas, enlaces_internos, enlaces_externos = ExtraerContenidoArticulo(enlace_completo, headers)

            # Guardar el contenido en un archivos .txt
            if texto:
                nombre_archivo = f"{titulo}.txt"
                nombre_archivo = "".join([c for c in nombre_archivo if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).rstrip()  # Limpiar el nombre del archivo
                ruta_archivo = os.path.join(carpeta_base, nombre_archivo)
                
                with open(ruta_archivo, 'w', encoding='utf-8') as f:
                    # Guardar metadatos
                    f.write(f"Fecha de publicación: {fecha}\n")
                    f.write(f"Categoría: {categoria}\n\n")

                    # Escribir el texto del artículo
                    f.write("Texto del artículo:\n")
                    f.write(texto)
                    f.write("\n\n")

                    # Agregar secciones para videos
                    if videos:
                        f.write("Videos:\n")
                        for video in videos:
                            f.write(f"{video}\n")
                        f.write("\n")

                    # Agregar secciones para imágenes
                    if imagenes:
                        f.write("Imágenes:\n")
                        for imagen in imagenes:
                            f.write(f"{imagen}\n")
                        f.write("\n")
                    
                    # Agregar listas si existen
                    if listas:
                        f.write("Listas:\n")
                        for lista in listas:
                            for item in lista:
                                f.write(f"- {item}\n")
                        f.write("\n")

                    # Agregar enlaces internos
                    if enlaces_internos:
                        f.write("Enlaces internos:\n")
                        for enlace in enlaces_internos:
                            f.write(f"{enlace}\n")
                        f.write("\n")
                    
                    # Agregar enlaces externos
                    if enlaces_externos:
                        f.write("Enlaces externos:\n")
                        for enlace in enlaces_externos:
                            f.write(f"{enlace}\n")
                        f.write("\n")

                print(f"Archivo '{nombre_archivo}' creado con éxito en la carpeta 'Base de conocimiento'")
    except Exception as e:
        print(f"Error en ScraperPrincipal: {e}")

# URL principal desde donde comienzas a extraer las carpetas
url_principal = "https://soporte.nasa.com.mx/support/home" 
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

# Crear la carpeta 'Base de conocimiento' si no existe
carpeta_base = "Base de conocimiento"
if not os.path.exists(carpeta_base):
    os.makedirs(carpeta_base)

# Extraer todas las URLs de las carpetas
urls_carpetas = ExtraerURLsCarpetas(url_principal, headers)

# Scraping de los artículos dentro de cada carpeta
for url in urls_carpetas:
    ScraperPrincipal(url, headers, carpeta_base)

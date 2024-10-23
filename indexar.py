import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Cargar el modelo de embeddings
modelo = SentenceTransformer('all-MiniLM-L6-v2')

# Carpeta de embeddings
carpeta_embeddings = "embeddings"  # Ajustar aquí la carpeta correcta
carpeta_BaseConocimmiento = "Base de conocimiento"
# Cargar el índice FAISS
ruta_indice_faiss = os.path.join(carpeta_embeddings, "faiss_index.index")
try:
    index = faiss.read_index(ruta_indice_faiss)
    print("Índice FAISS cargado correctamente.")
except Exception as e:
    print(f"Error al cargar el índice FAISS: {e}")

# Cargar los nombres de los archivos de texto
try:
    nombres_archivos = [f.replace('.npy', '') for f in os.listdir(carpeta_embeddings) if f.endswith('.npy')]
    print("Nombres de archivos de embeddings cargados correctamente.")
except Exception as e:
    print(f"Error al cargar los nombres de archivos de embeddings: {e}")

# Función para obtener el embedding de la pregunta
def obtener_embedding_pregunta(pregunta):
    try:
        embedding = modelo.encode(pregunta, convert_to_numpy=True)
        print("Embedding de la pregunta obtenido correctamente.")
        return embedding
    except Exception as e:
        print(f"Error al obtener el embedding de la pregunta: {e}")
        return None

# Función para recuperar texto basado en el índice
def recuperar_texto_por_indice(indices):
    textos_recuperados = []
    for idx in indices:
        try:
            ruta_texto = os.path.join(carpeta_BaseConocimmiento, f"{nombres_archivos[idx]}")
            with open(ruta_texto, 'r', encoding='utf-8') as file:
                texto = file.read()
            textos_recuperados.append(texto)
            print(f"Texto recuperado de {ruta_texto}.")
        except Exception as e:
            print(f"Error al recuperar el texto de {ruta_texto}: {e}")
    return textos_recuperados

# Interacción con el usuario
while True:
    pregunta = input("¿Cuál es tu pregunta? (o escribe 'salir' para terminar): ")
    if pregunta.lower() == 'salir':
        break

    # Obtener el embedding de la pregunta
    embedding_pregunta = obtener_embedding_pregunta(pregunta)
    if embedding_pregunta is None:
        continue

    # Buscar los K vecinos más cercanos
    k = 5  # Número de textos a recuperar
    try:
        distances, indices = index.search(np.array([embedding_pregunta]), k)
        print("Búsqueda en el índice FAISS realizada correctamente.")
    except Exception as e:
        print(f"Error al buscar en el índice FAISS: {e}")
        continue

    # Recuperar los textos asociados a los índices
    textos_recuperados = recuperar_texto_por_indice(indices[0])

    # Mostrar resultados
    print("Textos recuperados:")
    for i, texto in enumerate(textos_recuperados):
        print(f"{i + 1}: {texto}")

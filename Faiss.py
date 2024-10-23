import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Modelo de embeddings 
modelo = SentenceTransformer('all-MiniLM-L6-v2')

# Carpetas
carpeta_base = "Base de conocimiento"
carpeta_embeddings = "embeddings"

# Crear la carpeta 'embeddings' si no existe
if not os.path.exists(carpeta_embeddings):
    os.makedirs(carpeta_embeddings)

# Función para cargar texto desde archivos .txt
def cargar_textos(carpeta):
    textos = []
    nombres_archivos = []
    
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".txt"):
            ruta_archivo = os.path.join(carpeta, archivo)
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                texto = f.read()
                textos.append(texto)
                nombres_archivos.append(archivo)
    
    return textos, nombres_archivos

# Cargar los textos de la carpeta de base de conocimiento
textos, nombres_archivos = cargar_textos(carpeta_base)

# Aplicar el modelo de embeddings a cada texto
print("Generando embeddings...")
embeddings = modelo.encode(textos, convert_to_numpy=True)

# Crear el índice FAISS
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)  # Indexa usando la métrica de L2 (distancia euclidiana)
index.add(embeddings)  # Agrega los embeddings al índice

# Guardar el índice en la carpeta 'embeddings'
ruta_indice_faiss = os.path.join(carpeta_embeddings, "faiss_index.index")
faiss.write_index(index, ruta_indice_faiss)
print(f"Índice FAISS guardado en: {ruta_indice_faiss}")

# Guardar cada embedding individualmente como archivo .npy
for i, nombre_archivo in enumerate(nombres_archivos):
    ruta_embedding = os.path.join(carpeta_embeddings, f"{nombre_archivo}.npy")
    np.save(ruta_embedding, embeddings[i])
    print(f"Embedding de '{nombre_archivo}' guardado en: {ruta_embedding}")

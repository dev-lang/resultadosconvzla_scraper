import os
import csv
import logging
import requests
from bs4 import BeautifulSoup

# Definir el directorio de guardado como "resultadosconvzla"
SAVE_DIR = os.path.join(os.getcwd(), 'resultadosconvzla')

# Crear la carpeta si no existe
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Configuración de rangos e IDs - MODIFICAR RANGO PARA ABARCAR MAS O MENOS, RECOMIENDO TOMAR DE A RANGOS DE MÁXIMO 100 MIL ACTAS POR CARPETA
START_ID = 10400000
END_ID = 10500000

# Crear el archivo CSV con el nombre dinámico basado en el rango de IDs
CSV_FILE = os.path.join(SAVE_DIR, f'scraping_vzla_{START_ID}-{END_ID}.csv')
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['CEDULA', 'URL', 'ACTA'])  # Cabecera del CSV

# Crear un archivo de log con el nombre dinámico basado en el rango de IDs
LOG_FILE = os.path.join(SAVE_DIR, f'csv_scraping_vzla_{START_ID}-{END_ID}.log')

# Configurar el logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Archivo de log para guardar en el archivo
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)

# Función para guardar las referencias en el CSV
def save_reference_to_csv(id, url, acta):
    try:
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([id, url, acta])  # Guardamos el ID, URL del documento y URL de la imagen
        logger.info(f"Referencia guardada: {id}, {url}, {acta}")
    except Exception as e:
        logger.error(f"Error al guardar la referencia {id}, {url}, {acta}: {e}")

# Función para procesar un ID
def process_id(id):
    url = f'https://resultadosconvzla.com/documento/V{id}'
    logger.info(f"Procesando ID: {id}, URL: {url}")  # Agregamos un log para ver que está procesando

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Si la respuesta es un error, se lanza una excepción
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Intentamos encontrar la imagen en la página
        img_tag = soup.find('div', {'id': 'searchCedula'}).find('img', {'class': 'img-fluid responsive-img'})
        
        # Verificamos si encontramos la URL de la imagen
        if img_tag and 'src' in img_tag.attrs:
            img_url = img_tag['src']
            img_name = f"{id}_{os.path.basename(img_url)}"
            save_path = os.path.join(SAVE_DIR, img_name)
            logger.info(f"Imagen encontrada: {img_url}")
            # Llama a tu función de descarga de imagen (asumimos que tienes una función 'download_image' para esto)
            # download_image(img_url, save_path)  # Si quieres seguir descargando la imagen
            
            # Guardamos la URL de la imagen en el CSV en la columna ACTA
            save_reference_to_csv(id, url, img_url)
        else:
            logger.info(f"No se encontró imagen para el ID: {id}")
            # Si no encontramos imagen, guardamos 'Revisar LOG' en el CSV
            save_reference_to_csv(id, url, 'Revisar LOG')

    except requests.exceptions.RequestException as e:
        logger.error(f"Error al procesar ID {id}: {e}")
    except AttributeError as e:
        logger.error(f"No se encontró 'searchCedula' para el ID {id}. Error: {e}")

# Ejecutar el proceso para el rango de IDs
for id in range(START_ID, END_ID + 1):  # +1 para incluir el END_ID
    process_id(id)

import requests
from bs4 import BeautifulSoup
import os
import concurrent.futures
import logging
import random
import time
from tenacity import retry, wait_random, stop_after_attempt
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configuración de rangos e IDs - MODIFICAR RANGO PARA ABARCAR MAS O MENOS, RECOMIENDO TOMAR DE A RANGOS DE MÁXIMO 100 MIL ACTAS POR CARPETA
START_ID = 10400000
END_ID = 10500000

# Configuración del registro (logging)
log_file = f'scraping_vzla_{START_ID}-{END_ID}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Lista de User-Agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
]

# Configuración de sesión con retries
session = requests.Session()
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504, 403],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# Crear carpeta para guardar las imágenes
SAVE_DIR = f'resultadosconvzla_{START_ID}-{END_ID}'
os.makedirs(SAVE_DIR, exist_ok=True)

# Generar headers aleatorios
def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }

# Descargar imagen
@retry(wait=wait_random(min=1, max=3), stop=stop_after_attempt(5))
def download_image(url, save_path):
    try:
        response = session.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        logger.info(f"Imagen descargada: {save_path}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al descargar {url}: {e}")
        raise

'''# Procesar un ID
def process_id(id):
    url = f'https://resultadosconvzla.com/documento/V{id}'
    try:
        response = session.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = soup.find('div', {'id': 'searchCedula'}).find('img', {'class': 'img-fluid responsive-img'})
        
        if img_tag and 'src' in img_tag.attrs:
            img_url = img_tag['src']
            img_name = f"{id}_{os.path.basename(img_url)}"
            save_path = os.path.join(SAVE_DIR, img_name)
            download_image(img_url, save_path)
        else:
            logger.info(f"No se encontró imagen para el ID: {id}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al procesar ID {id}: {e}")'''

'''# Procesar un ID
def process_id(id):
    url = f'https://resultadosconvzla.com/documento/V{id}'
    try:
        # Realizar solicitud al sitio web
        response = session.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        
        # Parsear contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = soup.find('div', {'id': 'searchCedula'}).find('img', {'class': 'img-fluid responsive-img'})
        
        # Validar si se encuentra la etiqueta de imagen
        if img_tag and 'src' in img_tag.attrs:
            img_url = img_tag['src']
            img_name = f"{id}_{os.path.basename(img_url)}"
            
            # Validar y construir ruta para guardar la imagen
            if not os.path.exists(SAVE_DIR):
                os.makedirs(SAVE_DIR, exist_ok=True)
            save_path = os.path.join(SAVE_DIR, img_name)
            
            # Descargar la imagen
            download_image(img_url, save_path)
        else:
            logger.info(f"No se encontró imagen para el ID: {id}")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión o HTTP al procesar ID {id}: {e}")
    
    except AttributeError as e:
        logger.error(f"Error al parsear HTML para ID {id}: {e}")
    
    except Exception as e:
        logger.exception(f"Error inesperado procesando ID {id}: {e}")'''

# Procesar un ID
def process_id(id):
    url = f'https://resultadosconvzla.com/documento/V{id}'
    try:
        # Realizar solicitud al sitio web
        response = session.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        
        # Parsear contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Verificar si aparece un error en la página
        error_container = soup.find('div', {'class': 'error-container'})
        if error_container:
            logger.error(f"Error 404 al procesar ID {id}: No se encontró la imagen debido a un error en la página.")
            return
        
        # Buscar el contenedor de la imagen
        search_cedula = soup.find('div', {'id': 'searchCedula'})
        if not search_cedula:
            logger.error(f"No se encontró el contenedor 'searchCedula' para ID {id}. Puede no existir.")
            return
        
        # Buscar la imagen dentro del contenedor
        img_tag = search_cedula.find('img', {'class': 'img-fluid responsive-img'})
        if img_tag and 'src' in img_tag.attrs:
            img_url = img_tag['src']
            img_name = f"{id}_{os.path.basename(img_url)}"
            
            # Validar y construir ruta para guardar la imagen
            if not os.path.exists(SAVE_DIR):
                os.makedirs(SAVE_DIR, exist_ok=True)
            save_path = os.path.join(SAVE_DIR, img_name)
            
            # Descargar la imagen
            download_image(img_url, save_path)
        else:
            logger.info(f"No se encontró imagen dentro del contenedor 'searchCedula' para ID: {id}")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión o HTTP al procesar ID {id}: {e}")
    
    except AttributeError as e:
        logger.error(f"Error al parsear HTML para ID {id}: {e}")
    
    except Exception as e:
        logger.exception(f"Error inesperado procesando ID {id}: {e}")


# Ejecutar en paralelo
def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_id, id): id for id in range(START_ID, END_ID + 1)}
        for future in concurrent.futures.as_completed(futures):
            id = futures[future]
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error procesando ID {id}: {e}")

if __name__ == "__main__":
    main()

import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno desde archivo .env si existe
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Configuracion:
    """Configuración centralizada de la aplicación"""
    
    # Configuración de la base de datos
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vuelos.db")
    
    # Configuración del servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Configuración de tiempos de espera para vuelos
    TIEMPO_ESPERA_NORMAL = int(os.getenv("TIEMPO_ESPERA_NORMAL", "30"))  # minutos
    TIEMPO_ESPERA_EMERGENCIA = int(os.getenv("TIEMPO_ESPERA_EMERGENCIA", "5"))  # minutos
    
    # Límites de la API
    MAX_VUELOS_POR_PAGINA = int(os.getenv("MAX_VUELOS_POR_PAGINA", "100"))
    
    # Códigos de estados permitidos
    ESTADOS_VUELO = [
        "programado",
        "abordando", 
        "despegado", 
        "retrasado", 
        "cancelado"
    ]
    
    # Ubicación de logs
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "vuelos.log")

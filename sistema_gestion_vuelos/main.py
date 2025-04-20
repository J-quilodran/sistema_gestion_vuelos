import uvicorn
import logging
from configuracion import Configuracion

# Configurar logging
logging.basicConfig(
    level=getattr(logging, Configuracion.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=Configuracion.LOG_FILE if Configuracion.LOG_LEVEL != "DEBUG" else None
)

logger = logging.getLogger("vuelos_app")

def main():
    """Función principal para iniciar la aplicación"""
    logger.info("Iniciando aplicación de gestión de vuelos...")
    
    try:
        uvicorn.run(
            "api:app", 
            host=Configuracion.HOST, 
            port=Configuracion.PORT, 
            reload=Configuracion.DEBUG
        )
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {e}")
        raise

if __name__ == "__main__":
    main()
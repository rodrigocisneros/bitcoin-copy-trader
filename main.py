# main.py
import logging
from monitor import monitor_account
from config import BITCOIN_ADDRESS


# Configuración global del logging para mostrar en consola
logging.basicConfig(
    level=logging.INFO,  # Nivel mínimo de logs a mostrar
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato del log
    handlers=[
        logging.StreamHandler()  # Asegura que los logs se impriman en la consola
    ]
)

def main():
    
    try:
        monitor_account(BITCOIN_ADDRESS)
    except KeyboardInterrupt:
        logging.info("Monitoreo detenido manualmente.")

if __name__ == "__main__":
    main()

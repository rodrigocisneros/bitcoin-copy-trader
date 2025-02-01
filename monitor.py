# monitor.py
import requests
import time
import logging
from datetime import datetime, timedelta
from db_supabase import is_tx_replicated, store_tx
from trade import replicar_operacion
from config import BITCOIN_ADDRESS, POLL_INTERVAL

def fetch_address_transactions(address):
    """
    Consulta la API de BlockCypher para obtener las transacciones recientes de la dirección.
    Se consideran las transacciones confirmadas (campo 'txrefs').
    """
    url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}?limit=50"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("txrefs", [])
    except requests.RequestException as e:
        logging.error("Error al obtener transacciones: %s", e)
        return []

def interpretar_operacion(tx, address):
    """
    Interpreta la transacción 'tx' para determinar si se debe replicar una operación completa.
    
    Se define un umbral de 50 BTC (en satoshis):
      - Si la wallet recibe (compra) 50 BTC o más, se devuelve ("compra", "full").
      - Si la wallet envía (vende) 50 BTC o más, se devuelve ("venta", "full").
      - En caso contrario, no se replica.
    """
    value = tx.get("value", 0)
    threshold = 50 * 100_000_000  # 50 BTC en satoshis
    if value > 0:
        if value >= threshold:
            return "compra", "full"
        else:
            return None, None
    else:
        if abs(value) >= threshold:
            return "venta", "full"
        else:
            return None, None

def monitor_account(address):
    """
    Monitorea la dirección Bitcoin y, para cada transacción confirmada en el último día
    que no haya sido replicada, interpreta la operación y la replica.
    """
    logging.info("Iniciando monitoreo de la dirección: %s", address)
    
    while True:
        transactions = fetch_address_transactions(address)
        now_utc = datetime.utcnow()
        cutoff_time = now_utc - timedelta(days=1)

        for tx in transactions:
            tx_hash = tx.get("tx_hash")
            if not tx_hash:
                continue
            confirmed_str = tx.get("confirmed")
            if not confirmed_str:
                continue  # Omitir las transacciones no confirmadas
            try:
                confirmed_dt = datetime.strptime(confirmed_str, "%Y-%m-%dT%H:%M:%SZ")
            except Exception as e:
                logging.error("Error al parsear la fecha de la tx %s: %s", tx_hash, e)
                continue
            if confirmed_dt < cutoff_time:
                continue  # Transacción anterior a 24 horas
            logging.info("Procesando transacción: %s", tx)
            if is_tx_replicated(tx_hash):
                continue  # Transacción ya replicada
            tipo, valor = interpretar_operacion(tx, address)
            if tipo is None:
                continue
            logging.info("Tx %s interpretada como %s con valor %s", tx_hash, tipo, valor)
            replicar_operacion(tipo, valor)
            store_tx(tx_hash)
        logging.info("Esperando %d segundos para la siguiente consulta...", POLL_INTERVAL)
        time.sleep(POLL_INTERVAL)

# db_supabase.py
import logging
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def is_tx_replicated(tx_hash: str) -> bool:
    """Verifica si una transacción ya fue replicada consultando la tabla 'replicated_txs' en Supabase."""
    try:
        print("Comprobando si la transaccion está replicada en Supabase")
        response = supabase.table("replicated_txs").select("*").eq("tx_hash", tx_hash).execute()
        return bool(response.data and len(response.data) > 0)
    except Exception as e:
        logging.error("Error al consultar la tx replicada en Supabase: %s", e)
        return False

def store_tx(tx_hash: str) -> None:
    """Guarda el hash de la transacción en la tabla 'replicated_txs' de Supabase."""
    try:
        data = {"tx_hash": tx_hash}
        supabase.table("replicated_txs").insert(data).execute()
        logging.info("Transacción %s almacenada en Supabase (replicated_txs).", tx_hash)
    except Exception as e:
        logging.error("Error al almacenar la tx %s en Supabase: %s", tx_hash, e)

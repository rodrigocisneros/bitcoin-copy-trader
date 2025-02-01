# trade.py
import requests
import logging
from datetime import datetime
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, INITIAL_BTC, INITIAL_USDT

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_btc_usdt_price():
    """
    Obtiene el precio actual de BTC en USDT desde la API de CoinGecko.
    Retorna el precio como float o None en caso de error.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data["bitcoin"]["usd"])
    except Exception as e:
        logging.error("Error obteniendo el precio BTC/USDT: %s", e)
        return None

def get_current_wallet_state():
    """
    Consulta la tabla 'my_wallet' en Supabase para obtener el balance actual.
    Si no hay registros previos, retorna los valores iniciales.
    """
    try:
        response = supabase.table("my_wallet").select("*").order("id", desc=True).limit(1).execute()
        if response.data:
            last_trade = response.data[0]
            btc_balance = float(last_trade.get("new_btc_balance", INITIAL_BTC))
            usdt_balance = float(last_trade.get("new_usdt_balance", INITIAL_USDT))
        else:
            btc_balance = INITIAL_BTC
            usdt_balance = INITIAL_USDT
        return btc_balance, usdt_balance
    except Exception as e:
        logging.error("Error obteniendo el estado actual de la wallet: %s", e)
        return INITIAL_BTC, INITIAL_USDT

def simulate_trade(operation, btc_amount):
    """
    Simula la ejecución de la operación de copy trade:
      - Obtiene el precio actual BTC/USDT.
      - Calcula el costo (para COMPRA) o ingreso (para VENTA).
      - Verifica fondos disponibles y actualiza la tabla 'my_wallet' en Supabase.
    """
    price = get_btc_usdt_price()
    if price is None:
        logging.error("No se pudo obtener el precio para simular la operación.")
        return

    current_btc, current_usdt = get_current_wallet_state()

    if operation == "compra":
        cost = btc_amount * price
        if current_usdt < cost:
            logging.warning("Fondos insuficientes para COMPRA: USDT disponibles: %.2f, costo requerido: %.2f", current_usdt, cost)
            return
        new_btc = current_btc + btc_amount
        new_usdt = current_usdt - cost
        logging.info("Simulación COMPRA: Se compraron %.8f BTC a precio %.2f USDT (costo: %.2f USDT)", btc_amount, price, cost)
    elif operation == "venta":
        if current_btc < btc_amount:
            logging.warning("Fondos insuficientes para VENTA: BTC disponibles: %.8f, requeridos: %.8f", current_btc, btc_amount)
            return
        revenue = btc_amount * price
        new_btc = current_btc - btc_amount
        new_usdt = current_usdt + revenue
        logging.info("Simulación VENTA: Se vendieron %.8f BTC a precio %.2f USDT (ingreso: %.2f USDT)", btc_amount, price, revenue)
    else:
        logging.warning("Operación desconocida: %s", operation)
        return

    trade_data = {
        "operation": operation,
        "btc_amount": btc_amount,
        "price": price,
        "usdt_amount": btc_amount * price,  # Costo (compra) o ingreso (venta)
        "new_btc_balance": new_btc,
        "new_usdt_balance": new_usdt,
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        supabase.table("my_wallet").insert(trade_data).execute()
        logging.info("Operación simulada almacenada en my_wallet: %s", trade_data)
    except Exception as e:
        logging.error("Error al almacenar la operación en my_wallet: %s", e)

def replicar_operacion(tipo, valor):
    """
    Replica la operación detectada.
      - Si 'valor' es "full", se ejecuta la operación completa:
          • Para COMPRA: se usa todo el USDT disponible para comprar BTC.
          • Para VENTA: se venden todos los BTC disponibles.
      - Si 'valor' es numérico (en satoshis), se convierte a BTC.
    """
    if valor == "full":
        current_btc, current_usdt = get_current_wallet_state()
        if tipo == "compra":
            price = get_btc_usdt_price()
            if price is None:
                logging.error("No se pudo obtener el precio para replicar la COMPRA completa.")
                return
            btc_amount = current_usdt / price
        elif tipo == "venta":
            btc_amount = current_btc
        else:
            logging.warning("Operación desconocida: %s", tipo)
            return
    else:
        btc_amount = valor / 1e8  # Conversión de satoshis a BTC
    simulate_trade(tipo, btc_amount)

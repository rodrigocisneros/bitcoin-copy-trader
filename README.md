Este proyecto es un bot de trading automatizado que monitorea una dirección de Bitcoin y replica sus transacciones en una cuenta simulada en Supabase.

📌 Lógica del Copy Trading:

Si la dirección monitoreada vende más de 50 BTC, el bot vende todos los BTC disponibles en la cuenta simulada.
Si la dirección monitoreada compra más de 50 BTC, el bot usa todos los USDT disponibles para comprar BTC.
El bot consulta el precio en tiempo real de BTC/USDT a través de la API de CoinGecko.
Las operaciones simuladas se almacenan en Supabase en la tabla my_wallet.
Se evita replicar la misma transacción usando la tabla replicated_txs en Supabase.
📌 Tabla de Contenidos
🚀 Instalación
⚙️ Configuración
🔄 Flujo de Trabajo
🛠️ Ejecución
📡 Despliegue en la Nube (Railway)
🧪 Pruebas
📜 Licencia
🚀 Instalación
1️⃣ Clonar el repositorio

bash
Copiar
Editar
git clone https://github.com/tu-usuario/bitcoin-copy-trader.git
cd bitcoin-copy-trader
2️⃣ Crear un entorno virtual y activarlo

bash
Copiar
Editar
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
3️⃣ Instalar dependencias

bash
Copiar
Editar
pip install -r requirements.txt
⚙️ Configuración
Antes de ejecutar el bot, necesitas configurar las variables de entorno y las tablas en Supabase.

1️⃣ Configurar variables de entorno
Crea un archivo .env en la raíz del proyecto y añade lo siguiente:

ini
Copiar
Editar
# Supabase Config
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-supabase-key

# Bitcoin Address a Monitorear
BITCOIN_ADDRESS=1BoatSLRHtKNngkdXEeobR76b53LETtpyT

# Intervalo de consulta en segundos
POLL_INTERVAL=60

# Valores iniciales para la simulación
INITIAL_BTC=0.0
INITIAL_USDT=1000.0
✨ Nota: Reemplaza your-project-ref y your-supabase-key con tus credenciales reales de Supabase.

2️⃣ Crear las tablas en Supabase
Ejecuta estos comandos en la consola SQL de Supabase para crear las tablas necesarias.

📌 Tabla replicated_txs (Para evitar duplicados)
sql
Copiar
Editar
CREATE TABLE replicated_txs (
  id SERIAL PRIMARY KEY,
  tx_hash TEXT UNIQUE NOT NULL,
  replicated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now())
);
📌 Tabla my_wallet (Para simular las operaciones)
sql
Copiar
Editar
CREATE TABLE my_wallet (
  id SERIAL PRIMARY KEY,
  operation TEXT NOT NULL,  -- "compra" o "venta"
  btc_amount NUMERIC NOT NULL,
  price NUMERIC NOT NULL,  -- Precio BTC/USDT en el momento de la transacción
  usdt_amount NUMERIC NOT NULL,  -- Monto en USDT usado o recibido
  new_btc_balance NUMERIC NOT NULL,
  new_usdt_balance NUMERIC NOT NULL,
  timestamp TIMESTAMPTZ DEFAULT timezone('utc', now())
);
🔄 Flujo de Trabajo
1️⃣ El bot consulta la API de BlockCypher para monitorear las transacciones de la dirección Bitcoin.
2️⃣ Si detecta una transacción con 50 BTC o más, interpreta la operación como una compra o venta.
3️⃣ Se verifica en Supabase si la transacción ya fue replicada.
4️⃣ Si es una transacción válida y nueva, se ejecuta una simulación de trading:

Se obtiene el precio de BTC/USDT desde CoinGecko.
Se actualiza el balance en la tabla my_wallet de Supabase.
Se registra la transacción en replicated_txs para evitar duplicados.
🛠️ Ejecución
Para iniciar el bot localmente, ejecuta:

bash
Copiar
Editar
python main.py
Para detenerlo, usa:

bash
Copiar
Editar
CTRL + C

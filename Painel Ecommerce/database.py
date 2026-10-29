import sqlite3
import oracledb
import os
import json
from dotenv import load_dotenv

load_dotenv()

DB_FILE = "ecommerce-state.db"

# ==========================================
# 1. SIDECAR (SQLITE) - ESTADOS E NOTAS
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS OrderStates (
            order_id TEXT PRIMARY KEY,
            is_separated BOOLEAN DEFAULT 0,
            notes TEXT
        )
    ''')
    try:
        cursor.execute("ALTER TABLE OrderStates ADD COLUMN separator_name TEXT")
        cursor.execute("ALTER TABLE OrderStates ADD COLUMN separated_by_user TEXT")
        cursor.execute("ALTER TABLE OrderStates ADD COLUMN separated_at TEXT")
    except sqlite3.OperationalError:
        pass 
        
    conn.commit()
    conn.close()

def toggle_separation(order_id: str, current_state: bool, separator_name: str = "", separated_by_user: str = "", separated_at: str = ""):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    new_state = 0 if current_state else 1
    
    if new_state == 1:
        cursor.execute('''
            INSERT INTO OrderStates (order_id, is_separated, separator_name, separated_by_user, separated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(order_id)
            DO UPDATE SET is_separated = excluded.is_separated,
                          separator_name = excluded.separator_name,
                          separated_by_user = excluded.separated_by_user,
                          separated_at = excluded.separated_at
        ''', (order_id, new_state, separator_name, separated_by_user, separated_at))
    else:
        cursor.execute('''
            INSERT INTO OrderStates (order_id, is_separated, separator_name, separated_by_user, separated_at)
            VALUES (?, ?, '', '', '')
            ON CONFLICT(order_id)
            DO UPDATE SET is_separated = excluded.is_separated,
                          separator_name = '',
                          separated_by_user = '',
                          separated_at = ''
        ''', (order_id, new_state))
        
    conn.commit()
    conn.close()
    return new_state

def save_order_notes(order_id: str, notes_json: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO OrderStates (order_id, notes)
        VALUES (?, ?)
        ON CONFLICT(order_id)
        DO UPDATE SET notes = excluded.notes
    ''', (order_id, notes_json))
    conn.commit()
    conn.close()

# ==========================================
# 2. ERP (ORACLE) - PEDIDOS REAIS E ITENS
# ==========================================
def map_order_status(posicao):
    status_map = {
        'L': 'Em Separação',
        'F': 'Faturado',
        'C': 'Cancelado',
        'M': 'Montado',
        'P': 'Pendente',
        'B': 'Bloqueado'
    }
    return status_map.get(posicao, 'Indefinido')

async def get_orders_hybrid():
    conn_sq = sqlite3.connect(DB_FILE)
    conn_sq.row_factory = sqlite3.Row
    cursor = conn_sq.cursor()
    cursor.execute("SELECT * FROM OrderStates")
    local_states = {str(row["order_id"]): dict(row) for row in cursor.fetchall()}
    conn_sq.close()

    try:
        oracle_dsn = f"{os.getenv('ORACLE_HOST')}:{os.getenv('ORACLE_PORT')}/{os.getenv('ORACLE_SERVICE_NAME')}"
        conn_or = await oracledb.connect_async(
            user=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=oracle_dsn
        )
        
        sql = """
            SELECT 
                TO_CHAR(P.DATA, 'DD/MM/YYYY') AS DATA, 
                TO_CHAR(P.DTFAT, 'DD/MM/YYYY') AS DTFAT,
                P.NUMPED AS PEDIDO, 
                P.POSICAO, 
                C.CLIENTE, 
                NVL(P.NUMVIASMAPASEP, 0) AS VIAS 
            FROM PCPEDC P 
            INNER JOIN PCCLIENT C ON P.CODCLI = C.CODCLI 
            WHERE P.ORIGEMPED = 'W' 
                AND P.CONDVENDA = 1 
                AND P.VENDAASSISTIDA = 'N' 
                AND P.POSICAO IN ('F', 'C', 'L', 'M', 'P', 'B') 
                AND P.DATA BETWEEN TRUNC(SYSDATE) - 60 AND TRUNC(SYSDATE)
            ORDER BY P.DATA DESC, P.NUMPED DESC
        """
        
        cursor_or = conn_or.cursor()
        await cursor_or.execute(sql)
        oracle_rows = await cursor_or.fetchall()
        
        columns = [col[0] for col in cursor_or.description]
        cursor_or.close()
        await conn_or.close()
        
        final_orders = []
        for row in oracle_rows:
            order_data = dict(zip(columns, row))
            pedido_id = str(order_data["PEDIDO"])
            
            state = local_states.get(pedido_id, {"is_separated": 0, "notes": "[]"})
            
            notes_raw = state.get("notes", "[]")
            try:
                notes_parsed = json.loads(notes_raw) if notes_raw else []
            except:
                notes_parsed = []
            
            final_orders.append({
                "data": order_data["DATA"],
                "dtfat": order_data.get("DTFAT") or "",
                "pedido": pedido_id,
                "cliente": order_data["CLIENTE"],
                "vias": order_data["VIAS"],
                "status_erp": map_order_status(order_data["POSICAO"]),
                "is_separated": bool(state.get("is_separated", 0)),
                "separator_name": state.get("separator_name", "") or "",
                "separated_by_user": state.get("separated_by_user", "") or "",
                "separated_at": state.get("separated_at", "") or "",
                "notes": notes_parsed
            })
            
        return final_orders

    except Exception as e:
        print(f"❌ Erro crítico na conexão Oracle: {e}")
        return []

async def get_order_items(order_id: str):
    try:
        oracle_dsn = f"{os.getenv('ORACLE_HOST')}:{os.getenv('ORACLE_PORT')}/{os.getenv('ORACLE_SERVICE_NAME')}"
        conn_or = await oracledb.connect_async(
            user=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=oracle_dsn
        )
        
        sql = """
            SELECT 
                I.CODPROD,
                P.DESCRICAO,
                I.QT
            FROM PCPEDI I
            INNER JOIN PCPRODUT P ON I.CODPROD = P.CODPROD
            WHERE I.NUMPED = :pedido
            ORDER BY I.NUMSEQ
        """
        
        cursor_or = conn_or.cursor()
        await cursor_or.execute(sql, pedido=order_id)
        rows = await cursor_or.fetchall()
        
        items = []
        for row in rows:
            items.append({
                "codigo": row[0],
                "descricao": row[1],
                "quantidade": row[2]
            })
            
        cursor_or.close()
        await conn_or.close()
        return items
        
    except Exception as e:
        print(f"❌ Erro ao buscar itens do pedido {order_id}: {e}")
        return []

# ==========================================
# 3. AUTENTICAÇÃO (ORACLE) - WINTHOR
# ==========================================
async def authenticate_user(username: str, password: str):
    try:
        oracle_dsn = f"{os.getenv('ORACLE_HOST')}:{os.getenv('ORACLE_PORT')}/{os.getenv('ORACLE_SERVICE_NAME')}"
        conn = await oracledb.connect_async(
            user=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=oracle_dsn
        )
        
        # Função de descriptografia lida via variável de ambiente para não expor o schema no repositório público
        decrypt_fn = os.getenv("ORACLE_DECRYPT_FUNC", "DECRYPT")
        
        sql = f"""
            SELECT P.MATRICULA, P.NOME_GUERRA, P.CODSETOR, S.DESCRICAO AS SETOR, {decrypt_fn}(P.SENHABD, P.USUARIOBD) AS SENHA_DECRYPT
            FROM PCEMPR P INNER JOIN PCSETOR S ON S.CODSETOR = P.CODSETOR
            WHERE TO_CHAR(P.MATRICULA) = :user_val OR UPPER(P.NOME_GUERRA) = UPPER(:user_val)
        """
        
        cursor = conn.cursor()
        await cursor.execute(sql, user_val=str(username).strip())
        row = await cursor.fetchone()
        cursor.close()
        await conn.close()
        
        if not row: return None
            
        senha_decrypt = str(row[4] or '').strip().upper()
        pass_input = str(password or '').strip().upper()
        
        if senha_decrypt == pass_input:
            return {"matricula": row[0], "nome": row[1], "codSetor": row[2], "setor": row[3]}
            
        return None
    except Exception as e:
        print(f"❌ Erro na autenticação Oracle: {e}")
        return None

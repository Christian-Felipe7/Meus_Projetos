import sqlite3
import oracledb
import os
import json
from dotenv import load_dotenv

load_dotenv()

DB_FILE = "ecommerce-state.db"

# ==========================================
# 1. SIDE CAR (SQLITE) - ESTADOS E NOTAS
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
    # Integração híbrida:

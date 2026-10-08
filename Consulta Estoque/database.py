import sqlite3

DB_NAME = "banco_de_dados.db"

def init_db():
    """Cria o banco de dados e as tabelas se não existirem."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Exemplo de criação de uma tabela simples
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")

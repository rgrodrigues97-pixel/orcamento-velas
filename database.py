import sqlite3
from typing import List, Dict, Any, Optional

DB_NAME = "sistema_velas.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria as tabelas necessárias e inicializa os parâmetros se estiverem vazios."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Tabela de Clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                contato TEXT
            )
        """)

        # 2. Tabela de Produtos (Ficha técnica e mão de obra)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                valor_mao_de_obra REAL NOT NULL,
                cera_kg_unitario REAL NOT NULL,
                pavio_m_unitario REAL NOT NULL
            )
        """)

        # 3. Tabela de Parâmetros de Insumos (Preços de referência)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config_insumos (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                preco_kg_cera REAL NOT NULL,
                preco_metro_pavio REAL NOT NULL
            )
        """)

        # Insere valores padrão de insumos caso a tabela esteja vazia
        cursor.execute("SELECT COUNT(*) FROM config_insumos")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO config_insumos (id, preco_kg_cera, preco_metro_pavio)
                VALUES (1, 38.00, 0.80)
            """)

        conn.commit()


# --- Operações de Clientes ---

def listar_clientes() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, contato FROM clientes ORDER BY nome ASC")
        return [dict(row) for row in cursor.fetchall()]


def adicionar_cliente(nome: str, contato: str = ""):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clientes (nome, contato) VALUES (?, ?)",
            (nome.strip(), contato.strip()),
        )
        conn.commit()


def excluir_cliente(cliente_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()


# --- Operações de Produtos ---

def listar_produtos() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, valor_mao_de_obra, cera_kg_unitario, pavio_m_unitario FROM produtos ORDER BY nome ASC")
        return [dict(row) for row in cursor.fetchall()]


def obter_produto_por_id(produto_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, valor_mao_de_obra, cera_kg_unitario, pavio_m_unitario FROM produtos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def adicionar_produto(nome: str, valor_mao_de_obra: float, cera_kg_unitario: float, pavio_m_unitario: float):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO produtos (nome, valor_mao_de_obra, cera_kg_unitario, pavio_m_unitario)
            VALUES (?, ?, ?, ?)
            """,
            (nome.strip(), valor_mao_de_obra, cera_kg_unitario, pavio_m_unitario),
        )
        conn.commit()


def excluir_produto(produto_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        conn.commit()


# --- Operações de Configuração de Insumos ---

def obter_config_insumos() -> Dict[str, float]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT preco_kg_cera, preco_metro_pavio FROM config_insumos WHERE id = 1")
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {"preco_kg_cera": 38.00, "preco_metro_pavio": 0.80}


def atualizar_config_insumos(preco_kg_cera: float, preco_metro_pavio: float):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE config_insumos
            SET preco_kg_cera = ?, preco_metro_pavio = ?
            WHERE id = 1
            """,
            (preco_kg_cera, preco_metro_pavio),
        )
        conn.commit()
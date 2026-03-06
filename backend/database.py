import sqlite3

DB_PATH = "dofus_craft.db"

def get_connection():
    """Retorna uma conexão com o banco de dados."""
    return sqlite3.connect(DB_PATH)

def init_database():
    """
    Cria a conexão com o banco de dados.
    Cria as tabelas caso ainda não existam.
    Deve ser chamada uma vez na inicialização do servidor.
    """

    with get_connection() as conn:
        cursor = conn.cursor()

        #Tabela de itens: Armazena QUALQUER item, seja craftável ou ingrediente.
        #Um item pode aparecer nos dois papéis ao mesmo tempo.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id          INTEGER PRIMARY KEY,   -- ID do item na API do DofusDB
                name        TEXT NOT NULL,         -- Nome original Ex:"Maníaco menor"
                name_search TEXT NOT NULL,         -- Nome normalizadp Ex:"maniaco menor"
                level       INTEGER NOT NULL,
                price       INTEGER NOT NULL,      -- Preço retornado pela API (pode estar desatualizado)
                has_recipe  BOOLEAN NOT NULL
            )
        """)

        # Tabela de ingredientes de receita.
        # Cada linha representa UM ingrediente de UM item craftável.
        # Exemplo: se "Espada X" usa 3 ingredientes → 3 linhas com item_id = <id da Espada X>
        #
        # ingredient_id é FK para items.id — o ingrediente também é um item na mesma tabela.
        # Isso permite reaproveitar dados já cacheados e consultar o preço do ingrediente
        # via JOIN, sem precisar de colunas extras aqui.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id         INTEGER NOT NULL,  -- FK: o item craftável
                ingredient_id   INTEGER NOT NULL,  -- FK: o item usado como ingrediente
                quantities        INTEGER NOT NULL,  -- Quantidade necessária na receita
                FOREIGN KEY (item_id)       REFERENCES items(id),
                FOREIGN KEY (ingredient_id) REFERENCES items(id),
                UNIQUE (item_id, ingredient_id)    -- Evita duplicatas dentro da mesma receita
            )
        """)

        conn.commit()
    print("[DB] Banco de dados iniciado.")

# ─────────────────────────────────────────────
#  LEITURA
# ─────────────────────────────────────────────

def get_item_by_id(item_id: int) -> dict | None:
    """
    Busca um item no cache pelo ID.
    Retorna um dict com os dados do item e a lista de ingredientes (com preço de cada um).
    Retorna None se o item não estiver em cache.
    """
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()

        if item is None:
            return None

        result = dict(item)

        # Busca ingredientes com JOIN para trazer nome e preço de cada um.
        # O preço do ingrediente vem da tabela items — mesmo campo usado para qualquer item.
        if result["has_recipe"]:
            cursor.execute("""
                SELECT
                    ri.ingredient_id,
                    ri.quantities,
                    i.name  AS ingredient_name,
                    i.price AS ingredient_price
                FROM recipe_ingredients ri
                JOIN items i ON i.id = ri.ingredient_id
                WHERE ri.item_id = ?
            """, (item_id,))
            result["ingredients"] = [dict(row) for row in cursor.fetchall()]
        else:
            result["ingredients"] = []

        return result
    
def get_item_by_name_search(name_search: str) -> dict | None:

    """
    Busca um item no cache pelo nome (busca exata).
    Reutiliza get_item_by_id para não duplicar lógica.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM items WHERE name_search = ?", (name_search,))
        row = cursor.fetchone()

    if row is None:
        return None

    return get_item_by_id(row[0])

def is_item_cached_by_item_id(item_id: int) -> bool:
    """Verifica rapidamente se o item já existe no banco."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM items WHERE id = ?", (item_id,))
        return cursor.fetchone() is not None

def is_item_cached_by_name_search(name_search: str) -> bool:
    """Verifica rapidamente se o item já existe no banco."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM items WHERE name_search = ?", (name_search,))
        return cursor.fetchone() is not None
    
def get_igredient_by_item_id(item_id = int)-> list[dict]| None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ingredient_id, quantities FROM recipe_ingredients WHERE item_id = ?", (item_id, ))
        rows = cursor.fetchall()

        if rows is None:
            return None
        
        return [{"ingredient_id": row[0], "quantities": row[1]} for row in rows]

# ─────────────────────────────────────────────
#  ESCRITA
# ─────────────────────────────────────────────

def save_item(item_id: int, name: str, name_search: str, level: int, price: int, has_recipe: bool):
    """
    Salva um item no cache.
    Usa INSERT OR IGNORE para não duplicar caso o item já exista.
    Funciona tanto para itens craftáveis quanto para ingredientes simples.
    """
    with get_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO items (id, name, name_search, level, price, has_recipe)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item_id, name, name_search, level, price, int(has_recipe)))
        conn.commit()
    print(f"[DB] Item salvo: {name} (id={item_id})")


def save_ingredients(item_id: int, ingredients: list[dict]):
    """
    Salva os ingredientes de uma receita na tabela recipe_ingredients.
    IMPORTANTE: cada ingrediente já deve estar salvo em 'items' antes desta chamada,
    pois ingredient_id é FK para items.id.

    Formato esperado:
        ingredients = [
            {"ingredient_id": 123, "quantities": 5},
            {"ingredient_id": 456, "quantities": 2},
        ]
    """
    with get_connection() as conn:
        conn.executemany("""
            INSERT OR IGNORE INTO recipe_ingredients (item_id, ingredient_id, quantities)
            VALUES (:item_id, :ingredient_id, :quantities)
        """, [
            {
                "item_id":       item_id,
                "ingredient_id": i["ingredient_id"],
                "quantities":      i["quantities"],
            }
            for i in ingredients
        ])
        conn.commit()
    print(f"[DB] {len(ingredients)} ingrediente(s) salvos para item_id={item_id}")
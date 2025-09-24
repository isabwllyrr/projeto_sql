import pandas as pd
import mysql.connector
import unicodedata
import math

# --- Função para normalizar texto ---
def normalize(text):
    text = str(text).strip()  # remove espaços extras
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')  # remove acentos
    return text.lower()

# --- Função para tratar NaN ---
def fix_nan(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    return value

# --- Carregar CSVs ---
df_marcas = pd.read_csv("../dados/marcas_ofc.csv", sep=';', encoding='utf-8-sig')
df_marcas.columns = df_marcas.columns.str.strip()
df_marcas['brand_norm'] = df_marcas['brand'].apply(normalize)

df_produtos = pd.read_csv("../dados/produtos_ofc.csv", sep=';', encoding='utf-8-sig')
df_produtos.columns = df_produtos.columns.str.strip()
df_produtos['brand_norm'] = df_produtos['brand'].apply(normalize)

# --- Mapear marcas existentes ---
brand_map = dict(zip(df_marcas['brand_norm'], df_marcas['Id']))

# --- Conexão MySQL ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="36353658",  # senha do banco
    database="ecommerce_db"
)
cursor = conn.cursor()

# --- Inserir marcas ---
for _, row in df_marcas.iterrows():
    cursor.execute("""
        INSERT IGNORE INTO marcas (marca_id, nome_marca)
        VALUES (%s, %s)
    """, (fix_nan(row['Id']), normalize(row['brand'])))

# Atualizar o mapa
brand_map = dict(zip(df_marcas['brand_norm'], df_marcas['Id']))

# --- Inserir produtos ---
for _, row in df_produtos.iterrows():
    brand_norm = row['brand_norm']
    brand_id = brand_map.get(brand_norm)

    if brand_id is None:
        # Criar nova marca automaticamente
        cursor.execute("SELECT MAX(marca_id) FROM marcas")
        max_id = cursor.fetchone()[0] or 0
        brand_id = max_id + 1

        cursor.execute(
            "INSERT INTO marcas (marca_id, nome_marca) VALUES (%s, %s)",
            (brand_id, fix_nan(row['brand']))
        )
        brand_map[brand_norm] = brand_id

    cursor.execute("""
        INSERT IGNORE INTO produtos 
        (produto_id, nome_produto, preco, tamanho, clean_product, marca_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        fix_nan(row['Id']),
        fix_nan(row['name']),
        fix_nan(row['price']),
        fix_nan(row['size']),
        fix_nan(row['clean_product']),
        brand_id
    ))

# --- Inserir categorias ---
categorias_unicas = df_produtos['category'].dropna().unique()
for i, categoria in enumerate(categorias_unicas, start=1):
    cursor.execute("""
        INSERT IGNORE INTO categorias (categoria_id, nome_categoria)
        VALUES (%s, %s)
    """, (i, categoria))

# --- Inserir produto_categorias ---
for _, row in df_produtos.iterrows():
    if pd.notna(row['category']):
        cursor.execute("SELECT categoria_id FROM categorias WHERE nome_categoria=%s", (row['category'],))
        categoria_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT IGNORE INTO produto_categorias (produto_id, categoria_id)
            VALUES (%s, %s)
        """, (fix_nan(row['Id']), categoria_id))

# --- Inserir avaliacoes ---
for _, row in df_produtos.iterrows():
    cursor.execute("""
        INSERT IGNORE INTO avaliacoes (avaliacao_id, produto_id, n_reviews, n_loves, review_score)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        fix_nan(row['Id']),
        fix_nan(row['Id']),
        fix_nan(row['n_of_reviews']),
        fix_nan(row['n_of_loves']),
        fix_nan(row['review_score'])
    ))

# --- Finalizar ---
conn.commit()
conn.close()

print("✅ Importação concluída com sucesso!")

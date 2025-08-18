#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cria tabelas PostgreSQL a partir do schema exposto pela API.
- Staging (landing.<TABLE_NAME>): todas as colunas como TEXT
- Curada  (core.<TABLE_NAME>): tipos conforme mapeamento TYPE_MAP

Ajuste as constantes na seção CONFIG para seu ambiente.
"""
import os
from dotenv import load_dotenv
import os
import sys
import requests
from typing import Dict, List
from psycopg import connect
from psycopg.rows import dict_row

# ======================
# CONFIG
# ======================

# Carrega variáveis do arquivo .env para o ambiente
load_dotenv()

BASE = os.getenv("API_BASE")
SCHEMA_ENDPOINT = "/schema"   # caminho do endpoint de schema

TABLE_NAME = os.getenv("TABLE_NAME")
if not TABLE_NAME:
    raise ValueError("A variável TABLE_NAME não foi definida no ambiente.")  # nome da tabela a criar

# Headers de autenticação obrigatórios da API
headers = {
    "x-api-key": os.getenv("API_TOKEN")
}

print(headers)

PG_DSN = os.getenv("PG_DSN")

SCHEMA_STAGING = "landing"
SCHEMA_CORE = "core"

# Se souber a PK de negócio, defina aqui (ex.: "nk_ota_localizer_id"); caso contrário, deixe None
PRIMARY_KEY = os.getenv("PRIMARY_KEY")  # ou None

# Mapeamento de tipos da API -> PostgreSQL
# Ajuste se sua API usa outras labels (ex.: "decimal", "int32", etc.)
TYPE_MAP: Dict[str, str] = {
    "string": "TEXT",
    "float": "DOUBLE PRECISION",     # use NUMERIC(12,2) para dinheiro com precisão fixa
    "decimal": "NUMERIC(12,2)",      # caso a API retorne "decimal"
    "int": "BIGINT",
    "integer": "BIGINT",
    "bool": "BOOLEAN",
    "boolean": "BOOLEAN",
    "date": "DATE",
    "datetime": "TIMESTAMPTZ",
    "timestamp": "TIMESTAMPTZ",
    "time": "TIME",
}

# ======================
# HELPERS
# ======================

def quote_ident(name: str) -> str:
    """Cota identificadores de forma segura com aspas duplas."""
    return '"' + name.replace('"', '""') + '"'

def fetch_schema(base: str, endpoint: str, headers: Dict[str, str]) -> Dict:
    url = base.rstrip("/") + endpoint
    r = requests.get(url, headers=headers, timeout=60)
    r.raise_for_status()
    js = r.json()
    if "columns" not in js or not isinstance(js["columns"], list):
        raise ValueError(f"Schema inesperado de {url}: {js}")
    return js

def ensure_schemas(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_STAGING};")
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_CORE};")

def build_staging_ddl(table: str, columns: List[Dict[str, str]]) -> str:
    cols = [f"  {quote_ident(c['name'])} TEXT" for c in columns]
    cols.append("  raw_loaded_at TIMESTAMPTZ DEFAULT now()")
    ddl = f"""CREATE TABLE IF NOT EXISTS {SCHEMA_STAGING}.{quote_ident(table)} (
{",\n".join(cols)}
);"""
    return ddl

def build_core_ddl(table: str, columns: List[Dict[str, str]], pk: str | None) -> str:
    mapped_cols = []
    for c in columns:
        api_t = str(c.get("type", "string")).lower()
        pg_t = TYPE_MAP.get(api_t, "TEXT")
        mapped_cols.append(f"  {quote_ident(c['name'])} {pg_t}")
    ddl = f"""CREATE TABLE IF NOT EXISTS {SCHEMA_CORE}.{quote_ident(table)} (
{",\n".join(mapped_cols)}
);"""
    if pk:
        ddl += f"""
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'pk_{table}'
    ) THEN
        ALTER TABLE {SCHEMA_CORE}.{quote_ident(table)}
        ADD CONSTRAINT pk_{table} PRIMARY KEY ({quote_ident(pk)});
    END IF;
END$$;"""
    return ddl

# ======================
# MAIN
# ======================

def main():
    print(f"→ Lendo schema em {BASE}{SCHEMA_ENDPOINT} ...")
    schema = fetch_schema(BASE, SCHEMA_ENDPOINT, headers)
    columns = schema["columns"]  # esperado: list[ {name, type} ]
    if not columns:
        print("Schema sem colunas. Nada a criar.", file=sys.stderr)
        sys.exit(1)

    print(f"→ {len(columns)} colunas encontradas:")
    for c in columns:
        print(f"   - {c['name']} ({c.get('type','string')})")

    staging_ddl = build_staging_ddl(TABLE_NAME, columns)
    core_ddl = build_core_ddl(TABLE_NAME, columns, PRIMARY_KEY)

    print("\n→ Conectando ao Postgres ...")
    with connect(PG_DSN, row_factory=dict_row, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TIME ZONE 'UTC'")
        ensure_schemas(conn)
        print("→ Criando/validando tabela de staging ...")
        with conn.cursor() as cur:
            cur.execute(staging_ddl)
        print("→ Criando/validando tabela curada ...")
        with conn.cursor() as cur:
            cur.execute(core_ddl)
        conn.commit()

    print("\n✅ Concluído.")
    print(f"- Staging: {SCHEMA_STAGING}.{TABLE_NAME}")
    print(f"- Curada : {SCHEMA_CORE}.{TABLE_NAME}")
    if PRIMARY_KEY:
        print(f"- PK     : {PRIMARY_KEY}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(2)
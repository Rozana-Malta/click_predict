#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, requests
from typing import List, Dict, Any, Iterable, Tuple
from decimal import Decimal
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

load_dotenv()

API_BASE    = os.getenv("API_BASE", "").rstrip("/")
API_KEY     = os.getenv("API_TOKEN")
PG_DSN      = os.getenv("PG_DSN")
TABLE_NAME  = os.getenv("TABLE_NAME")                 # ex: clickbus_projetods
SCHEMA      = os.getenv("SCHEMA_TARGET", "core")      # padrão: core
PAGE_SIZE   = int(os.getenv("PAGE_SIZE", "5000"))

if not (API_BASE and API_KEY and PG_DSN and TABLE_NAME):
    raise SystemExit("Faltam variáveis no .env: API_BASE, API_TOKEN, PG_DSN, TABLE_NAME")

HEADERS = {"x-api-key": API_KEY}

# ---- ident antes de usar core_fqn ----
def ident(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'

core_fqn = f"{ident(SCHEMA)}.{ident(TABLE_NAME)}"

# --------------------------
# Helpers de tipos / casts
# --------------------------

def normalize_number_str(s: str) -> str:
    s = s.strip()
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            return s.replace(".", "").replace(",", ".")  # pt-BR
        return s.replace(",", "")                       # en-US
    if "," in s:
        return s.replace(",", ".")
    return s

def cast_value(value: Any, pg_type: str):
    if value is None:
        return None
    if isinstance(value, (int, float, bool, Decimal)):
        return value

    s = str(value).strip()
    if s == "":
        return None

    t = (pg_type or "").lower()

    try:
        if t in ("bigint", "integer", "smallint"):
            s_clean = "".join(ch for ch in s if ch.isdigit() or ch in "+-")
            return int(s_clean) if s_clean else None

        if t in ("numeric", "decimal", "double precision", "real"):
            s_num = normalize_number_str(s)
            if t in ("numeric", "decimal"):
                return Decimal(s_num)
            return float(s_num)

        if t == "boolean":
            low = s.lower()
            if low in {"true", "t", "1", "yes", "y", "sim"}:
                return True
            if low in {"false", "f", "0", "no", "n", "nao", "não"}:
                return False
            return bool(int(s))

        if "timestamp" in t or t.startswith("date") or t.startswith("time"):
            return s

        return s

    except Exception:
        return value

# --------------------------
# Descobrir colunas da tabela
# --------------------------

def get_table_columns(conn) -> Tuple[List[str], set, Dict[str, str]]:
    q = """
    SELECT column_name, data_type, is_identity = 'YES' AS is_identity
    FROM information_schema.columns
    WHERE table_schema = %s AND table_name = %s
    ORDER BY ordinal_position;
    """
    with conn.cursor() as cur:
        cur.execute(q, (SCHEMA, TABLE_NAME))
        rows = cur.fetchall()

    if not rows:
        raise SystemExit(f"Tabela {core_fqn} não encontrada.")

    cols = [r["column_name"] for r in rows]
    identity = {r["column_name"] for r in rows if r["is_identity"]}
    types = {r["column_name"]: r["data_type"] for r in rows}
    return cols, identity, types

# --------------------------
# API (paginação simples)
# --------------------------

def fetch_dados() -> Iterable[List[Dict[str, Any]]]:
    page = 1
    while True:
        params = {"page": page, "page_size": PAGE_SIZE}
        r = requests.get(f"{API_BASE}/dados", headers=HEADERS, params=params, timeout=120)
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        if not isinstance(data, list):
            raise SystemExit(f"/dados retornou formato inesperado (esperado lista). Página {page}.")
        yield data
        page += 1

# --------------------------
# SQL dinâmico de INSERT
# --------------------------

def build_insert_sql(cols: List[str]) -> str:
    insert_cols = ", ".join(ident(c) for c in cols)
    placeholders = ", ".join(f"%({c})s" for c in cols)
    return f"INSERT INTO {core_fqn} ({insert_cols}) VALUES ({placeholders});"

# --------------------------
# MAIN
# --------------------------

def main():
    print("→ Conectando ao Postgres …")
    with connect(PG_DSN, row_factory=dict_row, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TIME ZONE 'UTC'")

        table_cols, identity_cols, table_types = get_table_columns(conn)

        excluded = set(identity_cols) | {"raw_loaded_at"}
        insertable_cols = [c for c in table_cols if c not in excluded]

        insert_sql = build_insert_sql(insertable_cols)

        print(f"→ Tabela alvo: {core_fqn}")
        print(f"→ Colunas inseridas ({len(insertable_cols)}): {insertable_cols}")
        print("→ Duplicatas são permitidas (sem ON CONFLICT).")

        total = inserted = failed = 0

        for batch in fetch_dados():
            with conn.cursor() as cur:
                for row in batch:
                    total += 1
                    params = {c: cast_value(row.get(c), table_types.get(c, "")) for c in insertable_cols}
                    try:
                        cur.execute(insert_sql, params)
                        conn.commit()  # ✅ COMMIT por linha
                        inserted += 1
                    except Exception as e:
                        conn.rollback()
                        failed += 1
                        print(f"[ERRO] linha {total}: {type(e).__name__}: {e}", file=sys.stderr)

            print(f"→ Inseridos acumulados: {inserted} | Falhas: {failed} | Processados: {total}")

        print("\n✅ Ingestão finalizada.")
        print(f"   ✔ Inseridos: {inserted}")
        print(f"   ✖ Falhas   : {failed}")
        print(f"   Σ Processados: {total}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"ERRO: {type(e).__name__} {e}", file=sys.stderr)
        sys.exit(2)


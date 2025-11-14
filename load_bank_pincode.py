import sys
from pathlib import Path
import psycopg2
from good_debt import settings


def get_connection():
    cfg = settings.DATABASES["default"]
    opts = cfg.get("OPTIONS", {})
    return psycopg2.connect(
        dbname=cfg["NAME"],
        user=cfg["USER"],
        password=cfg["PASSWORD"],
        host=cfg.get("HOST", "localhost"),
        port=cfg.get("PORT", "5432"),
        sslmode=opts.get("sslmode", None),
    )


essql_create = (
    "CREATE TABLE IF NOT EXISTS public.App_bankpincode ("
    "id BIGINT PRIMARY KEY,"
    "bank_name TEXT,"
    "pincode TEXT,"
    "city TEXT,"
    "state TEXT,"
    "bank_url TEXT,"
    "loan_types TEXT"
    ")"
)


copy_sql = (
    "COPY public.App_bankpincode (id, bank_name, pincode, city, state, bank_url, loan_types) "
    "FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
)


def main():
    if len(sys.argv) < 2:
        print("Usage: python load_App_bankpincode.py <path-to-csv>")
        sys.exit(2)
    csv_path = Path(sys.argv[1])
    if not csv_path.exists() or not csv_path.is_file():
        print(f"File not found: {csv_path}")
        sys.exit(3)

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(essql_create)
        with conn.cursor() as cur:
            with open(csv_path, "r", encoding="utf-8", newline="") as f:
                cur.copy_expert(sql=copy_sql, file=f)
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM public.App_bankpincode")
                count = cur.fetchone()[0]
        print(f"Loaded into public.App_bankpincode. Total rows now: {count}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

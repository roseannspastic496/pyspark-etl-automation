import psycopg2
import configparser

# Read postgres configuration
config = configparser.ConfigParser()
config.read("etl.cfg")

# Connect to the postgres DB
params = config["postgresql"]
conn = psycopg2.connect(
    host=params["host"],
    dbname=params["dbname"],
    user=params["user"],
    password=params["password"],
    port=params["port"]
)

# Open a cursor to perform database operations
cur = conn.cursor()


def fetchEtlResult(cur, id: int) -> tuple:
    cur.execute("""
        SELECT 
            favourite_product,
            longest_streak 
        FROM customers 
        WHERE customer_id=%s
    """,(id,))

    # Retrieve query results
    row = cur.fetchone()

    return row

# Compare the query result with manually checked data
def test_fetchEtlResult():
    assert fetchEtlResult(cur, 23938) == ("PURA250", 2)
"""Entry point for the ETL application

Sample usage:
docker-compose run etl poetry run python main.py \
  --source /opt/data/transaction.csv \
  --database warehouse
  --table transactions
"""
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType,StructField,StringType,IntegerType,DateType
import os
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--source",help="Path to CSV source")
parser.add_argument("--database",help="database name in database")
parser.add_argument("--table",help="table name in database")
args = parser.parse_args()

dataSchema = StructType([
    StructField("transactionId",StringType()),
    StructField("custId",IntegerType()),
    StructField("transactionDate",DateType()),
    StructField("productSold",StringType()),
    StructField("unitsSold",IntegerType())  
])

spark = SparkSession\
    .builder\
    .master('spark://spark:7077')\
    .appName("Sertis")\
    .config("spark.jars", "/app/postgresql-42.6.0.jar") \
    .getOrCreate()

#  Spark read data from specific CSV file and specific source
transactionDf = spark.read.csv(args.source, sep='|', header=True, schema=dataSchema)

# use Spark SQL syntax
transactionDf.createOrReplaceTempView("transactions")
# Create customer purchase summary table to query each customer favourite product
purchaseSummaryDf = spark.sql("""
    SELECT 
        custId,
        productSold,
        SUM(unitsSold) AS totalSold
    FROM transactions
    GROUP BY custId, productSold
""")
purchaseSummaryDf.createOrReplaceTempView("purchaseSummary")

# Create favourite product dataframe
favouriteProductDf = spark.sql("""
    SELECT *
    FROM (
        SELECT
            custId,
            productSold,
            ROW_NUMBER() OVER (PARTITION BY custId ORDER BY totalsold DESC) AS rank
        FROM purchaseSummary
    )
    WHERE rank = 1
""")
favouriteProductDf.createOrReplaceTempView("favouriteProduct")

# Query for the each customer's longest purchasing streak
longestStreakDf = spark.sql("""
    WITH cte AS (
        SELECT DISTINCT 
            custId,
            transactionDate
        FROM transactions
        ),
        groups AS (
        SELECT
            custId,
            DATE_ADD(transactionDate, -ROW_NUMBER() OVER (PARTITION BY custId ORDER BY custId, transactionDate)) AS auxilaryGroup
        FROM cte
        )
    SELECT
        custId,
        MAX(consecutiveDay) AS longestStreak
    FROM (
        SELECT 
        custId,
        COUNT(*) AS consecutiveDay
        FROM groups
        GROUP BY custId, auxilaryGroup
    )
    GROUP BY custId
    ORDER BY longestStreak desc
""")
longestStreakDf.createOrReplaceTempView("longestStreak")

# Create final customers summary table by joining favouriteProduct and longestStreak temporary view
customersSummaryDf = spark.sql("""
  SELECT 
    fp.custId         AS customer_id,
    fp.productSold    AS favourite_product,
    ls.longestStreak  AS longest_streak
  FROM favouriteProduct fp
  JOIN longestStreak ls
    ON fp.custId = ls.custId
  ORDER BY longest_streak, favourite_product
""")

POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

customersSummaryDf.write\
    .format("jdbc")\
    .option("url",f"jdbc:postgresql://{POSTGRES_HOST}:5432/{args.database}")\
    .option("dbtable",f"{args.table}")\
    .option("createTableColumnTypes","customer_id INT,favourite_product VARCHAR(7),longest_streak SMALLINT")\
    .option("user",f"{POSTGRES_USER}")\
    .option("password",f"{POSTGRES_PASSWORD}")\
    .option("driver","org.postgresql.Driver")\
    .mode("overwrite")\
    .save()

# Spawn subprocess to verify the ETL process
result = subprocess.run("pytest")
if result.returncode != 0:
    raise RuntimeError("Tests failed")

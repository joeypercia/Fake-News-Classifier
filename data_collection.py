from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, rand
from pyspark.sql.types import StructType, StructField, StringType
import time


def print_type_counts(df, name):
    filtered_df = df.filter((col("type") == "fake") | (col("type") == "reliable"))
    count_df = filtered_df.groupBy("type").count()
    print(f"Counts of 'fake' and 'reliable' in {name}:")
    count_df.show()


start_time = time.time()

spark = SparkSession.builder \
    .appName("Data Preprocessing") \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "8g") \
    .config("spark.executor.instances", "3") \
    .getOrCreate()


schema = StructType([
    StructField("id", StringType(), True),
    StructField("domain", StringType(), True),
    StructField("type", StringType(), True),
    StructField("url", StringType(), True),
    StructField("content", StringType(), True),
    StructField("scraped_at", StringType(), True),
    StructField("inserted_at", StringType(), True),
    StructField("updated_at", StringType(), True),
    StructField("title", StringType(), True),
    StructField("authors", StringType(), True),
    StructField("keywords", StringType(), True),
    StructField("meta_keywords", StringType(), True),
    StructField("meta_description", StringType(), True),
    StructField("tags", StringType(), True),
    StructField("summary", StringType(), True),
    StructField("source", StringType(), True)
])

df = spark.read.format("csv") \
    .option("header", "true") \
    .option("delimiter", ",") \
    .option("multiLine", "true") \
    .option("escape", "\"") \
    .option("quote", "\"") \
    .option("inferSchema", "true") \
    .load("news_cleaned_2018_02_13.csv")

print("df:")
df.show(100)

df_filtered = df.select("title", "type", "content")

print("df_filtered:")
df_filtered.show(100)

df_filtered = df_filtered.filter(~col("type").isin(["political", "unreliable"]))

fake_types = ["satire", "bias", "rumor", "conspiracy", "junksci", "hate", "clickbait", "fake"]
df_filtered = df_filtered.withColumn("type", when(col("type").isin(fake_types), "fake").otherwise(col("type")))

fake_df = df_filtered.filter(col("type") == "fake").sample(fraction=0.5, seed=42)
real_df = df_filtered.filter(col("type") != "fake")

final_df = fake_df.union(real_df)
final_df = final_df.dropDuplicates(['title', 'content'])
final_df = final_df.orderBy(rand())
final_df = final_df.filter(
    (col("title").isNotNull()) &
    (col("type").isNotNull()) &
    (col("type") != "unknown") &
    (col("content").isNotNull())
)

train_df, val_df, test_df = final_df.randomSplit([0.8, 0.1, 0.1], seed=42)

print("train_df:")
train_df.show(100)
print("val_df:")
val_df.show(100)
print("test_df:")
test_df.show(100)

train_df.write.parquet("train_data.parquet", mode='overwrite')
val_df.write.parquet("val_data.parquet", mode='overwrite')
test_df.write.parquet("test_data.parquet", mode='overwrite')

print("val_data.parquet:")
df = spark.read.format("parquet").load("val_data.parquet")
df.show(100)

print("train_data.parquet:")
df = spark.read.format("parquet").load("train_data.parquet")
df.show(100)

print("test_data.parquet:")
df = spark.read.format("parquet").load("test_data.parquet")
df.show(100)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Data preparation execution time: {elapsed_time:.2f} seconds")

train_df.sample(fraction=0.05, seed=5)

print_type_counts(train_df, "Training Dataset")
print_type_counts(val_df, "Validation Dataset")
print_type_counts(test_df, "Test Dataset")

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Total execution time: {elapsed_time:.2f} seconds")

spark.stop()
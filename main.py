from pyspark.sql import SparkSession, DataFrameWriter
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StringIndexer, HashingTF, IDF
from pyspark.ml.classification import LogisticRegression
import time

start_time = time.time()

spark = SparkSession.builder \
    .appName("Fake News Classifier") \
    .config("spark.executor.memory", "3g") \
    .config("spark.driver.memory", "3g") \
    .config("spark.executor.memoryOverhead", "512m") \
    .getOrCreate()

# Load data
training_data = spark.read.format("parquet").load("sampled_train_data.parquet")
# test_data = spark.read.format("parquet").load("sampled_test_data.parquet")

# Tokenization and Feature Transformation
tokenizer = Tokenizer(inputCol="content", outputCol="words")
hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=10000)
idf = IDF(inputCol="rawFeatures", outputCol="features")

# Convert 'type' column to numeric 'label'
indexer = StringIndexer(inputCol="type", outputCol="label")

# Logistic Regression Model TODO: Implement cross-validation (task 3)
lr = LogisticRegression(maxIter=10, regParam=0.3, elasticNetParam=0.8)

# Build the pipeline
pipeline = Pipeline(stages=[tokenizer, hashingTF, idf, indexer, lr])

# TODO: Implement cross-validation (task 3)

# Fit the model
model = pipeline.fit(training_data)

# Save the model
model.write().overwrite().save("lr_model")

# TODO: Make predictions on test data and evaluate accuracy (task 4)
# predictions = model.transform(test_data)

# Define JDBC properties
url = "url"
properties = {
    "user": "cs179g",
    "password": "password",
    "driver": "com.mysql.jdbc.Driver"
}

# Write DataFrame to MySQL
# predictions.write.jdbc(url=url, table="test_predictions", mode="append", properties=properties)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Total execution time: {elapsed_time:.2f} seconds")

spark.stop()

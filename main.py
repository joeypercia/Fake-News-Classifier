from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StringIndexer, HashingTF, IDF
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
import time

start_time = time.time()

# executor instances = number of spark workers
spark = SparkSession.builder \
    .appName("Data Preprocessing") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memoryOverhead", "512") \
    .config("spark.memory.fraction", "0.8") \
    .config("spark.executor.instances", "4") \
    .config("spark.executor.cores", "4") \
    .config("spark.default.parallelism", "100") \
    .config("spark.executor.extraJavaOptions", "-XX:+UseG1GC") \
    .config("spark.driver.extraJavaOptions", "-XX:+UseG1GC") \
    .getOrCreate()

# Load data
training_data = spark.read.format("parquet").load("sampled_train_data.parquet")

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

# Make predictions on test data and evaluate accuracy
test_data = spark.read.format("parquet").load("sampled_test_data.parquet")
predictions = model.transform(test_data)
evaluator = BinaryClassificationEvaluator(rawPredictionCol="rawPrediction", labelCol="label", metricName="areaUnderROC")
accuracy = evaluator.evaluate(predictions)
print(f"Test Data Accuracy: {accuracy}")

# Write DataFrame to Cassandra
predictions.write\
    .format("org.apache.spark.sql.cassandra")\
    .mode('append')\
    .options(table="predictions", keyspace="pred")\
    .save()

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Total execution time: {elapsed_time:.2f} seconds")

spark.stop()
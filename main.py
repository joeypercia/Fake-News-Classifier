from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StringIndexer, HashingTF, IDF
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.sql.functions import udf, col, regexp_replace
from pyspark.sql.types import ArrayType, StringType
import time


def clean_non_ascii(text_list):
    cleaned_list = [x.encode('ascii', 'ignore').decode('ascii') for x in text_list]
    return cleaned_list


start_time = time.time()

# executor instances = number of spark workers
spark = SparkSession.builder \
    .appName("Fake News Classifier") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memoryOverhead", "512") \
    .config("spark.memory.fraction", "0.8") \
    .config("spark.default.parallelism", "100") \
    .config("spark.executor.extraJavaOptions", "-XX:+UseG1GC") \
    .config("spark.driver.extraJavaOptions", "-XX:+UseG1GC") \
    .config("spark.cassandra.connection.host", "localhost") \
    .config("spark.cassandra.connection.port", "9042") \
    .getOrCreate()

# Load data
training_data = spark.read.format("parquet").load("sampled_train_data.parquet")
training_data = training_data.sample(.05)

# Tokenization and Feature Transformation
tokenizer = Tokenizer(inputCol="content", outputCol="words")
hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=10000)
idf = IDF(inputCol="rawFeatures", outputCol="features")

# Convert 'type' column to numeric 'label'
indexer = StringIndexer(inputCol="type", outputCol="label")

# Logistic Regression Model
lr = LogisticRegression()

# Build the pipeline
pipeline = Pipeline(stages=[tokenizer, hashingTF, idf, indexer, lr])

# Cross-validation
paramGrid = ParamGridBuilder() \
    .addGrid(lr.maxIter, [10, 50, 100]) \
    .addGrid(lr.regParam, [0.0, 0.1, 0.3]) \
    .addGrid(lr.elasticNetParam, [0.0, 0.5, 1.0]) \
    .build()

crossval = CrossValidator(estimator=pipeline,
                            estimatorParamMaps=paramGrid,
                            evaluator=BinaryClassificationEvaluator(),
                            numFolds=3)  # Number of folds for cross-val

# Fit the model
cvModel = crossval.fit(training_data)

# Save the model
cvModel.write().overwrite().save("cv_model")

# Make predictions on test data and evaluate accuracy
test_data = spark.read.format("parquet").load("sampled_test_data.parquet")
test_data = test_data.sample(.05)
predictions = cvModel.transform(test_data)
evaluator = BinaryClassificationEvaluator(rawPredictionCol="rawPrediction", labelCol="label", metricName="areaUnderROC")
accuracy = evaluator.evaluate(predictions)
print(f"Test Data Accuracy: {accuracy}")

predictions.printSchema()
predictions.show()

# Drop incompatible vector columns from the DataFrame before writing to Cassandra
predictions = predictions.drop("rawFeatures", "rawPrediction", "features", "probability")

# Write to Cassandra
predictions.write \
    .format("org.apache.spark.sql.cassandra") \
    .mode('append') \
    .options(table="predictions", keyspace="pred") \
    .save()

# Read the data from Cassandra
data = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="predictions", keyspace="pred") \
    .load()

# Show the data
# Register UDF
clean_non_ascii_udf = udf(clean_non_ascii, ArrayType(StringType()))

# Clean dataframe
data = data.withColumn("title", regexp_replace("title", "[^\x00-\x7F]", ""))
data = data.withColumn("type", regexp_replace("type", "[^\x00-\x7F]", ""))
data = data.withColumn("content", regexp_replace("content", "[^\x00-\x7F]", ""))
data = data.withColumn("words", clean_non_ascii_udf(col("words")))
data.show()
data.printSchema()

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Total execution time: {elapsed_time:.2f} seconds")

spark.stop()

from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StringIndexer, CountVectorizer
from pyspark.ml.classification import LogisticRegression

spark = SparkSession.builder \
    .appName("Fake News Classifier") \
    .config("spark.executor.memory", "3g") \
    .config("spark.driver.memory", "3g") \
    .config("spark.executor.memoryOverhead", "512m") \
    .getOrCreate()

# Load data
training_data = spark.read.format("parquet").load("sampled_train_data.parquet")
# validation_data = spark.read.format("parquet").load("sampled_val_data.parquet")
# test_data = spark.read.format("parquet").load("sampled_test_data.parquet")

# Tokenization
tokenizer = Tokenizer(inputCol="content", outputCol="words")

# Vectorization TODO: Use TF-IDF instead (task 1)
vectorizer = CountVectorizer(inputCol="words", outputCol="features")

# Convert 'type' column to numeric 'label'
indexer = StringIndexer(inputCol="type", outputCol="label")

# Logistic Regression Model TODO: Implement TrainValidationSplit (task 3)
lr = LogisticRegression(maxIter=10, regParam=0.3, elasticNetParam=0.8)

# Build the pipeline
pipeline = Pipeline(stages=[tokenizer, vectorizer, indexer, lr])

# Fit the model
model = pipeline.fit(training_data)

# Save the model
model.write().overwrite().save("lr_model")

# TODO: Make predictions on test data and evaluate accuracy (task 4)

spark.stop()
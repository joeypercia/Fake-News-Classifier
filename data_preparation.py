from pyspark.sql import SparkSession
from pyspark.ml.feature import HashingTF, IDF, Tokenizer

spark = SparkSession.builder \
    .appName("Data Preprocessing") \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "8g") \
    .config("spark.executor.instances", "3") \
    .getOrCreate()

df = spark.read.format("csv") \
    .option("header", "true") \
    .option("delimiter", ",") \
    .option("multiLine", "true") \
    .option("escape", "\"") \
    .option("quote", "\"") \
    .option("inferSchema", "true") \
    .load("news_cleaned_2018_02_13.csv")

df_filtered = df.select("title", "type", "content")

tokenizer = Tokenizer(inputCol = "content", outputCol = "words")
wordsData = tokenizer.transform(df_filtered)
hashingTF = HashingTF(inputCol = "words", outputCol = "rawfeatures", numFeatures = 32)
featurizedData = hashingTF.transform(wordsData)
idf = IDF(inputCol = "rawfeatures", outputCol = "features")
idfModel = idf.fit(featurizedData)
rescaledData = idfModel.transform(featurizedData)

spark.stop()
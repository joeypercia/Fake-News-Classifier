# Fake News Classifier

This project uses machine learning to classify news articles into one of two categories: "reliable" or "fake".

## Data Collection/Cleaning
### Dataset: Fake News Corpus (https://github.com/several27/FakeNewsCorpus)

* Drop all but 3 columns, “title”, “type” (fake or real), and “content”.
* Remove all articles labeled as “political” or “proceed with caution”, their reliability is uncertain so they shouldn’t be used for training/testing.
* Aggregate all article types labeled as satire, bias, rumor, conspiracy, junksci, hate, and clickbait into one type: “fake” (may lead to underfitting, but having to classify too many types could lead to overfitting. Will change as needed when testing the model, simpler is better for now)
* Drop 50% of the fake articles, since there are twice as many in the dataset (3,835,102) vs. reliable articles (1,920,139). We don’t want our model to be biased towards predicting news as fake.
* Clean the dataset: remove entries with any NULL fields, or have an “unknown” type.
* Split the final dataframe into two sets: 90% training and 10% testing, then output them to separate files in parquet format.

## Building the AI Model:
* Data preparation: transform text from datasets into features using a method such as TF-IDF: https://spark.apache.org/docs/1.6.0/ml-features.html#feature-extractors
* Use cross-validation to train and validate the model: https://spark.apache.org/docs/latest/ml-tuning.html
* After the model is trained and validated, test it on the testing dataset: https://stackoverflow.com/questions/45681387/predict-test-data-using-model-based-on-training-data-set
* Use the model to classify new data: https://stackoverflow.com/questions/45986697/using-saved-spark-model-to-evaluate-new-data

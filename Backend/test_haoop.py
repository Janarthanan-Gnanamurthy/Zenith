from pyspark.sql import SparkSession

hadoop_file_path = "hdfs://0.0.0.0:19000/demo.csv"
spark = SparkSession.builder.appName("LoadJsonFromHadoopSimple").getOrCreate()

df = spark.read.format("csv").load(hadoop_file_path)

# Show the first few rows and the schema
df.show()

spark.stop()
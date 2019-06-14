
import glob
import sys


if len(sys.argv) > 0:
    slug = sys.argv[1]
else:
    slug = 'am-samoa_cap'

filename = glob.glob("../../caselaw/data/preprocessed/" + slug + "/*.txt")

print(filename)

import tools

spark = tools.get_spark()

sparkContext = spark.sparkContext
data = sparkContext.textFile(filename[0])

for f in filename[1:]:
    file = sparkContext.textFile(f)
    data = data.union(file)

unique_tokens = data.flatMap(lambda w: w.split()).distinct().count()

print(slug, "has ", unique_tokens, "unique tokens.")

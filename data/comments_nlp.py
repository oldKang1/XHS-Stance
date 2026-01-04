import pandas as pd
import time
from tqdm import tqdm
from transformers import pipeline
import numpy as np
import os

from datasets import Dataset
from transformers.pipelines.pt_utils import KeyDataset

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

thr = 0.94

def to_neutral(label, score):
    return "Neutral" if float(score) < thr else label

input = "comments1.csv"
output = "comments_nlp.csv"

df = pd.read_csv(input, encoding="utf-8", nrows=142587)

text_col = "content"

df[text_col] = df[text_col].replace(np.nan, "").astype(str).str.strip()

device_id = 0
print("雨姐加载模型中")
pipe = pipeline(
    "sentiment-analysis",
    model="IDEA-CCNL/Erlangshen-Roberta-330M-Sentiment",
    device=device_id
)

print("老铁开始了┗|｀O′|┛ 嗷~~")


ds = Dataset.from_dict({"text": df[text_col].tolist()})

batch_size = 258
t0 = time.time()

labels, scores = [], []

for out in tqdm(
    pipe(
        KeyDataset(ds, "text"),
        batch_size=batch_size,
        truncation=True,
        max_length=128
    ),
    total=len(ds),
    desc="nlp"
):
    labels.append(out["label"])
    scores.append(float(out["score"]))

df["sentiment"] = labels
df["sentiment_score"] = scores
df["sentiment"] = [to_neutral(l, s) for l, s in zip(df["sentiment"], df["sentiment_score"])]


df.to_csv(output, index=False, encoding="utf-8-sig")

t1 = time.time()
print(f"Done -> {output}")
print(f"Total time: {t1 - t0:.2f}s")
print(df["sentiment"].value_counts())

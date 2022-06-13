from fastapi import FastAPI
from pydantic import BaseModel

from transformers import pipeline



class Text(BaseModel):
    text: str = ""

fake_pipe = pipeline("text-classification", "./")
ner_pipe = pipeline("ner", "surdan/LaBSE_ner_nerel")
kwargs = {'padding':True,'truncation':True,'max_length':256}

app = FastAPI()


@app.post("/fake_news")
def fake_news(text: Text):
    text = text.text
    preds = fake_pipe(text, **kwargs)
    return preds

@app.post("/ner")
def fake_news(text: Text):
    text = text.text
    preds = ner_pipe(text)
    preds = process_preds(preds)
    return preds

def process_ners(preds):
    to_remove = set()
    for i, pred in enumerate(preds):
        if pred["word"].startswith("##") and i != 0:
            preds[i - 1]["word"] += pred["word"][2:]
            to_remove.add(i)
    preds = [p for i, p in enumerate(preds) if i not in to_remove]
    return preds

def process_preds(preds):
    print(preds)
    preds = process_ners(preds)
    for word_preds in preds:
        for k, v in word_preds.items():
            if type(v) == str:
                continue
            if v < 1:
                word_preds[k] = float(v)
            else:
                word_preds[k] = int(v)
    return preds

@app.post("/compare_ner")
def fake_(text_new: Text, text_db: Text):
    text_new = text_new.text
    text_db = text_db.text
    preds_new = ner_pipe(text_new)
    preds_new = process_preds(preds_new)
    preds_db = ner_pipe(text_db)
    preds_db = process_preds(preds_db)
    preds_db_words = {p["word"] for p in preds_db}
    extra_ners = [p for p in preds_new
                  if (p["word"] not in preds_db_words)
                  and not any(p["word"] in w for w in preds_db_words)
                  and not any(w in p["word"] for w in preds_db_words)]
    return extra_ners

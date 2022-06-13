# requires
# 11.06.2022  20:30            71 236 ru_RU.aff
# 11.06.2022  20:32         3 473 191 ru_RU.dic
import razdel
from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.tokenization import RegexTokenizer
from fastapi import FastAPI
from hunspell import Hunspell
from pydantic import BaseModel


class Text(BaseModel):
    text: str = ""


app = FastAPI()

spell_checker = Hunspell("ru_RU", hunspell_data_dir="./")
dostoevsky_tokenizer = RegexTokenizer()
sentiment_model = FastTextSocialNetworkModel(tokenizer=dostoevsky_tokenizer)


@app.post("/spelling")
def check_spelling(text: Text):
    text = text.text
    words = [w.text for w in razdel.tokenize(text)]
    unique_words = set(words)
    unique_words = {w for w in unique_words if len(w) >= 4}
    errors = 0
    for w in unique_words:
        check = spell_checker.spell(w)
        if not check:
            errors += 1
    return errors / len(unique_words)


@app.post("/sentiment")
def sentiment_analysis(text: Text):
    text = text.text
    results = sentiment_model.predict([text], k=2)
    return results

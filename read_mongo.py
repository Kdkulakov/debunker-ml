import os
from urllib.parse import quote_plus as quote

import ssl
import pymongo
import requests
from elasticsearch import Elasticsearch
from elasticsearch import RequestsHttpConnection

mongo_pass = os.getenv("MONGO_PASS")

url = "mongodb://{user}:{pw}@{hosts}/?replicaSet={rs}&authSource={auth_src}".format(
    user=quote("user_news"),
    pw=quote(mongo_pass),
    hosts=",".join(["rc1b-04te123feq45i8fg.mdb.yandexcloud.net:27018"]),
    rs="rs01",
    auth_src="db_news",
)
dbs = pymongo.MongoClient(
    url,
    tlsCAFile="/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt",
)["db_news"]

news_cursor = dbs.test_collection.find()

news = []
for col in dbs.news_test.find({}):
    news.append(col)


es = Elasticsearch(
    hosts=["https://c-c9qrq6v0lbv57ldktl6r.rw.mdb.yandexcloud.net:9200"],
    http_auth=("admin", "f294gh204h20hf"),
    timeout=30,
    max_retries=2,
    retry_on_timeout=True,
    verify_certs=False,
    connection_class=RequestsHttpConnection,
    use_ssl=True,
)

# проверка
es.ping()

# грузим в эластик. Там есть bulk загрузка. Но делал по-ленивому.
58936073

index_settings = {"settings": {"number_of_shards": 1, "number_of_replicas": 1}}
target_index = "news2"
es.indices.create(index=target_index, body=index_settings, ignore=[400])
for n in news:
    if "_id" not in n:
        pass
    else:
        n["uid"] = str(n["_id"])
        n.pop("_id")
    n["active_from_timestamp"] = int(n["active_from_timestamp"])
    n["active_to_timestamp"] = int(n["active_to_timestamp"])
    es.index(index=target_index, id=n["id"], body=n)

index = "news"
query = {
    "query": {
        "more_like_this": {
            "fields": ["full_text"],
            "like": "Москва заняла первое место",
            "min_term_freq": 1,
            "max_query_terms": 12,
        }
    }
}

res = es.search(index=index, body=query)

print(res["hits"])

import json
import sys
from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch import helpers

es_index_name = f"allrecipes-{datetime.now().strftime('%y-%m-%d')}"
es_index = Elasticsearch([{'host': 'localhost', 'port': 9200}])

measures = "teaspoon teaspoons tablespoon tablespoons ounce cup oz pound lbs can package and or all to as into"
with open('mappings.json') as mapping_f:
    config = json.load(mapping_f)
    config["settings"]["analysis"]["filter"]["unit_filter"]["stopwords"]\
        = measures.split()
es_index.indices.delete(index=es_index_name, ignore=[404])
es_index.indices.create(es_index_name, body=config)
idx_field_name = 'idx'

ingredient_stopwords = ""
def get_recipes(json_fname):
    with open(json_fname) as in_f:
        for idx, (url, recipe) in enumerate(json.load(in_f).items()):
            recipe[idx_field_name] = idx
            recipe['url'] = url
            recipe['brat_url'] = f"http://tarski.cs-i.brandeis.edu:8182/#/{idx}"
            recipe['ingredients'] = [ing.replace("* ", "") for ing in recipe['ingredients'] if len(ing.strip()) > 0]
            yield recipe


def to_bulk_iterable(index_name, elements):
    for i, element in enumerate(elements):
        docid = element.get(idx_field_name)
        identifier = i if docid is None else docid
        yield {
            # "_type": "_doc",
            "_id": identifier,
            "_index": index_name,
            "_source": element}


def load(es_index, elements):
    helpers.bulk(es_index, to_bulk_iterable(es_index_name, elements))


if __name__ == '__main__':
    load(es_index, get_recipes(sys.argv[1]))


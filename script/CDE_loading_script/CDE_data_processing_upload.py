import json
import ijson
import numpy as np
import pandas as pd
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from tqdm.std import tqdm
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from pprint import pprint
import glob
import os
def get_embedding_from_text(
    text_to_be_embedded,
    _ = None,
    model_name = 'BAAI/bge-small-en-v1.5'
):
    '''
    Calculate the embedding of the title + abstracts
    '''
    # load the model

    model = SentenceTransformer(model_name)
    print('* loaded model %s' % model_name)

    # encode the texts
    print("* encoding the texts ...")
    embeddings = model.encode(
        text_to_be_embedded,
        show_progress_bar=True,
    )
    return embeddings

def get_embedding_openai(texts, api_key, model='text-embedding-3-small'):
    client = OpenAI(api_key=api_key)
    embeddings = []
    for text in texts:
        text = text.replace("\n", " ")
        embedding = client.embeddings.create(input=[text], model=model).data[0].embedding
        embeddings.append(embedding)
    return embeddings

def process_cde_data(cde_data, embedding_method, api_key = None, endorsed=False):
    # Create a dataframe from the cde_data
    concept_id = []
    TinyId = []
    CDE = []
    Values = []
    Definition = []
    Collection = []
    Combination = []
    source_document = []

    for line in tqdm(cde_data):
        cde_name = line['designations'][0]['designation']
        cde_id = line['tinyId']
        cde_def = ''
        if len(line['definitions']) > 0:
            cde_def = line['definitions'][0]['definition']
        
        if endorsed:
            source = 'NIH-Endorsed'
        else:
            source = line['stewardOrg']['name']
        temp_values = []
        datatype = line['valueDomain']['datatype']
        if datatype == 'Value List':
            for v in line['valueDomain']['permissibleValues']:
                temp_values.append(v.get("permissibleValue"))
        
        combine = f'{cde_name}: {cde_def}'
        document = line

        concept_id.append(cde_id)
        TinyId.append(cde_id)
        CDE.append(cde_name)
        Values.append(" | ".join(temp_values))
        Definition.append(cde_def)
        Collection.append(source)
        Combination.append(combine)
        source_document.append(line)

    CDE_df = pd.DataFrame({"concept_id":TinyId, "source":Collection,"code":TinyId, "term":CDE, "value":Values, "description":Definition, "Combination":Combination,"source_document":source_document})

    embeddings = embedding_method(CDE_df["Combination"].tolist(), api_key)
    CDE_df["embedding"] = embeddings.tolist()

    cde_list = []
    for row in CDE_df.itertuples():
        cde_list.append({"concept_id":row.concept_id, "source":row.source, "code":row.code, "term":row.term,"value":row.value,"description":row.description,"source_document":row.source_document, "embedding":row.embedding})
    return cde_list

class Search:
    def __init__(self, index, es_url = 'http://localhost:9200', dims = 384):
        self.dims = dims
        self.es = Elasticsearch(es_url)
        client_info = self.es.info()
        print('Connected to Elasticsearch!')
        pprint(client_info.body)
        
        self.index = index
    
    def is_exist(self):
        if not self.es.indices.exists(index=self.index):
            return False
        else:
            return True
            

    def delete_index(self):
        self.es.indices.delete(index=self.index, ignore_unavailable=True)
        
    def search(self, **query_args):
        return self.es.search(index=self.index, **query_args)
    
    def retrieve_document(self, id):
        return self.es.get(index=self.index, id=id)

    def create_index(self):
        self.es.indices.delete(index=self.index, ignore_unavailable=True)
        self.es.indices.create(index=self.index, body = {
                    'mappings':{
                        'properties':{
                            'concept_id':{
                                'type': 'keyword'
                            },
                            'source':{
                                'type': 'keyword'
                            },
                            'code':{
                                'type': 'keyword'
                            },
                            'term':{
                                'type': 'text'
                            },
                            'value':{
                                'type': 'text'
                            },
                            'description':{
                                'type':'text'
                            },
                            'source_document':{
                                'type':'object',
                                'enabled':False
                            },
                            'embedding':{
                                'type': 'dense_vector',
                                'dims': self.dims,
                                'similarity': 'cosine'
                            }
                        }
                    }
                    })

    def insert_document(self, document):
        return self.es.index(index=self.index, body=document)
    

    def insert_documents(self, documents, chunk_size=500):
        def generate_operations(documents):
            for doc in documents:
                yield {'_index': self.index, '_source': doc}
        
        success, failed = 0, 0
        for ok, result in helpers.streaming_bulk(self.es, generate_operations(documents),\
                                                      chunk_size=chunk_size):
            if not ok:
                failed += 1
            else:
                success += 1
        return success, failed
    
    def reindex(self, json_file):
        self.create_index()
        with open(json_file, 'rt') as f:
            documents = json.loads(f.read())
        
        return self.insert_documents(documents)

def upload_cde_data(cde_list, index_name, force_update=False):
    search = Search(index_name,'http://localhost:9201', dims=384)
    if search.is_exist():
        if force_update:
            search.delete_index()
            search.create_index()
        else:
            print(f"Index '{index_name}' already exists. Use 'force_update=True' to delete and reindex.")
            return
    search.create_index()
    batch_size = 5000
    data_batches = []
    for item in tqdm(cde_list):
        data_batches.append(item)
        if len(data_batches) >= batch_size:
            search.insert_documents(data_batches)
            data_batches = []
    if data_batches:
        search.insert_documents(data_batches)
        data_batches = []
    print(f"Uploaded documents to index '{index_name}'")


if __name__ == "__main__":
    input_dir = "./input"
    json_files = glob.glob(os.path.join(input_dir, "*.json"))
    
    if json_files:
        print(f"Found {len(json_files)} JSON files in {input_dir}:")
        all_cde_list = []
        for file_path in json_files:
            endorsed = 'endorsed' in file_path
            print(endorsed)
            with open(file_path, 'r') as f:
                cde_data = json.load(f)
            cde_list = process_cde_data(cde_data, get_embedding_from_text, api_key = None, endorsed=endorsed)
            all_cde_list.extend(cde_list)
        upload_cde_data(all_cde_list, 'nih-cde-test', force_update=True)
    else:
        print(f"No JSON files found in {input_dir}")
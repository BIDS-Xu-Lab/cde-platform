'''
Script for loading index to ES
'''

import os
import sys
import json
import ijson
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers
from pprint import pprint
from tqdm.std import tqdm
from openai import OpenAI

load_dotenv()

class Search:
    def __init__(self, index="", encoder='text-embedding-3-small'):
        self.es = Elasticsearch(os.environ['ES_PATH']) ##里面替换成合适的url，但是端口号应该还是9200
        client_info = self.es.info()
        print('Connected to Elasticsearch!')
        pprint(client_info.body)
        
        self.index = index
        self.model = encoder
        api_key = os.environ['OPENAI_API_KEY']
        if api_key:
            self.client = OpenAI(api_key=api_key)
    
    ## 用于判断你提供的index是否存在
    def list_index(self):
        return self.es.indices.get_alias("*")
    def is_exist(self):
        if not self.es.indices.exists(index=self.index):
            raise ConnectionError(f"Index '{self.index}' does not exist.")
            
    ## 输入一个text，会调用GPT生成embedding
    def get_embedding(self, text):
        text = text.replace("\n", " ")
        return self.client.embeddings.create(input=[text], model=self.model).data[0].embedding
    
    ## 用于删除index
    def delete_index(self):
        self.es.indices.delete(index=self.index, ignore_unavailable=True)
        
    ## 用于检索query,但是具体的实现要自己实现，我这里面没有提供，因为我这边的检索只是我当时自己测试使用的，和CDE mapper里面的代码会有所不同
    def search(self, **query_args):
        return self.es.search(index=self.index, **query_args)
    
    def retrieve_document(self, id):
        return self.es.get(index=self.index, id=id)
        
    ## 创建index
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
                            'Embedding':{
                                'type': 'dense_vector',
                                'dims': 1536,
                                'similarity': 'cosine'
                            }
                        }
                    }
                    })
        
    ## 按行上传index到elasticsearch中
    def insert_document(self, document):
        return self.es.index(index=self.index, body=document)
    

    ## 按照批次上传到elasticsearch中，默认是一次上传500行
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
    

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Load index to Elasticsearch'
    )

    parser.add_argument(
        'action',
        type=str,
        default='help',
        help='Action (e.g., reindex/clear/list/create/insert)'
    )

    parser.add_argument(
        '-index',
        type=str,
        help='Index name (e.g., cde-demo)'
    )

    parser.add_argument(
        '-files',
        type=str,
        help='Path to json files (e.g., data1.json,data2.json)'
    )

    args = parser.parse_args()

    action = args.action

    if action == 'help':
        parser.print_help()
        sys.exit(0)

    if action == 'list':
        es = Elasticsearch(os.environ['ES_PATH'])
        try:
            indices = es.indices.get_alias(index="*")
            print("Elasticsearch Indices:")
            for index_name in indices:
                print(index_name)
        except Exception as e:
            print("Error fetching indices:", e)
            sys.exit(1)
        sys.exit(0)

    search = Search(args.index)
    if action == 'create':
        search.create_index()
        print('* Index created')

        batch_size = 5000
        data_bacth = []
        filenames = args.files.split(',')
        # check if the files exist
        for filename in filenames:
            if not os.path.exists(filename):
                print(f'* File {filename} does not exist')
                sys.exit(1)
        print('* Found %s files' % len(filenames))
        for name in filenames:
            with open(name,'rb') as f:
                for i,item in tqdm(enumerate(ijson.items(f,'item'))):
                    data_bacth.append(item)
                    if len(data_bacth) >= batch_size:
                        search.insert_documents(data_bacth)
                        data_bacth = []
                if data_bacth:
                    search.insert_documents(data_bacth)
                    data_bacth = []
        print('add all documents into database')
        sys.exit(0)

    if action == 'insert':
        search.is_exist()
        batch_size = 5000
        data_bacth = []
        filenames = args.files.split(',')
        # check if the files exist
        for filename in filenames:
            if not os.path.exists(filename):
                print(f'* File {filename} does not exist')
                sys.exit(1)
        print('* Found %s files' % len(filenames))
        for name in filenames:
            with open(name,'rb') as f:
                for i,item in tqdm(enumerate(ijson.items(f,'item'))):
                    data_bacth.append(item)
                    if len(data_bacth) >= batch_size:
                        search.insert_documents(data_bacth)
                        data_bacth = []
                if data_bacth:
                    search.insert_documents(data_bacth)
                    data_bacth = []
        print('add all documents into database')
        sys.exit(0)


    if action == 'reindex':
        search.reindex(args.files)
        print('* Index reindexed')
        sys.exit(0)
    
    if action == 'clear':
        search.delete_index()
        print('* Index deleted')
        sys.exit(0)
    
    print(f'* Action {action} not found')
    sys.exit(1)

    
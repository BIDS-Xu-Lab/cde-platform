import datetime
import time
import os
import asyncio
from elasticsearch import Elasticsearch
import jwt
from motor.motor_asyncio import AsyncIOMotorClient
import json
import httpx
import logging

from fastapi import FastAPI, HTTPException, Request, Response, Body, Path, Depends, status, Security, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from bson import ObjectId
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger("uvicorn")

# app = FastAPI(root_path=os.environ['ROOT_PATH'])
app = FastAPI(root_path="/")
# prefix_router = APIRouter(root_path="/cde-api")

es = Elasticsearch(os.environ['ES_PATH'])
auth_scheme = HTTPBearer()
mongo_client = AsyncIOMotorClient(os.environ['MONGODB_URI'])
db = mongo_client.get_database()
jobs_collection = db.jobs
users_collection = db.users

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def validate_token(http_auth: HTTPAuthorizationCredentials = Security(auth_scheme)):
    token = http_auth.credentials
    try:
        return {
            "user_id": "test_user",
            "token": '123'
        }
    except Exception as e:
        raise e


class BulkSearchRequest(BaseModel):
    queries: List[str]
    description: List[str] | None = None
    source: List[str] | None = None
    mapping: str
    if_fuzzy: bool = True
    openai: bool = False

def sign_jwt(user) -> Dict[str, str]:
    '''
    Sign a JWT token with the user's information.
    '''
    # {
    #     "email": email.lower(),
    #     "name": name,
    # }

    user["exp"] = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=10)

    token = jwt.encode(
        user, 
        "12312321312321312312321321", 
        algorithm='HS256'
    )

    return token

class UserLoginModel(BaseModel):
    email: str
    name: str
    password: str

@app.post("/login", tags=["user"])
async def user_login(
    request: Request,
    response: Response,
    user_login: UserLoginModel
):
    '''
    User login
    '''
    # logging.info(f"User login token: {user_login.email[:20]} ...")

    # try:
        # check whether this user is in the database
    _user = dict(
        email=user_login.email, 
        name=user_login.email + " name",
        password=user_login.password,
    )

    logging.debug(f"User login: get user {_user}")

    if _user is None:
        # create a new user
        new_user = _user

        # sign a jwt for this session
        token = sign_jwt(new_user)
        flag_new_user = True
        
        # fix new user bug
        _user = new_user
        
        logging.info(f"User login: new user created {_user['email']}")

    else:
        # update the session
        token = sign_jwt(_user)
        flag_new_user = False
        logging.info(f"User login: existing user {_user['email']}")

    # set the cookie
    response.set_cookie(
        'access_token',
        token,
        httponly=True,
        secure=True,
        samesite='strict',
    )

    return {
        "success": True,
        "message": "Login successfully",
        "flag_new_user": flag_new_user,
        "access_token": token,
        "user": _user
    }

    # except Exception as e:
    #     logging.error(f"Error in user_login: {e}")
    #     raise HTTPException(status_code=403, detail="Invalid/expired token or other errors %s" % e)
        # return {
        #     "success": False,
        #     "message": "Error in user_login %s" % e
        # }


@app.post("/logout", tags=["user"])
async def user_logout(
    request: Request,
    response: Response,
    req: dict,
):
    '''
    User logout
    '''
    # remove the cookie
    response.set_cookie(
        'access_token',
        '',
        httponly=True,
        # secure=True,
        samesite='strict',
    )
        
    return {
        "success": True,
        "message": "Logout successfully"
    }
    



@app.post('/openai/job')
async def create_job(requests: Dict[str, Any] = Body(...)):
    request_data = {
        "requests": requests.get("requests", []),
    }
    request_data["status"] = "pending"
    result = await jobs_collection.insert_one(request_data)
    job_id = str(result.inserted_id)
    return {"job_id": job_id}


@app.get('/openai/job/{job_id}')
async def get_openai_job(job_id: str = Path(..., title="The ID of the job to get")):
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid job_id format")
    job = await jobs_collection.find_one({"_id": ObjectId(job_id)})
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    job["_id"] = str(job["_id"])  # Convert ObjectId to string for JSON compatibility
    return job


@app.put("/users/{user_id}", response_model=Dict[str, Any], summary="Create or Update User Document", dependencies=[Depends(validate_token)])
async def upsert_user_document(user_id: str, user_data: Dict[str, Any] = Body(...)):
    # Ensure the user_id in the body matches the user_id in the path
    user_data['user_id'] = user_id
    
    result = await db.user_files.update_one(
        {"user_id": user_id},
        {"$set": user_data},
        upsert=True
    )

    return {"message": "User document created or updated successfully", "user_data": user_data}
    # raise HTTPException(status_code=500, detail="An error occurred while updating the user document.")


@app.get("/users/{user_id}", response_model=Dict[str, Any], summary="Retrieve User Document", dependencies=[Depends(validate_token)])
async def get_user_document(user_id: str):
    user_document = await db.user_files.find_one({"user_id": user_id})
    if user_document:
        # Optionally, you might want to exclude the MongoDB '_id' field from the response
        user_document.pop('_id', None)
        return user_document
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/users/{user_id}/files/{file_id}/concepts", response_model=List[Dict[str, Any]], summary="Retrieve Concepts by User and File ID", dependencies=[Depends(validate_token)])
async def get_concepts(user_id: str, file_id: str):
    concepts_collection = db.concepts_collection
    query = {"user_id": user_id, "file_id": file_id}

    concepts = await concepts_collection.find(query).to_list(length=None)

    if not concepts:
        raise HTTPException(status_code=404, detail="Concepts not found")

    for concept in concepts:
        concept['_id'] = str(concept['_id'])

    return concepts


@app.put("/users/{user_id}/files/{file_id}/concepts/{concept_id}", summary="Update a Concept", dependencies=[Depends(validate_token)])
async def update_concept(user_id: str, file_id: str, concept_id: str, update_request: Dict[str, Any] = Body(...)):
    concepts_collection = db['concepts_collection']
    query = {
        "user_id": user_id,
        "file_id": file_id,
        "id": int(concept_id),
    }

    update_request = {key: item for key, item in update_request.items() if key != "_id"}

    update_data = {"$set": update_request}
    logger.info("update data qurey")
    # logger.info(query)
    # logger.info(update_data)
    if not update_data:
        logger.info("no update data")
    result = await concepts_collection.update_one(query, update_data)

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Concept not found")

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="No changes made to the concept")

    return {"message": "Concept updated successfully"}


@app.post("/users/{user_id}/files/{file_id}/concepts", summary="Batch Insert Concepts", dependencies=[Depends(validate_token)])
async def batch_insert_concepts(user_id: str, file_id: str, request: List[Any] = Body(...) ):
    concepts_collection = db['concepts_collection']

    # Prepare the concepts for insertion
    concepts_to_insert = request

    # Insert the concepts
    result = await concepts_collection.insert_many(concepts_to_insert)
    return {"message": f"{len(result.inserted_ids)} concepts inserted successfully"}


@app.get('/job/{job_id}', 
         summary="Retrieve Job Details",
         description="Retrieves the details of a specific job from MongoDB using the job ID. "
                     "The endpoint returns all the fields present in the job document, "
                     "including its status, requests, and other information.",
         dependencies=[Depends(validate_token)]
)
async def get_job(job_id: str = Path(..., description="The ID of the job to retrieve")) -> dict:
    try:
        object_id = ObjectId(job_id)
        job = await jobs_collection.find_one({"_id": object_id})

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Convert ObjectId to string for JSON serialization
        job['_id'] = str(job['_id'])
        return job
    except Exception as e:
        raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/bulk_search', response_model=Dict[str, Any], summary="Perform a bulk search.", description="If 'openai' flag is true, submit the search results as a job for further processing and return the job ID. Otherwise, return the search results directly.", dependencies=[Depends(validate_token)])
async def bulk_search(request_data: BulkSearchRequest):
    data = request_data
    queries = data.queries  # Expecting an array of terms
    description = data.description
    sources = data.source
    es_index = data.mapping
    should = data.if_fuzzy
    openai = data.openai


    if openai:
        embeddings = []
        for query in queries:
            job_response = await create_job({"requests": [{"model": 'text-embedding-3-small', "messages": query, "category": "embedding"}]})
            # logger.info("openai got job response")
            # logger.info(job_response)
            job_id = job_response["job_id"]
            embedding = await poll_for_job_completion(job_id)
            if embedding is None:

                break
            embeddings.append(embedding)

    # Construct the bulk search request
    bulk_search_body = []
    for i, term in enumerate(queries):
        header = {"index": es_index}
        body = {
            "size": 100,
            "query": {
                "bool": {
                    "should": [
                        {"match": {
                            "term": term,
                        }}
                          
                    ]
                }
            }
        }
        if description and i < len(description):
            body["query"]["bool"]["should"] = []
            body["query"]["bool"]["should"] = [
                {"multi_match": {"query": description[i], "fields": ["term^2.5", "description^3","value^2"]}},
                {"multi_match": {"query": term, "fields": ["term^3", "description^2.5", "value^2"]}},
                # {"multi_match": {"query": description[i], "fields": ["value"]}},
                # {"multi_match": {"query": term, "fields": ["value"]}},
            ] 
            body["query"]["bool"]["minimum_should_match"] = 1


       

        if openai and i < len(embeddings):
            # body["query"]["bool"]["boost"] = 0.8
            body["query"]["bool"]["should"].append({"knn": {
                "field": "Embedding",
                "query_vector": embeddings[i],
                "num_candidates": 50,
                # "k": 10,
                "boost": 0.2,
                "filter": {
                    "terms":{
                        "source":sources
                    }
                }
            }})

        if sources:
            body["query"]["bool"]["filter"] = {
                "terms": {
                    "source": sources,
                }
            }
        bulk_search_body.append(header)
        bulk_search_body.append(body)
        logger.info("bulk search body")
        logger.info(body)
    # Execute the bulk search
    try:
        bulk_response = es.msearch(body=bulk_search_body)
        all_results = []
        for i, response in enumerate(bulk_response['responses']):
            # logger.info("bulk response")
            # logger.info(response)
            hits = response['hits']['hits']
            results = [{
                'score': hit['_score'],
                'conceptId': hit['_source'].get('concept_id'),
                'conceptCode': hit['_source'].get('code'),
                'conceptSource': hit['_source'].get('source'),
                'standardConcept': hit['_source'].get('term', ''),
                'description': hit['_source'].get('description', ''),
                'valueDomain': hit['_source'].get('source_document', {}).get('valueDomain', {}),
            } for hit in hits]
            all_results.append(results)

        return {"results": all_results}

    except Exception as e:
        raise e
        raise HTTPException(status_code=500, detail=str(e))


async def poll_for_job_completion(job_id: str) -> List[float]:
    counter = 0
    while True:
        if counter >= 10:
            logger.warning("Fetching job results timed out."+ str(job_id))  # Log a warning
            return None
        job = await get_job(job_id)
        if job["status"] == "completed":
            return job["requests"][0]["result"]
        counter += 1
        await asyncio.sleep(1)


@app.get('/mappings', response_model=List[str], summary="Retrieve top-level ontology data mappings.", description="This endpoint queries Elasticsearch to get all indices representing top-level ontology mappings. It filters out system indices (those starting with a dot '.') and returns a list of index names that represent different ontology mappings.", dependencies=[Depends(validate_token)])
def get_mappings():
    indices = es.indices.get_alias(index="*")
    index_names = [val for val in list(indices.keys()) if val[0] != '.']
    return index_names

@app.get('/sources', response_model=List[str], summary="Retrieve a list of source vocabularies.", description="This endpoint returns all vocabularies from the given mappings.", dependencies=[Depends(validate_token)])
async def get_sources(mapping: str):
    try:
        # Elasticsearch query for Terms Aggregation on the "source" field
        query_body = {
            "size": 0,  # We don't need actual documents, just the aggregation
            "aggs": {
                "unique_sources": {
                    "terms": {
                        "field": "source",  # Adjust if your field name is different
                        "size": 1000  # Adjust the size as needed
                    }
                }
            }
        }

        response = es.search(index=mapping, body=query_body)
        sources = [bucket['key'] for bucket in response['aggregations']['unique_sources']['buckets']]
        return sources
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

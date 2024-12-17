import datetime
import time
import os
import asyncio
from elasticsearch import Elasticsearch
import jwt
from motor.motor_asyncio import AsyncIOMotorClient
import json
import httpx
import sys
import logging

from fastapi import FastAPI, HTTPException, Request, Response, Body, Path, Depends, status, Security, APIRouter
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.security import APIKeyCookie
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from bson import ObjectId
from dotenv import load_dotenv
load_dotenv()

# get the logger
import logging.config
logging.config.fileConfig(os.environ['LOGGING_CONF'])
logger = logging.getLogger("uvicorn")

async def unhandled_exception_handler(request: Request, exc: Exception) -> PlainTextResponse:
    """
    This middleware will log all unhandled exceptions.
    Unhandled exceptions are all exceptions that are not HTTPExceptions or RequestValidationErrors.
    """
    logging.debug("Unhandled exception was triggered when processing the request %s", request.url.path)

    # gather the request information
    host = getattr(getattr(request, "client", None), "host", None)
    port = getattr(getattr(request, "client", None), "port", None)
    url = f"{request.url.path}?{request.query_params}" if request.query_params else request.url.path
    exception_type, exception_value, exception_traceback = sys.exc_info()
    exception_name = getattr(exception_type, "__name__", None)

    # save the log
    logging.error(
        f'{host}:{port} - "{request.method} {url}" 500 Internal Server Error <{exception_name}: {exception_value}> - Stack trace: {exception_traceback}',
    )

    return PlainTextResponse(str(exc), status_code=500)

# Create the FastAPI app
app = FastAPI(root_path=os.environ['ROOT_PATH'])

# allow all origins
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

app.add_exception_handler(Exception, unhandled_exception_handler)

# Create the Elasticsearch and MongoDB clients
es = Elasticsearch(os.environ['ES_PATH'])
logging.info('* connected to elasticsearch at %s' % os.environ['ES_PATH'])

mongo_client = AsyncIOMotorClient(os.environ['MONGODB_URI'])
db = mongo_client.get_database()
logging.info('* connected to mongodb at %s' % os.environ['MONGODB_URI'])



# jobs_collection = db.jobs

###########################################################
# User authentication related functions
###########################################################
# authentication for user related APIs
auth_scheme = HTTPBearer()
async def validate_token(http_auth: HTTPAuthorizationCredentials = Security(auth_scheme)):
    token = http_auth.credentials
    try:
        return {
            "user_id": "test_user",
            "token": '123'
        }
    except Exception as e:
        raise e


def sign_jwt(user) -> Dict[str, str]:
    '''
    Sign a JWT token with the user's information.

    User is a dictionary with the following keys:
    - email: email address
    - name: user's name
    '''
    # add a expiration time for the token
    user["exp"] = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=10)

    # sign the token
    token = jwt.encode(
        user, 
        os.environ['JWT_SECRET'], 
        algorithm=os.environ['JWT_ALGORITHM']
    )

    return token


def decode_jwt(token: str) -> dict:
    '''
    Decode a JWT token and return the user basic information.
    '''
    try:
        decoded_token = jwt.decode(
            token, 
            os.environ['JWT_SECRET'], 
            algorithms=os.environ['JWT_ALGORITHM']
        )
        return decoded_token 
    
    except jwt.ExpiredSignatureError as e:
        logging.error(f"JWT token expired: {e}")
        return None
    

###########################################################
# Authentication related scheme
###########################################################
cookie_scheme = APIKeyCookie(name="access_token", auto_error=True)
async def authJWTCookie(access_token: str = Security(cookie_scheme)):
    '''
    This is the blocking version of the JWT authentication.

    If the access_token is not in the cookie or the token is invalid, 
    it will raise an HTTPException with status code 401.
    '''
    user = decode_jwt(access_token)

    if user is None:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired jwt token."
        )
    
    return user


x_token_header_scheme = APIKeyHeader(
    name="x-token", 
    auto_error=True
)
async def authXTokenHeader(x_token: str = Security(x_token_header_scheme)):
    if os.environ['DEBUG_MODE']:
        # you can any x-token if the debug mode is on
        return 'debug_mode'
    
    if x_token not in os.environ['SECRET_TOKEN']:
        raise HTTPException(
            status_code=400, 
            detail="X-Token header invalid"
        )
    
    return x_token

###########################################################
# User session related APIs
###########################################################
class UserLoginModel(BaseModel):
    email: str
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
    try:
        # check whether this user is in the database
        _user = dict(
            email=user_login.email, 
            name=user_login.email + " name",
        )

        if user_login.password != "123":
            raise HTTPException(
                status_code=401, 
                detail="Invalid password"
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

    except Exception as e:
        logging.error(f"Error in user_login: {e}")
        raise HTTPException(status_code=403, detail="Invalid/expired token or other errors %s" % e)


@app.post("/logout", tags=["user"])
async def user_logout(
    request: Request,
    response: Response,
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
    

@app.get("/me", tags=["user"])
async def show_me(
    request: Request,
    current_user: dict = Depends(authJWTCookie), 
):
    '''
    Get user private datasets
    '''
    logging.info("get user private datasets")

    # _user = await db.users.find_one({
    #     "email": current_user['email']
    # })

    _user = current_user

    return {
        'success': True,
        'user': _user
    }


@app.post("/refresh_token", tags=["user"])
async def refresh_token(
    request: Request,
    response: Response,
    current_user: dict = Depends(authJWTCookie), 
):
    '''
    Refresh access token
    '''
    # _user = await users_repo.get_user_by_email(db_session, current_user['email'])
    _user = current_user

    # sign a new token
    new_token = sign_jwt(_user)

    response.set_cookie(
        'access_token',
        new_token,
        httponly=True,
        # secure=True,
        samesite='strict',
    )

    return {
        'success': True,
    }


###########################################################
# Test related APIs
###########################################################
@app.get('/test/es', tags=["test"])
async def test_es():
    return es.info()

@app.get('/test/mongo', tags=["test"])
async def test_mongo():
    return db.list_collection_names()



###########################################################
# Admin related APIs
###########################################################

@app.post("/init_database", tags=["admin"])
async def init_database(
    request: Request,
    x_token: str = Depends(authXTokenHeader)
):
    '''
    Initialize the database
    '''
    # create collection `users` if not exist
    existing_collections = await db.list_collection_names()

    for collection_name in ['users', 'jobs', 'projects']:
        if collection_name in existing_collections:
            logging.info(f"* found collection `{collection_name}` exists")
        else:
            # await db[collection_name].insert_one({"init": True})
            await db.create_collection(collection_name)
            logging.info(f"* created collection `{collection_name}`")

    return {
        'success': True,
        'message': 'database initialized'
    }


class UserRegisterModel(BaseModel):
    email: str | None
    name: str | None
    password: str | None

@app.post("/register", tags=["user"])
async def user_register(
    request: Request,
    user_register: UserRegisterModel,
):
    '''
    User register
    '''
    if user_register.email is None or \
        user_register.name == None or \
        user_register.password == None:

        raise HTTPException(status_code=400, detail="email, name, and password are required")
    
    # find user by email
    _user = await db.users.get_user_by_email(db_session, email)

    if _user is not None:
        return {
            'success': False,
            'message': 'email already exists'
        }

    # ok, create a new user    
    user = await users_repo.create_user(db_session, email, name)

    return {
        'success': False,
        'message': 'user created',
        'user': user
    }

###########################################################
# OpenAI related APIs
###########################################################
# @app.post('/openai/job')
# async def create_job(requests: Dict[str, Any] = Body(...)):
#     request_data = {
#         "requests": requests.get("requests", []),
#     }
#     request_data["status"] = "pending"
#     result = await jobs_collection.insert_one(request_data)
#     job_id = str(result.inserted_id)
#     return {"job_id": job_id}


# @app.get('/openai/job/{job_id}')
# async def get_openai_job(job_id: str = Path(..., title="The ID of the job to get")):
#     if not ObjectId.is_valid(job_id):
#         raise HTTPException(status_code=400, detail="Invalid job_id format")
#     job = await jobs_collection.find_one({"_id": ObjectId(job_id)})
#     if job is None:
#         raise HTTPException(status_code=404, detail="Job not found")
#     job["_id"] = str(job["_id"])  # Convert ObjectId to string for JSON compatibility
#     return job


# @app.put("/users/{user_id}", response_model=Dict[str, Any], summary="Create or Update User Document", dependencies=[Depends(validate_token)])
# async def upsert_user_document(user_id: str, user_data: Dict[str, Any] = Body(...)):
#     # Ensure the user_id in the body matches the user_id in the path
#     user_data['user_id'] = user_id
    
#     result = await db.user_files.update_one(
#         {"user_id": user_id},
#         {"$set": user_data},
#         upsert=True
#     )

#     return {"message": "User document created or updated successfully", "user_data": user_data}
#     # raise HTTPException(status_code=500, detail="An error occurred while updating the user document.")


# @app.get("/users/{user_id}", response_model=Dict[str, Any], summary="Retrieve User Document", dependencies=[Depends(validate_token)])
# async def get_user_document(user_id: str):
#     user_document = await db.user_files.find_one({"user_id": user_id})
#     if user_document:
#         # Optionally, you might want to exclude the MongoDB '_id' field from the response
#         user_document.pop('_id', None)
#         return user_document
#     else:
#         raise HTTPException(status_code=404, detail="User not found")


# @app.get("/users/{user_id}/files/{file_id}/concepts", response_model=List[Dict[str, Any]], summary="Retrieve Concepts by User and File ID", dependencies=[Depends(validate_token)])
# async def get_concepts(user_id: str, file_id: str):
#     concepts_collection = db.concepts_collection
#     query = {"user_id": user_id, "file_id": file_id}

#     concepts = await concepts_collection.find(query).to_list(length=None)

#     if not concepts:
#         raise HTTPException(status_code=404, detail="Concepts not found")

#     for concept in concepts:
#         concept['_id'] = str(concept['_id'])

#     return concepts


# @app.put("/users/{user_id}/files/{file_id}/concepts/{concept_id}", summary="Update a Concept", dependencies=[Depends(validate_token)])
# async def update_concept(user_id: str, file_id: str, concept_id: str, update_request: Dict[str, Any] = Body(...)):
#     concepts_collection = db['concepts_collection']
#     query = {
#         "user_id": user_id,
#         "file_id": file_id,
#         "id": int(concept_id),
#     }

#     update_request = {key: item for key, item in update_request.items() if key != "_id"}

#     update_data = {"$set": update_request}
#     logger.info("update data qurey")
#     # logger.info(query)
#     # logger.info(update_data)
#     if not update_data:
#         logger.info("no update data")
#     result = await concepts_collection.update_one(query, update_data)

#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="Concept not found")

#     if result.modified_count == 0:
#         raise HTTPException(status_code=400, detail="No changes made to the concept")

#     return {"message": "Concept updated successfully"}


# @app.post("/users/{user_id}/files/{file_id}/concepts", summary="Batch Insert Concepts", dependencies=[Depends(validate_token)])
# async def batch_insert_concepts(user_id: str, file_id: str, request: List[Any] = Body(...) ):
#     concepts_collection = db['concepts_collection']

#     # Prepare the concepts for insertion
#     concepts_to_insert = request

#     # Insert the concepts
#     result = await concepts_collection.insert_many(concepts_to_insert)
#     return {"message": f"{len(result.inserted_ids)} concepts inserted successfully"}


# @app.get('/job/{job_id}', 
#          summary="Retrieve Job Details",
#          description="Retrieves the details of a specific job from MongoDB using the job ID. "
#                      "The endpoint returns all the fields present in the job document, "
#                      "including its status, requests, and other information.",
#          dependencies=[Depends(validate_token)]
# )
# async def get_job(job_id: str = Path(..., description="The ID of the job to retrieve")) -> dict:
#     try:
#         object_id = ObjectId(job_id)
#         job = await jobs_collection.find_one({"_id": object_id})

#         if not job:
#             raise HTTPException(status_code=404, detail="Job not found")

#         # Convert ObjectId to string for JSON serialization
#         job['_id'] = str(job['_id'])
#         return job
#     except Exception as e:
#         raise e
#         raise HTTPException(status_code=500, detail=str(e))


class BulkSearchRequest(BaseModel):
    queries: List[str]
    description: List[str] | None = None
    source: List[str] | None = None
    mapping: str
    if_fuzzy: bool = True
    openai: bool = False

# @app.post('/bulk_search', response_model=Dict[str, Any], summary="Perform a bulk search.", description="If 'openai' flag is true, submit the search results as a job for further processing and return the job ID. Otherwise, return the search results directly.", dependencies=[Depends(validate_token)])
# async def bulk_search(request_data: BulkSearchRequest):
#     data = request_data
#     queries = data.queries  # Expecting an array of terms
#     description = data.description
#     sources = data.source
#     es_index = data.mapping
#     should = data.if_fuzzy
#     openai = data.openai


#     if openai:
#         embeddings = []
#         for query in queries:
#             job_response = await create_job({"requests": [{"model": 'text-embedding-3-small', "messages": query, "category": "embedding"}]})
#             # logger.info("openai got job response")
#             # logger.info(job_response)
#             job_id = job_response["job_id"]
#             embedding = await poll_for_job_completion(job_id)
#             if embedding is None:

#                 break
#             embeddings.append(embedding)

#     # Construct the bulk search request
#     bulk_search_body = []
#     for i, term in enumerate(queries):
#         header = {"index": es_index}
#         body = {
#             "size": 100,
#             "query": {
#                 "bool": {
#                     "should": [
#                         {"match": {
#                             "term": term,
#                         }}
                          
#                     ]
#                 }
#             }
#         }
#         if description and i < len(description):
#             body["query"]["bool"]["should"] = []
#             body["query"]["bool"]["should"] = [
#                 {"multi_match": {"query": description[i], "fields": ["term^2.5", "description^3","value^2"]}},
#                 {"multi_match": {"query": term, "fields": ["term^3", "description^2.5", "value^2"]}},
#                 # {"multi_match": {"query": description[i], "fields": ["value"]}},
#                 # {"multi_match": {"query": term, "fields": ["value"]}},
#             ] 
#             body["query"]["bool"]["minimum_should_match"] = 1


       

#         if openai and i < len(embeddings):
#             # body["query"]["bool"]["boost"] = 0.8
#             body["query"]["bool"]["should"].append({"knn": {
#                 "field": "Embedding",
#                 "query_vector": embeddings[i],
#                 "num_candidates": 50,
#                 # "k": 10,
#                 "boost": 0.2,
#                 "filter": {
#                     "terms":{
#                         "source":sources
#                     }
#                 }
#             }})

#         if sources:
#             body["query"]["bool"]["filter"] = {
#                 "terms": {
#                     "source": sources,
#                 }
#             }
#         bulk_search_body.append(header)
#         bulk_search_body.append(body)
#         logger.info("bulk search body")
#         logger.info(body)
#     # Execute the bulk search
#     try:
#         bulk_response = es.msearch(body=bulk_search_body)
#         all_results = []
#         for i, response in enumerate(bulk_response['responses']):
#             # logger.info("bulk response")
#             # logger.info(response)
#             hits = response['hits']['hits']
#             results = [{
#                 'score': hit['_score'],
#                 'conceptId': hit['_source'].get('concept_id'),
#                 'conceptCode': hit['_source'].get('code'),
#                 'conceptSource': hit['_source'].get('source'),
#                 'standardConcept': hit['_source'].get('term', ''),
#                 'description': hit['_source'].get('description', ''),
#                 'valueDomain': hit['_source'].get('source_document', {}).get('valueDomain', {}),
#             } for hit in hits]
#             all_results.append(results)

#         return {"results": all_results}

#     except Exception as e:
#         raise e
#         raise HTTPException(status_code=500, detail=str(e))


# async def poll_for_job_completion(job_id: str) -> List[float]:
#     counter = 0
#     while True:
#         if counter >= 10:
#             logger.warning("Fetching job results timed out."+ str(job_id))  # Log a warning
#             return None
#         job = await get_job(job_id)
#         if job["status"] == "completed":
#             return job["requests"][0]["result"]
#         counter += 1
#         await asyncio.sleep(1)


# @app.get('/mappings', response_model=List[str], summary="Retrieve top-level ontology data mappings.", description="This endpoint queries Elasticsearch to get all indices representing top-level ontology mappings. It filters out system indices (those starting with a dot '.') and returns a list of index names that represent different ontology mappings.", dependencies=[Depends(validate_token)])
# def get_mappings():
#     indices = es.indices.get_alias(index="*")
#     index_names = [val for val in list(indices.keys()) if val[0] != '.']
#     return index_names

# @app.get('/sources', response_model=List[str], summary="Retrieve a list of source vocabularies.", description="This endpoint returns all vocabularies from the given mappings.", dependencies=[Depends(validate_token)])
# async def get_sources(mapping: str):
#     try:
#         # Elasticsearch query for Terms Aggregation on the "source" field
#         query_body = {
#             "size": 0,  # We don't need actual documents, just the aggregation
#             "aggs": {
#                 "unique_sources": {
#                     "terms": {
#                         "field": "source",  # Adjust if your field name is different
#                         "size": 1000  # Adjust the size as needed
#                     }
#                 }
#             }
#         }

#         response = es.search(index=mapping, body=query_body)
#         sources = [bucket['key'] for bucket in response['aggregations']['unique_sources']['buckets']]
#         return sources
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001
    )

import datetime
import hashlib
import time
import os
import asyncio
import uuid
# from elasticsearch import Elasticsearch
from elasticsearch import AsyncElasticsearch
import jwt
from motor.motor_asyncio import AsyncIOMotorClient
import json
import httpx
import sys
import logging
from bson import json_util

from contextlib import asynccontextmanager
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # Create the Elasticsearch
    global es
    es = AsyncElasticsearch(os.environ['ES_PATH'])
    logging.info('* connected to elasticsearch at %s' % os.environ['ES_PATH'])

    # Create the MongoDB client
    global db
    mongo_client = AsyncIOMotorClient(os.environ['MONGODB_URI'])
    db = mongo_client.get_database()
    logging.info('* connected to mongodb at %s' % os.environ['MONGODB_URI'])

    # serve the app
    yield

    # close app
    await es.close()
    await mongo_client.close()


# Create the FastAPI app
app = FastAPI(
    root_path=os.environ['ROOT_PATH'],
    lifespan=lifespan,
)

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

# all the collections
MONGO_ALL_COLLECTION_NAMES = [
    'users',          # user information
    'projects',       # project information
    'files',          # file information of projects
    'concepts',       # concepts loaded from files
    'file_users',     # user permissions on each file
    'jobs',           # jobs for OpenAI
    'mappings',       # mappings between concepts and CDEs
]


###########################################################
# User authentication related functions
###########################################################
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
# scheme for the JWT cookie for general user
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

# scheme for the x-token header for admin access
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
        _user = await db.users.find_one({
            "email": user_login.email
        })

        logging.debug(f"User login: get user {_user}")

        if _user is None:
            return {
                "success": False,
                "message": "User not found"
            }

        else:
            # check password
            if _user['password'] == hashlib.md5(user_login.password.encode()).hexdigest():
                # ok, password is correct
                user2 = formatUser(_user)
                token = sign_jwt(user2)
                logging.info(f"User login: existing user {user2['email']}")

            else:
                return {
                    "success": False,
                    "message": "Username or password incorrect"
                }

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
            "access_token": token,
            "user": formatUser(_user)
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
    logging.info("get myself")

    _user = await db.users.find_one({
        "email": current_user['email']
    })

    return {
        'success': True,
        'user': formatUser(_user)
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
    _user = current_user
    logging.debug('* refresh token for user %s' % _user)

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
@app.get('/admin/test', tags=["admin"])
async def admin_test(
    request: Request,
    x_token: str = Depends(authXTokenHeader)
):
    '''
    Test the admin token
    '''
    return {
        'success': True,
        'message': 'admin test ok'
    }


@app.post("/admin/init_database", tags=["admin"])
async def admin_init_database(
    request: Request,
    x_token: str = Depends(authXTokenHeader)
):
    '''
    Initialize the database
    '''
    logging.info("init database")
    # create collection `users` if not exist
    existing_collections = await db.list_collection_names()

    for collection_name in MONGO_ALL_COLLECTION_NAMES:
        if collection_name in existing_collections:
            # ok, this collection exists
            logging.info(f"* found collection `{collection_name}` exists")
        else:
            # not found, create this collection!
            await db.create_collection(collection_name)
            logging.info(f"* created collection `{collection_name}`")
            
            if collection_name == 'users':
                # add a default admin
                admin = {
                    "user_id": str(uuid.uuid4()),
                    "email": os.environ['ADMIN_EMAIL'],
                    "name": os.environ['ADMIN_NAME'],
                    "role": "admin",
                    "password": hashlib.md5(os.environ['ADMIN_PASSWORD'].encode()).hexdigest()
                }
                await db.users.insert_one(admin)
                logging.info(f"* created admin {admin['email']}")

    return {
        'success': True,
        'message': 'database initialized'
    }


@app.post("/admin/init_elasticsearch", tags=["admin"])
async def admin_init_elasticsearch(
    request: Request,
    x_token: str = Depends(authXTokenHeader)
):
    '''
    Initialize the elasticsearch
    '''
    indexes = [
        { "filename": "cde-sample-cancer", "index_name": "nih-cde-cancer" },
        { "filename": "cde-sample-general", "index_name": "nih-cde-general" },
        { "filename": "cde-sample-covid19", "index_name": "nih-cde-covid19" },
    ]

    for idx in indexes:
        index_name = idx['index_name']
        filename = idx['filename']

        if es.indices.exists(index=index_name):
            logging.info(f"* found index `{index_name}` exists")
            continue
        else:
            es.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "source": {
                                "type": "keyword",
                            },
                            "term": {
                                "type": "text",
                            },
                            "description": {
                                "type": "text",
                            },
                            "value": {
                                "type": "text",
                            },
                        }
                    }
                }
            )
            logging.info(f"* created index `{index_name}`")

        # get the current file location based __FILE__
        current_file = os.path.realpath(__file__)
        current_dir = os.path.dirname(current_file)
        data_file = os.path.join(current_dir, f"./samples/{filename}.json")
        logging.info(f"* loading data from {data_file}")

        # load data from the file
        with open(data_file, 'r') as f:
            data = json.load(f)
            logging.info(f"* loaded {len(data)} data from {data_file}")

            # insert data into the index
            for item in data:
                # add concept_id
                item['concept_id'] = item['tinyId']
                item['code'] = item['tinyId']

                # add a column called source
                item['source'] = item['stewardOrg']['name']

                # add term, description to the source
                item['term'] = item['designations'][0]['designation']
                item['description'] = item['definitions'][0]['definition'] if len(item['definitions']) > 0 else ""

                # add value if it has
                if len(item['valueDomain']['permissibleValues']) > 0:
                    item['value'] = "|".join(map(lambda x: x['permissibleValue'], item['valueDomain']['permissibleValues']))

                # insert the item
                await es.index(index=index_name, body=item)
            
            logging.info(f"* inserted {len(data)} data into {index_name}")

    return {
        'success': True,
        'message': 'elasticsearch initialized'
    }

class UserRegisterModel(BaseModel):
    email: str | None
    name: str | None
    role: str | None
    password: str | None

@app.post("/admin/register_user", tags=["admin"])
async def admin_register_user(
    request: Request,
    user_register: UserRegisterModel,
):
    '''
    User register
    '''
    if user_register.email is None or \
        user_register.name == None or \
        user_register.role == None or \
        user_register.password == None:

        raise HTTPException(status_code=400, detail="email, name, and password are required")
    
    # find user by email
    _user = await db.users.find_one({
        "email": user_register.email
    })
    logging.debug(f"User register: get user {_user}")

    if _user is None:
        # create this user
        new_user = {
            "user_id": str(uuid.uuid4()),
            "email": user_register.email,
            "name": user_register.name,
            "role": user_register.role,
            # hash the password to avoid saving plain text
            "password": hashlib.md5(user_register.password.encode()).hexdigest()
        }
        await db.users.insert_one(new_user)

        return {
            'success': True,
            'message': 'user created',
            'user': formatUser(new_user)
        }

    return {
        'success': False,
        'message': 'user exists',
        'user': formatUser(_user)
    }


@app.get('/admin/get_all_users', tags=["admin"])
async def admin_get_all_users(
    request: Request,
    x_token: str = Depends(authXTokenHeader)
):
    '''
    Get all users
    '''
    logging.info("get all users")

    users = await db.users.find().to_list(length=None)
    logging.debug(f"* found {len(users)} users")

    return {
        'success': True,
        'message': 'get all %s users' % len(users),
        'users': formatUsers(users)
    }


@app.get('/admin/get_all_projects', tags=["admin"])
async def admin_get_all_projects(
    request: Request,
    x_token: str = Depends(authXTokenHeader)
):
    '''
    Get all projects
    '''
    logging.info("get all projects")

    projects = await db.projects.find().to_list(length=None)
    logging.debug(f"* found {len(projects)} projects")

    return {
        'success': True,
        'message': 'get all %s projects' % len(projects),
        'projects': formatProjects(projects)
    }


class AdminClearDatabaseModel(BaseModel):
    # collections to exclude from deletion
    exclude_collections: List[str] = []

@app.post("/admin/clear_database", tags=["admin"])
async def admin_clear_database(
    request: Request,
    data: AdminClearDatabaseModel | None = None,
    x_token: str = Depends(authXTokenHeader)
):
    '''
    Clear the database
    '''
    existing_collections = await db.list_collection_names()

    for collection_name in MONGO_ALL_COLLECTION_NAMES:
        # skip the excluded collections
        if data is not None and collection_name in data.exclude_collections:
            logging.info(f"* skip specific collection `{collection_name}`")
            continue

        if collection_name in existing_collections:
            await db[collection_name].drop()
            logging.info(f"* dropped collection `{collection_name}`")
        else:
            logging.info(f"* collection `{collection_name}` not found")

    return {
        'success': True,
        'message': 'all database collections cleared, except %s' % data
    }


@app.post("/admin/clear_elasticsearch", tags=["admin"])
async def admin_clear_elasticsearch(
    request: Request,
    x_token: str = Depends(authXTokenHeader)
):
    '''
    Clear the elasticsearch
    '''
    indices = es.indices.get_alias(index="*")
    index_names = [val for val in list(indices.keys()) if val[0] != '.']
    for index_name in index_names:
        es.indices.delete(index=index_name)
        logging.info(f"* deleted index `{index_name}`")

    return {
        'success': True,
        'message': 'elasticsearch cleared'
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

###########################################################
# General APIs
###########################################################
@app.get('/get_stats', tags=["general"])
async def get_stats(
    request: Request,
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Get stats
    '''
    logging.info("get stats")

    # get the number of projects of the current user
    n_projects = await db.projects.count_documents({
        "members": {
            "$elemMatch": {
                "user_id": current_user['user_id']
            }
        }
    })

    n_files = await db.files.count_documents({
        "project_id": {
            "$in": [
                project['project_id'] for project in await db.projects.find({
                    "members.user_id": current_user['user_id']
                }, {"project_id": 1}).to_list(length=None)
            ]
        }
    })
     

    # get the number of concepts of the current user
    n_concepts = await db.concepts.count_documents({
        "file_id": {
            "$in": [
                file['file_id'] for file in await db.files.find({
                    "project_id": {
                        "$in": [
                            project['project_id'] for project in await db.projects.find({
                                "members.user_id": current_user['user_id']
                            }, {"project_id": 1}).to_list(length=None)
                        ]
                    }
                }, {"file_id": 1}).to_list(length=None)
            ]
        }
    })

    # get the number of mappings of the current user
    n_mappings = await db.mappings.count_documents({
        "user_id": current_user['user_id']
    })

    return {
        'success': True,
        'stats': {
            'n_projects': n_projects,
            'n_files': n_files,
            'n_concepts': n_concepts,
            'n_mappings': n_mappings,
        }
    }

###########################################################
# Project related APIs
###########################################################
@app.get('/get_project', tags=["project"])
async def get_project(
    request: Request,
    project_id: str,
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Get a project
    '''
    logging.info("get project")

    project = await db.projects.find_one({
        "project_id": project_id,
        "user_id": current_user['user_id']
    })

    # ok, try to find participated projects

    # oh, still none, we will return None
    if project is None:
        return {
            'success': False,
            'project': None
        }
    
    # ok, we found the project
    # let's extend the member information with email and name for frontend
    for member in project['members']:
        user = await db.users.find_one({
            "user_id": member['user_id']
        })
        member['email'] = user['email']
        member['name'] = user['name']

    # add a statistics to the project
    project['n_files'] = await db.files.count_documents({
        "project_id": project['project_id']
    })
    
    return {
        'success': True,
        'project': formatProject(project)
    }


@app.get('/get_projects', tags=["project"])
async def get_projects(
    request: Request,
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Get all projects of the current user
    '''
    logging.info("get projects")

    start_time = time.time()
    projects = await db.projects.find({
        "user_id": current_user['user_id']
    }).to_list(length=None)

    #if no projects, try to find the project with the member
    if len(projects) == 0:
        projects = await db.projects.find({
            "members": {
                "$elemMatch": {
                    "user_id": current_user['user_id']
                }
            }
        }).to_list(length=None)

    # for each project, add members' email and name
    for project in projects:
        for member in project['members']:
            user = await db.users.find_one({
                "user_id": member['user_id']
            })
            member['email'] = user['email']
            member['name'] = user['name']
    end_time = time.time()
    logging.info(f"taken to retrieve projects: {end_time - start_time} seconds")

    # add statistics to the projects
    for project in projects:
        project['n_files'] = await db.files.count_documents({
            "project_id": project['project_id']
        })

    return {
        'success': True,
        'message': 'get all %s projects (%s seconds)' % (len(projects), end_time - start_time),
        'projects': formatProjects(projects)
    }

@app.post('/create_project', tags=["project"])
async def create_project(
    request: Request,
    project_data: Dict[str, Any],
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Create a project
    '''
    logging.info("create project")

    # create project_id
    project_data['project_id'] = str(uuid.uuid4())

    # set the user_id using the current user
    project_data['user_id'] = current_user['user_id']

    # add self as the owner
    project_data['members'] = [
        { "user_id": current_user['user_id'], "role": "owner" }
    ]

    # set the created and updated time
    project_data['created'] = datetime.datetime.now()
    project_data['updated'] = datetime.datetime.now()

    result = await db.projects.insert_one(project_data)

    return {
        'success': True,
        'message': 'Project created successfully',
        'project': formatProject(project_data)
    }

class DeleteProjectModel(BaseModel):
    project_id: str

@app.post('/delete_project', tags=["project"])
async def delete_project(
    request: Request,
    project: DeleteProjectModel,
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Delete a project
    '''
    project_id = project.project_id
    logging.info("delete project")

    project = await db.projects.find_one({
        "project_id": project_id,
        "user_id": current_user['user_id']
    })

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    result = await db.projects.delete_one({
        "project_id": project_id,
        "user_id": current_user['user_id']
    })

    return {
        'success': True,
        'message': 'Project deleted successfully'
    }


class AddUserToProjectByEmailModel(BaseModel):
    project_id: str
    email: str
    role: str

@app.post('/add_user_to_project_by_email', tags=["project"])
async def add_user_to_project_by_email(
    request: Request,
    data: AddUserToProjectByEmailModel,
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Add a user to a project
    '''
    logging.info("add user to project")

    # check whether the current user is the owner of this project
    project = await db.projects.find_one({
        "project_id": data.project_id,
        "user_id": current_user['user_id']
    })

    if project is None:
        raise HTTPException(status_code=404, detail="Not owner of this project")
    
    # check whether the user is in the database
    user = await db.users.find_one({
        "email": data.email
    })

    if user is None:
        return {
            'success': False,
            'message': 'User [%s] not found' % data.email
        }
    
    # check if this user['user_id'] is already in the project['members']
    # if so, we will return False
    if any(member['user_id'] == user['user_id'] for member in project['members']):
        return {
            'success': False,
            'message': 'User [%s] already in the project' % data.email
        }

    # add this user to the project's members
    _ = await db.projects.update_one(
        {"project_id": data.project_id},
        {"$push": {
            "members": {
                "user_id": user['user_id'],
                "role": data.role
            }
        }}
    )

    return {
        'success': True,
        'message': f'User [{data.email}] is added to project as [{data.role}] successfully',
    }

class RemoveUserFromProjectByEmailModel(BaseModel):
    project_id: str
    user_id: str

@app.post('/remove_user_from_project', tags=["project"])
async def remove_user_from_project(
    request: Request,
    data: RemoveUserFromProjectByEmailModel,
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Remove a user from a project
    '''
    logging.info("remove user from project")

    # check whether the current user is the owner of this project
    project = await db.projects.find_one({
        "project_id": data.project_id,
        "user_id": current_user['user_id']
    })

    remove_user = await db.users.find_one({
        "user_id": data.user_id
    })

    if project is None:
        raise HTTPException(status_code=404, detail="Not owner of this project")

    
    # if so, we will return False
    if not any(member['user_id'] == data.user_id for member in project['members']):
        return {
            'success': False,
            'message': f'User [{data.user_id}] not in the project'
        }

    # remove this user from the project's members
    _ = await db.projects.update_one(
        {"project_id": data.project_id},
        {"$pull": {
            "members": {
                "user_id": data.user_id
            }
        }}
    )

    return {
        'success': True,
        'message': f'User [{remove_user['email']}] is removed from project successfully',
    }

###########################################################
# File related APIs
###########################################################

@app.post("/upload_file", tags=["file"])
async def upload_file(
    request: Request,
    file_data: Dict[str, Any],
    current_user: dict = Depends(authJWTCookie), 
):
    '''
    Upload a file
    '''
    logging.debug('* got file data %s' % str(file_data))

    # find the project
    project = await db.projects.find_one({
        "project_id": file_data['project_id']
    })

    # if project is None, we will create a default project
    if project is None:
        # try to find the default project
        default_project = await db.projects.find_one({
            "name": 'Default Project',
            "user_id": current_user['user_id']
        })

        if default_project is None:
            # insert a default
            project = {
                "project_id": str(uuid.uuid4()),
                "name": "Default Project",
                "user_id": current_user['user_id'],
                'members': [
                    { 
                        "user_id": current_user['user_id'], "role": "owner"
                        }
                    ],
                "created": datetime.datetime.now(),
                "updated": datetime.datetime.now(),
            }

            await db.projects.insert_one(project)
            logging.debug(f"* created a default project {project['project_id']}")
        else:
            project = default_project
            logging.debug(f"* use the default project {project['project_id']}")
    else:
        logging.debug(f"* found project {project['project_id']}")

    # set the project_id using the project we found or created
    file_data['project_id'] = project['project_id']

    file_data['file_owner'] = current_user['user_id']

    # set the round of file, index is the round number, and detail is the dict
    file_data['round'] = [
            {
                "stage": "mapping", # mapping, reviewing, completed
                "review_round": 0
            }
        ]

    # get all the concepts from this file
    concepts = file_data.pop('concepts', None)

    # save all concepts
    if concepts:
        for concept in concepts:
            # add a concept_id
            concept['concept_id'] = str(uuid.uuid4())
            # add the project_id
            concept['project_id'] = project['project_id']
            # add the file_id
            concept['file_id'] = file_data['file_id']
            # add the user_id
            concept['user_id'] = current_user['user_id']
            await db.concepts.insert_one(concept)
        logging.debug(f"* saved {len(concepts)} concepts")

    # save the file data
    result = await db.files.insert_one(file_data)
    logging.debug(f"* saved file {file_data['file_id']}")

    return {
        'success': True,
        'message': 'User document created or updated successfully'
    }


@app.get('/get_files_by_project', tags=["file"])
async def get_files_by_project(
    request: Request,
    project_id: str,
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Get all files by project
    '''
    logging.info("get files by project")

    # get all files
    files = await db.files.find({
        "project_id": project_id
    }).to_list(length=None)

    # add stats to the files
    for file in files:
        file['n_concepts'] = await db.concepts.count_documents({
            "file_id": file['file_id']
        })

        # count the unique users who have mapped this file
        # and the `submitted` is true
        file['n_submitted'] = len(await db.mappings.distinct("user_id", {
            "file_id": file['file_id'],
            "submitted": True
        }))

    return {
        'success': True,
        'files': formatFiles(files)
    }

@app.post('/update_file', tags=["file"])
async def update_file(
    request: Request,
    file_data: Dict[str, Any],
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Update a file
    '''
    logging.info("update file")

    # get the file_id
    file_id = file_data['file_id']

    # get the file
    file = await db.files.find_one({
        "file_id": file_id
    })

    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    # update the file
    result = await db.files.update_one(
        {"file_id": file_id},
        {"$set": file_data},
    )

    return {
        'success': True,
        'message': 'File updated successfully',
        'file': formatFile(file_data)
    }

class DeleteFileModel(BaseModel):
    file_id: str
    
@app.post('/delete_file', tags=["file"])
async def delete_file(
    request: Request,
    delete_file_data: DeleteFileModel,
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Delete a file
    '''
    file_id = delete_file_data.file_id
    logging.info("delete file %s" % file_id)

    # get the file
    file = await db.files.find_one({
        "file_id": file_id,
        "file_owner": current_user['user_id']
    })

    if file is None:
        logging.error(f"* not found delete file {file_id} owned by {current_user['user_id']}")
        raise HTTPException(status_code=404, detail="File not found")
    
    # delete the file
    result = await db.files.delete_one({
        "file_id": file_id,
        "file_owner": current_user['user_id']
    })

    return {
        'success': True,
        'message': 'File deleted successfully'
    }


@app.get('/save_file', tags=["file"])
async def save_file(
    request: Request,
    file_id: str,
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Save a file
    '''
    logging.info("save file")

    # get the file
    file = await db.files.find_one({
        "file_id": file_id
    })

    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    # check ownership of this file for this user
    flag_has_ownership = file['file_owner'] == current_user['user_id'] 
    logging.debug(f"* check ownership of file {file_id} for user {current_user['user_id']} = {flag_has_ownership}")

    # check permission of this file for this user
    permission = await db.projects.find_one({
        "project_id": file['project_id'],
        "members": {
            "$elemMatch": {
                "user_id": current_user['user_id']
            }
        }
    })
    logging.debug(f"* check permission of file {file_id} for user {current_user['user_id']} = {permission is not None}")

    if flag_has_ownership:
        # ok we have the ownership, we can pass
        pass

    elif permission:
        pass
    
    else:
        # no ownership and no permission, we will raise an error
        raise HTTPException(status_code=403, detail="No permission on the requested file")

    # get all concepts
    concepts = await db.concepts.find({
        "file_id": file_id
    }).to_list(length=None)

    mappings = await db.mappings.find({
        "concept_id": {"$in": [concept['concept_id'] for concept in concepts]},
        "user_id": current_user['user_id']
    }).to_list(length=None)

    # post-processing the final output
    # delete file_id, project_id
    file.pop('file_id')
    file.pop('project_id')

    # delete file_id, project_id, and user_id from concepts
    for concept in concepts:
        concept.pop('file_id')
        concept.pop('project_id')
        concept.pop('user_id')

    # delete mapping_id, user_id, and source from mappings
    for mapping in mappings:
        mapping.pop('mapping_id')
        mapping.pop('user_id')
        mapping.pop('source')
    
    #point mappings' concept_id to the index of the concept
    for mapping in mappings:
        for i, concept in enumerate(concepts):
            if concept['concept_id'] == mapping['concept_id']:
                mapping['concept_id'] = concept['id']
                break
    
    #remove concept_id from concepts
    for concept in concepts:
        concept.pop('concept_id')

    return {
        'file': formatFile(file),
        'concepts': formatConcepts(concepts),
        'mappings': formatMappings(mappings)
    }

class SubmitMappingWorkModel(BaseModel):
    file_id: str

@app.post('/submit_mapping_work', tags=["file"])
async def submit_mapping_work(
    request: Request,
    file_id: SubmitMappingWorkModel,
    current_user: dict = Depends(authJWTCookie),
): 
    file_id = file_id.file_id
    logging.info(f"submit mapping work for file {file_id}")
    
    # get the file
    file = await db.files.find_one({
        "file_id": file_id
    })
    # check if the file exists
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    # get the round of the file
    file_round = len(file['round']) - 1
    if file['round'][file_round]['stage'] != "mapping":
        raise HTTPException(status_code=403, detail="Not in mapping stage")
    
    # get all concepts
    concepts = await db.concepts.find({
        "file_id": file_id
    }).to_list(length=None)
    
    # get all mappings
    mappings = await db.mappings.find({
        "concept_id": {"$in": [concept['concept_id'] for concept in concepts]},
        "user_id": current_user['user_id'],
        "round": file_round
    }).to_list(length=None)

    # check if all concepts have been mapped
    if len(mappings) != len(concepts):
        return {
        'success': False,
        'message': 'Not all concepts have been mapped'
    }

    # # check if all mappings already submitted (temporary disabled)
    # if all(mapping['submitted'] for mapping in mappings):
    #     raise HTTPException(status_code=403, detail="All mappings have been submitted")
    
    # update all mappings submitted as True
    for mapping in mappings:
        await db.mappings.update_one(
            {"mapping_id": mapping['mapping_id']},
            {"$set": {
                "submitted": True
            }}
        )
    return {
        'success': True,
        'message': 'Mapping work submitted successfully'
    }
# @app.get('/assign_file', tags=["file"])
# async def assign_file(
#     request: Request,
#     file_id: str,
#     user_id: str,
#     current_user: dict = Depends(authJWTCookie),
# ):
#     '''
#     Assign a file to a user
#     '''
#     # Debug: check the file_id user_id and current user
#     logging.info(f"assign file {file_id} to user {user_id} by {current_user['user_id']}")
    
#     # get the file
#     file = await db.files.find_one({
#         "file_id": file_id
#     })
#     if file is None:
#         raise HTTPException(status_code=404, detail="File not found")
    
#     # check ownership of this file for this user
#     flag_has_ownership = file['file_owner'] == current_user['user_id']
#     logging.debug(f"* check ownership of file {file_id} for user {current_user['user_id']} = {flag_has_ownership}")

#     if flag_has_ownership:
#         # ok we have the ownership, we can pass
#         pass
#     else:
#         raise HTTPException(status_code=403, detail="Permission denied")
    
#     # assign the file to the user
#     result = await db.files.update_one(
#         {"file_id": file_id},
#         {"$set": {
#             f".{user_id}": 1
#         }}
#     )
#     logger.info(f"* assigned file {file_id} to user {user_id}")
#     return {
#         'success': True,
#         'message': 'File assigned successfully'
#     }


###########################################################
# Concepts related APIs
###########################################################

@app.get('/get_concepts_by_file', tags=["concept"])
async def get_concepts_by_file(
    request: Request,
    file_id: str,
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Get all concepts by file
    '''
    logging.info("get concepts by file")

    # get the file first
    file = await db.files.find_one({
        "file_id": file_id
    })

    # if file is None, we will raise an error to the user
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    # check ownership of this file for this user
    flag_has_ownership = file['file_owner'] == current_user['user_id']
    logging.debug(f"* check ownership of file {file_id} for user {current_user['user_id']} = {flag_has_ownership}")

    # check permission of this file for this user
    permission = await db.projects.find_one({
        "project_id": file['project_id'],
        "members": {
            "$elemMatch": {
                "user_id": current_user['user_id']
            }
        }
    })  
    logging.debug(f"* check permission of file {file_id} for user {current_user['user_id']} = {permission is not None}")

    if flag_has_ownership:
        # ok we have the ownership, we can pass
        pass

    elif permission:
    #not owner but has permission, we can pass
        pass
    
    else:
        # no ownership and no permission, we will raise an error
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # get the round of the file by looping through the files['round'] and find the last file['round']['stage'] == "mapping"
    round = len(file['round']) - 1
    
    logging.debug(f"* get round of file {file_id} = {round}")
    # get all concepts
    concepts = await db.concepts.find({
        "file_id": file_id
    }).to_list(length=None)

    mappings = await db.mappings.find({
        "concept_id": {"$in": [concept['concept_id'] for concept in concepts]},
        "user_id": current_user['user_id'],
        "round": round
    }).to_list(length=None)

    return {
        'success': True,
        'concepts': formatConcepts(concepts),
        'mappings': formatMappings(mappings)
    }

###########################################################
# Mapping data related APIs
###########################################################

@app.get('/get_sources', tags=["mapping"])
async def get_sources(
    request: Request
):
    '''
    Get all sources for mapping
    '''
    logging.info("get sources and collections")

    indices = await es.indices.get_alias(index="*")
    index_names = [val for val in list(indices.keys()) if val[0] != '.']
    return {
        'success': True,
        'sources': index_names
    }

@app.get('/get_collections_by_source', tags=["mapping"])
async def get_collections_by_source(
    request: Request,
    source: str
):
    '''
    Get all collections for mapping
    '''
    logging.info("get collections")

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

        response = await es.search(index=source, body=query_body)
        sources = [bucket['key'] for bucket in response['aggregations']['unique_sources']['buckets']]
        return {
            'success': True,
            'collections': sources
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

class SearchModel(BaseModel):
    source: str | None = None
    collections: List[str]
    queries: List[Dict[str, Any]]  # Allow None values in the dictionary
    flag_embedding: bool = False
    flag_openai: bool = False
    flag_fuzzy: bool = True
    size: int = 100
    

@app.post('/search', tags=["mapping"])
async def search(
    request: Request,
    search_data: SearchModel,
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Search data
    '''
    logging.info("search")

    if search_data.source is None:
        raise HTTPException(status_code=400, detail="source is required")

    bulk_search_body = []
    for query in search_data.queries:
        # search header
        header = {"index": search_data.source}

        # search body
        body = {
            'size': search_data.size,
            'query': {
                'bool': {
                    'should': [
                        {"multi_match": {"query": query['description'], "fields": ["term^2.5", "description^3","value^2"]}},
                        {"multi_match": {"query": query['term'], "fields": ["term^3", "description^2.5", "value^2"]}},
                    ],
                    'minimum_should_match': 1
                }
            }
        }

        # add the collection filter
        if search_data.collections:
            body['query']['bool']['filter'] = {
                'terms': {
                    'source': search_data.collections
                }
            }
        
        # add to the bulk search body
        bulk_search_body.append(header)
        bulk_search_body.append(body)

    # Execute the bulk search
    try:
        bulk_response = await es.msearch(body=bulk_search_body)
        all_results = []
        for i, response in enumerate(bulk_response['responses']):
            hits = response['hits']['hits']
            results = []
            for hit in hits:
                _r = {
                    'score': hit['_score'],
                    'term_id': hit['_source'].get('concept_id'),
                    'term_code': hit['_source'].get('code'),
                    'term_source': hit['_source'].get('source'),

                    'term': hit['_source'].get('term'),
                    'description': hit['_source'].get('description'),
                    'values': [],
                }
                # parse values
                _value = hit['_source'].get('value')
                if _value:
                    _values = _value.split("|")
                    for v in _values:
                        _r['values'].append(v.strip())
                else:
                    _r['values'] = []

                results.append(_r)
            all_results.append(results)

            # get the round of this file
            file = await db.files.find_one({
                "file_id": search_data.queries[i]['file_id']
            })
            round = len(file['round']) - 1

            # check whether we already have this in mappings 
            m = await db.mappings.find_one({
                "concept_id": search_data.queries[i]['concept_id'],
                "user_id": current_user['user_id'],
                "round": round
            })

            if m is None:
                # save the mapping
                mapping = {
                    "mapping_id": str(uuid.uuid4()),
                    "file_id": search_data.queries[i]['file_id'],
                    "concept_id": search_data.queries[i]['concept_id'],
                    "user_id": current_user['user_id'],
                    "round": round,
                    "submitted": False,
                    "source": search_data.source,
                    "collections": search_data.collections,
                    "selected_results": [],
                    "search_results": results,
                    "created": datetime.datetime.now(),
                    "updated": datetime.datetime.now(),
                }
                await db.mappings.insert_one(mapping)
                logging.debug(f"* saved mapping {mapping['mapping_id']}")
            else:
                # update the mapping
                _mapping = {
                    "source": search_data.source,
                    "collections": search_data.collections,
                    "search_results": results,
                    "updated": datetime.datetime.now(),
                }
                mapping = await db.mappings.update_one(
                    {"mapping_id": m['mapping_id']},
                    {"$set": _mapping},
                )
                logging.debug(f"* updated mapping {m['mapping_id']}")

        return {
            'success': True,
            'results': all_results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/get_mapping', tags=["mapping"])
async def get_mapping(
    request: Request,
    concept_id: str,
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Get mapping by concept_id
    '''
    logging.info("get mapping")

    m = await db.mappings.find_one({
        "concept_id": concept_id,
        "user_id": current_user['user_id']
    })

    if m is None:
        return {
            'success': True,
            'message': []
        }
    
    return {
        'success': True,
        'mapping': formatMapping(m)
    }


class UpdateSelectedResultsModel(BaseModel):
    concept_id: str
    selected_results: List[Dict[str, Any]]

@app.post('/update_selected_results', tags=["mapping"])
async def update_selected_results(
    request: Request,
    update_data: UpdateSelectedResultsModel,
    current_user: dict = Depends(authJWTCookie),
):
    '''
    Update selected results
    '''
    logging.info("update selected results")

    # update the mapping by concept_id and user_id
    m = await db.mappings.find_one({
        "concept_id": update_data.concept_id,
        "user_id": current_user['user_id']
    })

    if m is None:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    # update the selected results
    _mapping = {
        "selected_results": update_data.selected_results,
        "updated": datetime.datetime.now(),
    }
    mapping = await db.mappings.update_one(
        {"mapping_id": m['mapping_id']},
        {"$set": _mapping},
    )

    return {
        'success': True,
        'message': 'Selected results updated successfully',
    }


# @app.post("/users/{user_id}", response_model=Dict[str, Any], summary="Create or Update User Document", dependencies=[Depends(validate_token)])
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


# class BulkSearchRequest(BaseModel):
#     queries: List[str]
#     description: List[str] | None = None
#     source: List[str] | None = None
#     mapping: str
#     if_fuzzy: bool = True
#     openai: bool = False

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
###########################################################
# Helper functions
###########################################################
def formatUser(user):
    user.pop('_id', None)
    user.pop('password', None)

    return user

def formatUsers(users):
    for user in users:
        user.pop('_id', None)
        user.pop('password', None)

    return users

def formatProject(project):
    project.pop('_id', None)

    return project

def formatProjects(projects):
    for project in projects:
        project.pop('_id', None)

    return projects

def formatFile(file):
    file.pop('_id', None)

    return file

def formatFiles(files):
    for file in files:
        file.pop('_id', None)

    return files

def formatConcept(concept):
    concept.pop('_id', None)

    return concept

def formatConcepts(concepts):
    for concept in concepts:
        concept.pop('_id', None)

    return concepts

def formatMapping(mapping):
    mapping.pop('_id', None)

    return mapping

def formatMappings(mappings):
    for mapping in mappings:
        mapping.pop('_id', None)

    return mappings

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001
    )

# CDE Platform

A platform for CDE related tasks, such as mapping, reviewing, creating, and updating CDEs.

# Development

## Docker compose

You can use docker compose to create an environment for development.

First, create the `.env` file for backend service. For development, you don't need to change the values for local development.

```bash
cp api/dotenv.tpl api/.env
```

Then, use docker compose file for development.

```bash
cd conf/dev
docker compose up --build -d
```

Then, you should be able to access the backend service at:

- UI: `http://localhost:5173`
- API: `http://localhost:8001`

If you change the `.env` file, you need to restart the container to apply the changes. For example, the following command will restart the backend service.

```bash
docker compose restart api
```

If still something wrong, just rebuild the container.

```bash
docker compose up --build -d
```

## Manual setup

If you want to setup the environment manually, you can follow the steps below. 

### Backend

First, create the `.env` file for backend service. For development, you don't need to change the values for local development.

```bash
cp api/dotenv.tpl api/.env
```

Then, install the dependencies in a virtual env.

```bash
cd api
pip install -r requirements.txt
```

Then, you can run the backend service.

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Frontend

Install the dependencies.

```bash
cd web
npm install
```

Then update the config, if needed.

```bash
cp dotenv.tpl .env
```

Then, you can run the frontend service.

```bash
npx vite --host 0.0.0.0 --port 5173
```

Then, you should be able to access the frontend service at `http://localhost:5173`.


# Deployment

Please use docker to deploy the service. 

TBD

# Change log

## 0.8.2

- Bug fixes
- Add search results sorting function
- Added accept suggestions function

## 0.8.1

- Added edit comments function
- Revised some UI

## 0.8.0
- Added basic mapping function
- Added review function
- Added grand review function
- Added finalize file and multi round review function

## 0.7.2

- Added user registration and login
- Added file upload
- Added file list
- Added project creation
- Added project list
- Added project detail

## 0.7.0

- Added other pages and views

## 0.6.0

- Added login page and own login logics
- Added user registration APIs

## 0.5.0

- Added main.py for backend service
- Added basic APIs for admin

## 0.4.0

- Added docker compose file for development

## 0.3.0

- Implemented basic UI using Primevue
- Added homepage

## 0.2.0

- Added api and ui folders

## 0.1.0

- Initialized the repo version
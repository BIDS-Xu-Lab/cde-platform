# CDE Platform

A platform for managing CDEs

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

Then, you can run the frontend service.

```bash
npx vite --host 0.0.0.0 --port 5173
```

Then, you should be able to access the frontend service at `http://localhost:5173`.
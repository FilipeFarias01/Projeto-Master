from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers.tarefas import router as tarefas_router

app = FastAPI(
    title='API de Tarefas',
    description='API para gerenciamento de tarefas',
    version='1.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(tarefas_router)

app.mount(
    '/',
    StaticFiles(directory='front', html=True),
    name='front'
)

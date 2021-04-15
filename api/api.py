import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import trades_router, quotes_router
import config

def serve():
    uvicorn.run(
        'api:api',
        host=config.http_host,
        port=config.http_port,
        reload=True
    )

api = FastAPI()

# api.include_router(
#     users.router,
#     tags=['users'],
#     prefix='/users'
# )
api.include_router(
    trades_router.router,
    tags=['trades'],
    prefix='/trades'
)
api.include_router(
    quotes_router.router,
    tags=['quotes'],
    prefix='/quotes'
)

origins = [
    'http://localhost:8080',
    'http://127.0.0.1:8080',
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@api.on_event('startup')
async def startup():
    config.load_api_keys()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from authentication.routers import router as auth_router
from market.routers import router as market_router


app = FastAPI()

app.include_router(auth_router, prefix='/api')
app.include_router(market_router, prefix='/api')

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/api')
async def root():
    return {'message': 'Portfolio app.'}

if '__name__' == '__main__':
    uvicorn.run(app, host='0.0.0.0', port='8000')


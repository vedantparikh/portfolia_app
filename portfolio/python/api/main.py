from fastapi import FastAPI

from market.stock import get_symbols

app = FastAPI()


@app.get("/symbols/")
async def symbols(name: str):

    return await get_symbols(name=name)
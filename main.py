from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import os, hmac, hashlib, time, requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")

def generar_firma(params: dict) -> str:
    sorted_params = sorted(params.items())
    query_string = '&'.join([f"{key}={value}" for key, value in sorted_params])
    return hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()

@app.post("/retirar")
def retirar(wallet: str = Form(...), amount: float = Form(...)):
    timestamp = str(int(time.time() * 1000))
    params = {
        "api_key": API_KEY,
        "timestamp": timestamp,
        "coin": "BTC",
        "address": wallet,
        "amount": str(amount),
        "chain": "BTC",
    }
    params["sign"] = generar_firma(params)

    response = requests.post("https://api.bybit.com/v5/asset/withdraw/create", data=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=500, detail=response.json())
from fastapi import FastAPI
from routes import router

app = FastAPI()
app.include_router(router)

# 서버 헬스 체크용
@app.get("/")
def read_root():
    return {"status": "ERP AI Server Running"}
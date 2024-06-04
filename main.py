from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sys
import yaml
from utils.summarize import LLMSummarizer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("template/index.html")


with open("./config/config.yaml", "rb") as f:
    config = yaml.safe_load(f)

rag_chain = LLMSummarizer(
            embedding_model=config["embedding_model"],
            llm_info=config["llm_config"],
            data_path=f"./data/{config['data']}",
            prompt_template=config["template"]
            )

class QueryRequest(BaseModel):
    query: str

class Response(BaseModel):
    answer: str

@app.post("/query", response_model=Response)
async def query_rag(request: QueryRequest):
    try:
        answer = rag_chain.ask(request.query)
        return Response(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def read_root():
    return {"message": "Analysis of last articles of Apple Stocks"}
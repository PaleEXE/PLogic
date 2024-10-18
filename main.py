import logging
from urllib.request import Request

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List
import json
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from PLogic import PExp


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExpressionInput(BaseModel):
    expression: str


class WhereInput(BaseModel):
    expression: str
    conditions: Dict[str, int]


@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Received request: {request.method} {request.url}")
    logger.info(f"Headers: {request.headers}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


@app.post("/evaluate")
async def evaluate_expression(inp: ExpressionInput):
    try:
        pexp = PExp(inp.expression).solve()
        df = pexp.df

        print("Truth Table:", df.to_json(orient="records"))  # Debugging line
        return {
            "expression": inp.expression,
            "truth_table": json.loads(df.to_json(orient="records"))
        }
    except Exception as e:
        print("Error in evaluate_expression:", str(e))  # Debugging line
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/compare")
async def compare_expressions(expressions: List[str]):
    if len(expressions) != 2:
        raise HTTPException(status_code=400, detail="Please provide exactly two expressions to compare")

    try:
        pexp1 = PExp(expressions[0]).solve()
        pexp2 = PExp(expressions[1]).solve()
        are_equal = pexp1 == pexp2
        return {
            "expressions": expressions,
            "are_equal": are_equal,
        }
    except Exception as e:
        print("Error in compare_expressions:", str(e))
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/where")
async def where_condition(inp: WhereInput):
    try:
        pexp = PExp(inp.expression).solve()
        result_df = pexp.where(**inp.conditions)
        print("Where Result:", result_df)
        return {
            "expression": inp.expression,
            "conditions": inp.conditions,
            "truth_table": json.loads(result_df.to_json(orient="records"))
        }
    except Exception as e:
        print("Error in where_condition:", str(e))  # Debugging line
        raise HTTPException(status_code=400, detail=str(e))


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    response = RedirectResponse(url="/static/favicon.ico")
    response.headers["Cache-Control"] = "no-store"  # Prevent caching
    return response


@app.get("/")
async def read_index():
    logger.info("Serving index.html")
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
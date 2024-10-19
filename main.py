import logging

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List
import json
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from PLogic import PExp

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
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
    """
    Evaluate the logical expression and return the truth table.
    """
    try:
        pexp = PExp(inp.expression).solve()
        df = pexp.df
        logger.info("Truth Table: %s", df.to_json(orient="records"))  # Log output for debugging
        return {
            "expression": inp.expression,
            "truth_table": json.loads(df.to_json(orient="records"))
        }
    except Exception as e:
        logger.error("Error in evaluate_expression: %s", str(e))  # Log error for debugging
        raise HTTPException(status_code=400, detail="Failed to evaluate expression.")


@app.post("/compare")
async def compare_expressions(expressions: List[str]):
    """
    Compare two logical expressions to determine if they are equivalent.
    """
    if len(expressions) != 2:
        raise HTTPException(status_code=400, detail="Please provide exactly two expressions to compare")

    try:
        pexp1 = PExp(expressions[0]).solve()
        pexp2 = PExp(expressions[1]).solve()

        are_equal = pexp1 == pexp2

        return {
            "expressions": expressions,
            "are_equal": are_equal
        }
    except Exception as e:
        logger.error("Error in compare_expressions: %s", str(e))
        raise HTTPException(status_code=400, detail="Failed to compare expressions.")


@app.post("/where")
async def where_condition(inp: WhereInput):
    """
    Apply conditions to the logical expression and return the filtered results.
    """
    try:
        pexp = PExp(inp.expression).solve()
        result_df = pexp.where(**inp.conditions)
        logger.info("Where Result: %s", result_df.to_json(orient="records"))  # Log output for debugging
        return {
            "expression": inp.expression,
            "conditions": inp.conditions,
            "truth_table": json.loads(result_df.to_json(orient="records"))
        }
    except Exception as e:
        logger.error("Error in where_condition: %s", str(e))  # Log error for debugging
        raise HTTPException(status_code=400, detail="Failed to apply where conditions.")


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

from fastapi import FastAPI
import uvicorn
from fastapi.responses import JSONResponse
import pandas as pd
import os

app = FastAPI()

@app.get("/points")
async def get_points():
    file_path = os.path.join("data", "Иннополис.csv")
    try:
        # Read the CSV file using pandas
        df = pd.read_csv(file_path, encoding="utf-8")
        points = df.to_dict(orient="records")  # Convert DataFrame to a list of dictionaries
    except FileNotFoundError:
        return {"error": "File not found"}
    except Exception as e:
        return {"error": str(e)}
    return {"points": points}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict this to specific domains)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/points")
async def get_points():
    file_path = os.path.join("data", "Иннополис.csv")
    try:
        # Read the CSV file using pandas
        df = pd.read_csv(file_path, encoding="utf-8")

        # Ensure 'Custom' is parsed as a list
        if "Custom" in df.columns:
            df["Custom"] = df["Custom"].apply(lambda x: eval(x) if isinstance(x, str) else x)

        points = df.to_dict(orient="records")  # Convert DataFrame to a list of dictionaries
    except FileNotFoundError:
        return {"error": "File not found"}
    except Exception as e:
        return {"error": str(e)}
    return {"points": points}

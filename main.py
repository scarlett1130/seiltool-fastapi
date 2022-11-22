from pickle import FALSE, TRUE
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
from models import SearchData, CategoryList
import logging
import uvicorn

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

logger = logging.getLogger(__name__)

@app.get("/", response_model=SearchData)
async def get_json_data(
    categories: str = None,
    keyword: str = "",
    page: int = 0,
    limit: int = 10
):
    categories = json.loads(categories) if categories is not None else []
    data = None
    try:
        with open("./api/search.json", "r") as json_file:
            data = json.load(json_file)
    except Exception as error:
        logger.error(f"Error reading json file: {error}")

    if data:
        if categories == [] and keyword == "":
            return { "data": data[page * limit: (page + 1) * limit], "total": len(data) }
        else:
            tmp = []
            for row in data:
                search_string = ""
                for item in row:
                    search_string += str(row[item]['content']) + "##"
                if search_string.__contains__(keyword) and (row['category']['content'] in categories or categories == []):
                    tmp.append(row)

            return { "data": tmp[page * limit: (page + 1) * limit], "total": len(tmp) }
            
    return { "status": 400, "message": "Bad Request" }
    #raise HTTPException(400, "Bad Request")

@app.get("/categories", response_model=CategoryList)
async def get():
    data = None
    try:
        with open("./api/search.json", "r") as json_file:
            data = json.load(json_file)
    except Exception as error:
        logger.error(f"Error reading json file: {error}")
    if data:
        obj_map = {}
        for row in data:
            if not obj_map.__contains__(row["category"]["content"]):
                obj_map[row["category"]["content"]] = row["category"]["content"]
        categories = obj_map.values()

        def keyToCode(k):
            return k['code']

        return { "data": sorted([{ "code": category } for category in categories if category is not None], key = keyToCode) }

    #raise HTTPException(400, "Bad Request")
    return { "status": 400, "message": "Bad Request" }
    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

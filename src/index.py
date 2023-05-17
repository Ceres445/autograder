import os
from typing import List
from fastapi import FastAPI, Request
from fastapi import UploadFile
import aiofiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.tester.autograder import autoeval

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/upload_files")
async def upload_program(files: List[UploadFile]):
    c = False
    json = False
    if len(files) != 2:
        return {
            "Result": "ERROR",
            "filenames": [file.filename for file in files],
            "error": "Wrong number of files",
        }
    if not os.path.exists("/tmp/files"):
        os.mkdir("/tmp/files")
    for file in files:
        if file.filename.endswith(".c"):
            destination_file_path = "/tmp/files/test.c"
            async with aiofiles.open(destination_file_path, "wb") as out_file:
                while content := await file.read(1024):  # async read file chunk
                    await out_file.write(content)  # async write file chunk
            c = True
        elif file.filename.endswith(".json"):
            destination_file_path = "/tmp/files/test.json"
            async with aiofiles.open(destination_file_path, "wb") as out_file:
                while content := await file.read(1024):
                    await out_file.write(content)
            json = True

    if c and json:
        return {"Result": "OK", "filenames": [file.filename for file in files]}
    else:
        if not c:
            return {
                "Result": "ERROR",
                "filenames": [file.filename for file in files],
                "error": "No C file",
            }
        else:
            return {
                "Result": "ERROR",
                "filenames": [file.filename for file in files],
                "error": "No JSON file",
            }


@app.get("/test")
async def test():
    if os.path.exists("/tmp/files/test.c") and os.path.exists("/tmp/files/test.json"):
        result = autoeval("/tmp/files/test.c", "/tmp/files/test.json")
        os.remove("/tmp/files/test.c")
        os.remove("/tmp/files/test.json")
        return {"Result": "OK", "content": result[0], "score": result[1]}
    else:
        return {"Result": "ERROR", "content": "Files don't exist"}

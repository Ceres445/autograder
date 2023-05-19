import os
from typing import List
from fastapi import FastAPI, Request
from fastapi import UploadFile
import aiofiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from src.tester.autograder import autoeval
import shutil

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

stats = {
    "total": 0,
    "success": 0,
    "visited": 0,
}


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    stats["visited"] += 1
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/stats")
async def stats_a():
    return {"Result": "OK", "stats": stats}


@app.post("/upload_files")
async def upload_program(files: List[UploadFile]):
    stats["total"] += 1
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


@app.post("/untar")
async def untar(file: UploadFile):
    if not file.filename.endswith(".tar.gz"):
        return {"Result": "ERROR", "error": "Wrong file extension"}
    if not os.path.exists("/tmp/files"):
        os.mkdir("/tmp/files")
    else:
        
        shutil.rmtree("/tmp/files", ignore_errors=True)
        os.mkdir("/tmp/files")

    destination_file_path = "/tmp/files/test.tar"
    async with aiofiles.open(destination_file_path, "wb") as out_file:
        while content := await file.read(1024):
            await out_file.write(content)
    os.system("tar -xf /tmp/files/test.tar -C /tmp/files")
    files = os.listdir("/tmp/files")
    for file in files:
        if file.endswith(".c"):
            return FileResponse(f"/tmp/files/{file}")
    return {"Result": "ERROR", "error": "No C file"}


@app.get("/test")
async def test():
    if os.path.exists("/tmp/files/test.c") and os.path.exists("/tmp/files/test.json"):
        result = autoeval("/tmp/files/test.c", "/tmp/files/test.json")
        os.remove("/tmp/files/test.c")
        os.remove("/tmp/files/test.json")
        stats["success"] += 1
        return {"Result": "OK", "content": result[0], "score": result[1]}
    else:
        return {"Result": "ERROR", "content": "Files don't exist"}

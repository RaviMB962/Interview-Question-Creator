from fastapi import FastAPI, Form, Request, Response, File, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
import uvicorn
import os
import aiofiles
import json
import csv
from src.helper import llm_pipeline

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name= "static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})




@app.post("/upload")
async def chat(request: Request, pdf_file: bytes = File(), filename: str = Form(...)):
    base_folder = "static/docs/"
    if not os.path.isdir(base_folder):
        os.makedirs(base_folder)
    pdf_file_name = os.path.join(base_folder, filename)

    async with aiofiles.open(pdf_filename, "wb") as f:
        await f.write(pdf_file)
    
    response_data = jsonable_encoder(json.dumps({"msg": "success", "pdf_filename": pdf_file_name}))
    res = Response(response_data)
    return res


def get_csv(filepath):
    answer_generation_chain, ques_list = llm_pipeline(file_path)
    base_folder = 'static/output/'
    if not os.path.isdir(base_folder):
        os.makedirs(base_folder)
    output_file =  base_folder+"QA.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Question", "Answer"]) #

        for question in ques_list:
            print("Question: ", question)
            answer = answer_generation_chain.run(question)
            print("Answer: ", answer)
            print("-------------------------------------------\n\n")

            csv_writer.writerow([question, answer])

    return output_file

@app.post("/analyze")
async def chat(request: Request, pdf_file_name: str = Form(...)):
    output_file = get_csv(pdf_file_name)
    response_data = jsonable_encoder(json.dumps({"output_file": output_file}))
    res = Response(response_data)
    return res


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

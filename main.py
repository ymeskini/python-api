from fastapi import BackgroundTasks, FastAPI
from pdf2image import convert_from_bytes
import tempfile
import urllib.request
import boto3
import io
import os
from datetime import datetime
import logging
import concurrent.futures

logging.getLogger().setLevel(logging.INFO)


app = FastAPI()

BUCKET = os.getenv("AWS_BUCKET")

s3 = boto3.client(
  service_name = "s3",
  endpoint_url = os.getenv("AWS_ENDPOINT_URL"),
  aws_access_key_id = os.getenv("AWS_ACCESS_ID"),
  aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
  region_name = "auto",
)

def upload_image_to_s3(image, fname):
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes.seek(0)
    s3.upload_fileobj(image_bytes, BUCKET, fname)
    image.close()
    logging.info(f'Uploaded {fname}')

def convert_pdf_to_jpg(response, author, bookId):
    with tempfile.TemporaryDirectory() as path:
        images_from_path = convert_from_bytes(response, output_folder=path)
        with concurrent.futures.ThreadPoolExecutor(10) as executor:
            for i, image in enumerate(images_from_path):
                fname = f'books/{author}/{bookId}/{i}.jpeg'
                executor.submit(upload_image_to_s3, image, fname)

@app.post("/books")
def read_root(url: str, author: str, bookId: str, background_tasks: BackgroundTasks):
    response = urllib.request.urlopen(url).read()
    background_tasks.add_task(convert_pdf_to_jpg, response, author, bookId)
    return {"success": True}

@app.get("/health")
def health():
    return {"success": True, "date": datetime.utcnow()}
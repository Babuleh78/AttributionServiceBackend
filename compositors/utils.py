
from minio import Minio
import random
from datetime import timedelta
from faker import Faker
import os
import unicodedata
import re

f = Faker("ru_RU")

def safe_filename(filename):
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return re.sub(r'_+', '_', filename).strip('_')

def upload_image_to_minio(django_file, bucket_name="services-images"):
    client = Minio(
        "minio:9000",  
        access_key="minio",        
        secret_key="minio123",     
        secure=False
    )

    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)

    original_name = os.path.basename(django_file.name)
    filename = safe_filename(original_name)

    django_file.seek(0)

    client.put_object(
        bucket_name,
        filename,
        data=django_file,
        length=django_file.size,
        content_type=django_file.content_type  
    )

    return f"http://localhost:9000/{bucket_name}/{filename}"

def delete_image_from_minio(image_url):
    if not image_url:
        return
    client = Minio(
        "minio:9000",          
        access_key="minio",    
        secret_key="minio123",
        secure=False
    )
    key = image_url.split('/')[-1]
    try:
        client.remove_object("services-images", key)
    except Exception as e:
        print(f"Ошибка при удалении изображения: {e}")

def get_minio_client():
    return Minio(
        os.getenv("MINIO_HOST", "localhost:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minio"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minio123"),
        secure=False
    )

def random_date(start_date="-1y", end_date="+1w"):
    return f.date_time_between(start_date=start_date, end_date=end_date)


def random_timedelta(factor=100):
    return timedelta(random.uniform(0, 1) * factor)



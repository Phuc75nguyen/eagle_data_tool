import os
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# 1. Initialize MinIO client
minio_client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False  # Running locally without HTTPS, set to False
)

BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")

def init_minio_bucket():
    """This function runs when the server starts to check if the bucket exists, if not, it will create it automatically"""
    try:
        found = minio_client.bucket_exists(BUCKET_NAME)
        if not found:
            minio_client.make_bucket(BUCKET_NAME)
            print(f"INFO: Created new MinIO bucket: '{BUCKET_NAME}'")
        else:
            print(f"INFO: MinIO bucket '{BUCKET_NAME}' already exists.")
    except Exception as e:
        print(f"ERROR: MinIO connection failed: {e}")

# Helper function for reuse
def upload_file_to_minio(file_stream, task_id: str, file_name: str, content_type: str, is_anonymized: bool = False):
    """
    is_anonymized = False -> Save to: {task_id}/original/{file_name}
    is_anonymized = True  -> Save to: {task_id}/anonymized/{file_name}
    """
    folder_name = "anonymized" if is_anonymized else "original"
    
    # This is where the folder is created on MinIO
    object_name = f"{task_id}/{folder_name}/{file_name}" 
    
    try:
        # Get file size
        file_stream.seek(0, 2)
        file_size = file_stream.tell()
        file_stream.seek(0)

        minio_client.put_object(
            bucket_name=BUCKET_NAME,
            object_name=object_name,
            data=file_stream,
            length=file_size,
            content_type=content_type
        )
        return object_name
    except Exception as e:
        print(f"MinIO Upload Error: {e}")
        raise e
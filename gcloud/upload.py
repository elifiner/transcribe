import os
from tqdm.std import tqdm
from distutils.command.upload import upload
from google.cloud import storage

def upload_to_bucket(blob_name, path_to_file, bucket_name):
    """ Upload data to a bucket"""

    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json('key.json')

    #print(buckets = list(storage_client.list_buckets())

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name, chunk_size=256*1024)

    with open(path_to_file, "rb") as in_file:
        total_bytes = os.fstat(in_file.fileno()).st_size
        with tqdm.wrapattr(in_file, "read", total=total_bytes, miniters=1, desc=blob_name) as file_obj:
            blob.upload_from_file(
                file_obj,
                # content_type=content_type,
                size=total_bytes,
            )
    return blob.public_url

upload_to_bucket('output.flac', 'output.flac', 'transcribe-audio-upload')

# print(upload_to_bucket('requirements.txt', 'requirements.txt', 'transcribe-audio-upload'))
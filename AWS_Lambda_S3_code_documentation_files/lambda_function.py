import boto3
import os
import sys
import uuid
from urllib.parse import unquote_plus
from PIL import Image
import PIL.Image

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

def resize_image(image_path, resized_path):
    with Image.open(image_path) as image:
        if image.width > 300 or image.height > 300:
            output_size = (300, 300)
            image.thumbnail(output_size)
            image.save(resized_path)
            return True
        else:
            return False
            # image.save(resized_path)

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        tmpkey = key.replace('/', '')
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
        upload_path = '/tmp/resized-{}'.format(tmpkey)
        s3_client.download_file(bucket, key, download_path)
        
        if resize_image(download_path, upload_path): #true
            ###
            s3_resource.Object(bucket, key).delete()
            ###
            s3_client.upload_file(upload_path, '{}'.format(bucket), '{}'.format(key))

        

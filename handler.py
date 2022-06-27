import os
import uuid
import json
import boto3
from datetime import datetime
from distutils.command.upload import upload
from email.mime import image
from urllib import response
from io import BytesIO
from PIL import Image, ImageOps

s3 = boto3.client('s3')
size = int(os.environ['THUMBNAIL_SIZE'])

def s3_thumbnail_generator(event, context):
    
    print("EVENT:::", event)

    bucket  = event['Records'][0]['s3']['bucket']['name']
    key     = event['Records'][0]['s3']['object']['key']
    imgSize = event['Records'][0]['s3']['object']['size']

    if (not key.endswith("-thumbnail.png")):
        image = getImageFromS3(bucket, key)
        thumbnail = createThumbnail(image)
        thumbnailKey = newFilename(key)

        url = uploadToS3(bucket, thumbnailKey, thumbnail, imgSize)

        return url

def getImageFromS3(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    imageContent = response['Body'].read()

    file = BytesIO(imageContent)
    img = Image.open(file)
    return img

def createThumbnail(image):
    return ImageOps.fit(image, (size, size), Image.ANTIALIAS)

def newFilename(key):
    keySplit = key.rsplit('.', 1)
    return keySplit[0] + "-thumbnail.png"

def uploadToS3(bucket, key, image, imageSize):
    # We're saving the image into a BytesIO object to avoid writing to disk
    thumbnail = BytesIO()

    image.save(thumbnail, 'PNG')
    thumbnail.seek(0)

    response = s3.put_object(
        ACL='public-read',
        Body=thumbnail,
        Bucket=bucket,
        ContentType='image/png',
        Key=key
    )

    # Debug
    print(response)

    url = '{}/{}/{}'.format(s3.meta.endpoint_url, bucket, key)

    # save image url to db:
    saveInfoOnDynamo(url_path= url, imgSize= imgSize)
    return url
        
def saveInfoOnDynamo(url, imgSize):
    return null
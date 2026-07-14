import json
import boto3
import uuid
import base64
import os

s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

def lambda_handler(event, context):
    try:
        # Debug mínimo (só se precisar)
        # print("Event keys:", list(event.keys()))
        
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body)
        
        headers = event.get('headers', {}) or {}
        content_type = headers.get('content-type', headers.get('Content-Type', ''))
        
        if 'multipart/form-data' not in content_type.lower():
            return error_response("Content-Type deve ser multipart/form-data")
        
        boundary = content_type.split('boundary=')[-1].strip('--')
        if not boundary:
            return error_response("Boundary não encontrado")
        
        parts = body.split(('--' + boundary).encode())
        job_id = str(uuid.uuid4())
        job_prefix = f"jobs/{job_id}/"
        uploaded_count = 0
        
        for part in parts:
            if b'filename="' not in part:
                continue
                
            header_end = part.find(b'\r\n\r\n') + 4
            if header_end < 4:
                continue
                
            content = part[header_end:].rstrip(b'\r\n--')
            
            header = part[:header_end].decode('utf-8', errors='ignore')
            filename_start = header.find('filename="') + 10
            if filename_start < 10:
                continue
            filename_end = header.find('"', filename_start)
            filename = header[filename_start:filename_end].strip()
            
            if filename and filename.lower().endswith(('.xlsx', '.xltm')):
                key = job_prefix + filename
                s3.put_object(
                    Bucket=BUCKET_NAME,
                    Key=key,
                    Body=content,
                    ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                uploaded_count += 1
        
        return success_response(job_id, uploaded_count)
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return error_response(str(e))


def success_response(job_id, count):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        },
        "body": json.dumps({
            "status": "success",
            "job_id": job_id,
            "files_uploaded": count
        })
    }


def error_response(message):
    return {
        "statusCode": 400,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"error": message})
    }
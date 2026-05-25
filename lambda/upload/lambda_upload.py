import json
import boto3
import uuid
import base64
from io import BytesIO

s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

def lambda_handler(event, context):
    try:
        # Handle base64 encoded body (API Gateway)
        body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body)
        
        headers = event.get('headers', {})
        
        # Simple multipart parsing (using built-in approach + fallback)
        # For production, you can add 'python-multipart' to the layer if needed
        boundary = None
        content_type = headers.get('content-type', headers.get('Content-Type', ''))
        if 'boundary=' in content_type:
            boundary = content_type.split('boundary=')[1].strip()
        
        if not boundary:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid multipart request"})
            }
        
        # Parse files (basic implementation)
        files = parse_multipart(body, boundary)
        
        if not files:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No files uploaded"})
            }
        
        job_id = str(uuid.uuid4())
        job_prefix = f"jobs/{job_id}/"
        
        uploaded_files = []
        
        for file_info in files:
            filename = file_info['filename']
            content = file_info['content']
            
            if not filename.lower().endswith(('.xlsx', '.xltm')):
                continue
                
            key = job_prefix + filename
            s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=content)
            uploaded_files.append(filename)
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "success",
                "job_id": job_id,
                "files_uploaded": len(uploaded_files),
                "message": f"{len(uploaded_files)} arquivos enviados com sucesso."
            })
        }
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


def parse_multipart(body, boundary):
    """Basic multipart parser for files"""
    files = []
    parts = body.split(b'--' + boundary.encode())
    
    for part in parts:
        if b'Content-Disposition' not in part:
            continue
        if b'filename="' not in part:
            continue
            
        header_end = part.find(b'\r\n\r\n') + 4
        content = part[header_end:].strip(b'\r\n--')
        
        # Extract filename
        header = part[:header_end].decode('utf-8', errors='ignore')
        filename_start = header.find('filename="') + 10
        filename_end = header.find('"', filename_start)
        filename = header[filename_start:filename_end]
        
        if filename:
            files.append({
                'filename': filename,
                'content': content
            })
    
    return files
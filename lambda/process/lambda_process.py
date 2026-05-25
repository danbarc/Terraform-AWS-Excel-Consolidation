import pandas as pd
import boto3
import os
import re
from datetime import datetime
import json

s3 = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

# ====================  ORIGINAL FUNCTIONS ====================

def is_date_format(value):
    if not isinstance(value, str):
        return None
    pattern = r'^\d{1,2}/\d{1,2}/\d{2,4}$'
    if re.match(pattern, value):
        try:
            parts = value.split('/')
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            if len(str(year)) == 2:
                year = 2000 + year
            date_obj = datetime(year, month, day)
            return date_obj.strftime('%d/%m/%Y')
        except ValueError:
            return None
    return None


def lambda_handler(event, context):
    try:
        bucket = event.get('bucket', BUCKET_NAME)
        job_id = event.get('job_id')
        
        if not job_id:
            return {"statusCode": 400, "body": json.dumps({"error": "job_id is required"})}
        
        job_prefix = f"jobs/{job_id}/"
        
        # List all files in the job
        response = s3.list_objects_v2(Bucket=bucket, Prefix=job_prefix)
        files = response.get('Contents', [])
        
        dados_combinados = []
        temp_dir = "/tmp"
        
        processed_count = 0
        
        for file_obj in files:
            key = file_obj['Key']
            if not key.lower().endswith(('.xlsx', '.xltm')):
                continue
                
            filename = os.path.basename(key)
            print(f"Processando arquivo: {filename}")
            
            # Download to /tmp
            local_path = os.path.join(temp_dir, filename)
            s3.download_file(bucket, key, local_path)
            
            try:
                excel_file = pd.ExcelFile(local_path, engine='openpyxl')
                
                for aba in excel_file.sheet_names:
                    print(f"Processando aba: {aba} no arquivo {filename}")
                    
                    df = excel_file.parse(aba, header=None)
                    
                    # === FIND OBRA (CLIENTE) ===
                    obra = "Desconhecido"
                    encontrou_cliente = False
                    for i in range(len(df)):
                        for j in range(len(df.columns)):
                            valor = str(df.iloc[i, j]).strip().upper()
                            if valor == "CLIENTE":
                                for k in range(j + 1, len(df.columns)):
                                    valor_direita = df.iloc[i, k]
                                    if not pd.isna(valor_direita):
                                        obra = valor_direita
                                        print(f"Obra encontrada: {obra}")
                                        break
                                encontrou_cliente = True
                                break
                        if encontrou_cliente:
                            break
                    
                    # === FIND DATE ===
                    data = None
                    for i in range(len(df)):
                        for j in range(len(df.columns)):
                            valor = df.iloc[i, j]
                            if isinstance(valor, str):
                                data_found = is_date_format(valor)
                                if data_found:
                                    data = data_found
                                    print(f"Data encontrada: {data}")
                                    break
                            elif isinstance(valor, (pd.Timestamp, datetime)):
                                data = valor.strftime('%d/%m/%Y')
                                print(f"Data encontrada (datetime): {data}")
                                break
                        if data is not None:
                            break
                    
                    # === FIND DATA SECTION (QTD. to VOLUME) ===
                    linha_inicio = None
                    linha_fim = None
                    for i in range(len(df)):
                        for j in range(len(df.columns)):
                            valor = str(df.iloc[i, j]).strip().upper()
                            if valor == "QTD.":
                                linha_inicio = i
                            if valor == "VOLUME":
                                linha_fim = i
                                break
                        if linha_inicio is not None and linha_fim is not None:
                            break
                    
                    if linha_inicio is None:
                        print(f"Linha 'QTD.' não encontrada em {filename} - {aba}")
                        continue
                        
                    if linha_fim is None:
                        linha_fim = len(df)
                    
                    # Read data section
                    num_linhas = linha_fim - (linha_inicio + 1)
                    if num_linhas <= 0:
                        continue
                        
                    df_dados = excel_file.parse(aba, skiprows=linha_inicio + 1, nrows=num_linhas)
                    
                    # Select columns C, D, E, F (0-based indices 2,3,4,5)
                    if len(df_dados.columns) > 5:
                        df_dados = df_dados.iloc[:, [2, 3, 4, 5]]
                        df_dados.columns = ["Código", "Item", "Qtd", "UN"]
                    
                    df_dados = df_dados.dropna(subset=["Código"], how="all")
                    
                    # Add metadata
                    df_dados["Obra"] = obra
                    df_dados["Arquivo"] = filename
                    df_dados["Data"] = data
                    
                    if not df_dados.empty:
                        dados_combinados.append(df_dados)
                        
            except Exception as e:
                print(f"Erro processando {filename}: {e}")
                continue
            
            processed_count += 1
        
        if not dados_combinados:
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "warning", "message": "Nenhum dado válido encontrado"})
            }
        
        # Final consolidation
        resultado = pd.concat(dados_combinados, ignore_index=True)
        resultado = resultado[["Código", "Item", "Qtd", "UN", "Obra", "Arquivo", "Data"]]
        
        # Save and upload result
        output_filename = "rastreamento_codigos.xlsx"
        output_key = f"outputs/{job_id}/{output_filename}"
        output_path = os.path.join(temp_dir, output_filename)
        
        resultado.to_excel(output_path, index=False)
        s3.upload_file(output_path, bucket, output_key)
        
        # Generate presigned URL
        download_url = s3.generate_presigned_url('get_object',
                                                 Params={'Bucket': bucket, 'Key': output_key},
                                                 ExpiresIn=3600)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "job_id": job_id,
                "download_url": download_url,
                "rows_processed": len(resultado),
                "files_processed": processed_count
            })
        }
        
    except Exception as e:
        print(f"Critical error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
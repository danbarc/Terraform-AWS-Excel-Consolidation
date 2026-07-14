resource "aws_lambda_function" "upload" {
  filename         = "${path.module}/lambda/upload.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda/upload.zip") # ← Adicione esta linha
  function_name    = "${var.project_name}-upload"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_upload.lambda_handler"
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 1024
  layers           = [local.pandas_layer_arn]

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.main.id
    }
  }
}

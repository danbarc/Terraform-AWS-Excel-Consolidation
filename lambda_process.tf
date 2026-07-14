resource "aws_lambda_function" "process" {
  filename         = "${path.module}/lambda/process.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda/process.zip")
  function_name    = "${var.project_name}-process"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_process.lambda_handler"
  runtime          = "python3.11"
  timeout          = var.lambda_timeout
  memory_size      = 3008 # ← Changed from 4096 to 3008 (maximum allowed)

  ephemeral_storage {
    size = var.ephemeral_storage
  }

  layers = [local.pandas_layer_arn]

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.main.id
    }
  }
}

output "api_endpoint" {
  value = aws_apigatewayv2_api.main.api_endpoint
}

output "s3_bucket_data" {
  value = aws_s3_bucket.main.id
}

output "frontend_url" {
  value = aws_s3_bucket_website_configuration.frontend.website_endpoint
}

output "frontend_bucket" {
  value = aws_s3_bucket.frontend.id
}

output "upload_lambda" {
  value = aws_lambda_function.upload.function_name
}

output "process_lambda" {
  value = aws_lambda_function.process.function_name
}

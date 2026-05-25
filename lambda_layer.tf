# ==================== AWS SDK FOR PANDAS LAYER (sa-east-1) ====================

locals {
  # Official AWS-managed Pandas layer for Python 3.11 in sa-east-1
  pandas_layer_arn = "arn:aws:lambda:sa-east-1:336392948345:layer:AWSSDKPandas-Python311:31"
}

output "pandas_layer_arn" {
  value = local.pandas_layer_arn
}

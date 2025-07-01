resource "aws_secretsmanager_secret" "scorpius_secrets" {
  name = "scorpius-enterprise-secrets"
  description = "Scorpius Enterprise Platform secrets"

  tags = {
    Environment = var.environment
    Project     = "scorpius-enterprise"
  }
}

resource "aws_secretsmanager_secret_version" "initial" {
  secret_id     = aws_secretsmanager_secret.scorpius_secrets.id
  secret_string = jsonencode(var.initial_secrets)
}

resource "aws_secretsmanager_secret_rotation" "scorpius" {
  secret_id          = aws_secretsmanager_secret.scorpius_secrets.id
  rotation_lambda_arn = aws_lambda_function.rotation_function.arn
  rotation_rules {
    automatically_after_days = 90
  }
}

resource "aws_lambda_function" "rotation_function" {
  filename         = "${path.module}/rotation_function.zip"
  function_name    = "scorpius-secrets-rotation"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "rotation_function.lambda_handler"
  runtime          = "python3.11"
  timeout          = 300

  environment {
    variables = {
      SECRET_ID = aws_secretsmanager_secret.scorpius_secrets.id
    }
  }
}

resource "aws_iam_role" "lambda_execution" {
  name = "scorpius-secrets-rotation-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_execution" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "secrets_manager_access" {
  name = "scorpius-secrets-rotation-policy"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecretVersionStage"
        ]
        Resource = aws_secretsmanager_secret.scorpius_secrets.arn
      }
    ]
  })
}

output "secret_arn" {
  value = aws_secretsmanager_secret.scorpius_secrets.arn
}

output "secret_id" {
  value = aws_secretsmanager_secret.scorpius_secrets.id
}

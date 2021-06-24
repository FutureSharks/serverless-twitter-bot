terraform {
  required_version = ">= 0.14.6"

  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = var.AWS_REGION
}

resource "aws_lambda_function" "main" {
  function_name    = var.bot_name
  filename         = "lambda.zip"
  source_code_hash = filebase64sha256("lambda.zip")
  role             = aws_iam_role.main.arn
  handler          = "main.handler"
  runtime          = "python3.8"
  timeout          = 900
  memory_size      = 256

  environment {
    variables = {
      TWITTER_CONSUMER_KEY        = var.TWITTER_CONSUMER_KEY
      TWITTER_CONSUMER_SECRET     = var.TWITTER_CONSUMER_SECRET
      TWITTER_ACCESS_TOKEN        = var.TWITTER_ACCESS_TOKEN
      TWITTER_ACCESS_TOKEN_SECRET = var.TWITTER_ACCESS_TOKEN_SECRET
      STATE_S3_BUCKET             = aws_s3_bucket.bot_state.id
      STATE_S3_KEY                = var.bot_name
      PYTHONPATH                  = "serverless_twitter_bot"
      TWITTER_TEST_MODE           = "0"
    }
  }
}

resource "random_id" "random_string" {
  byte_length = 4
}

resource "aws_s3_bucket" "tfstate_bucket" {
  bucket        = "tfstate-${var.bot_name}-${random_id.random_string.dec}"
  acl           = "private"
  force_destroy = true
}

resource "aws_s3_bucket" "bot_state" {
  bucket        = "${var.bot_name}-${random_id.random_string.dec}"
  acl           = "private"
  force_destroy = true
}

resource "aws_cloudwatch_log_group" "main" {
  name              = "/aws/lambda/${aws_lambda_function.main.function_name}"
  retention_in_days = 30
}

resource "aws_iam_role" "main" {
  name               = var.bot_name
  assume_role_policy = data.aws_iam_policy_document.main_assume_role_policy.json
}

data "aws_iam_policy_document" "main_assume_role_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "main" {
  statement {
    sid    = "${replace(var.bot_name, "-", "")}Logging"
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["${aws_cloudwatch_log_group.main.arn}:*"]
  }

  statement {
    sid    = "${replace(var.bot_name, "-", "")}S3Object"
    effect = "Allow"

    actions = [
      "s3:PutObject",
      "s3:PutObjectAcl",
      "s3:PutObjectTagging",
      "s3:PutObjectVersionAcl",
      "s3:GetObject",
      "s3:GetObjectAcl",
      "s3:GetObjectVersion",
      "s3:GetObjectTagging",
      "s3:DeleteObject",
      "s3:DeleteObjectVersion",
      "s3:DeleteObjectTagging",
    ]

    resources = ["${aws_s3_bucket.bot_state.arn}/*"]
  }

  statement {
    sid    = "${replace(var.bot_name, "-", "")}S3Bucket"
    effect = "Allow"

    actions = [
      "s3:ListBucket",
      "s3:GetBucketLocation",
    ]

    resources = [aws_s3_bucket.bot_state.arn]
  }
}

resource "aws_iam_policy" "main" {
  name        = var.bot_name
  description = "Basic execution policy for a ${aws_lambda_function.main.function_name} Lambda function"
  policy      = data.aws_iam_policy_document.main.json
}

resource "aws_iam_role_policy_attachment" "main" {
  role       = aws_iam_role.main.name
  policy_arn = aws_iam_policy.main.arn
}

# Scheduled execution

resource "aws_lambda_permission" "main" {
  count         = var.enable_schedule ? 1 : 0
  statement_id  = "AllowExecutionFromCloudWatch_${var.bot_name}"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.schedule[0].arn
}

resource "aws_cloudwatch_event_rule" "schedule" {
  count               = var.enable_schedule ? 1 : 0
  name                = "${var.bot_name}_schedule"
  description         = "schedule for ${var.bot_name}"
  schedule_expression = "cron(${var.schedule_mins} ${var.schedule_hours} * * ? *)"
}

resource "aws_cloudwatch_event_target" "schedule" {
  count     = var.enable_schedule ? 1 : 0
  target_id = "${var.bot_name}_schedule"
  rule      = aws_cloudwatch_event_rule.schedule[0].name
  arn       = aws_lambda_function.main.arn
}

# Function error notifications

resource "aws_sns_topic" "notifications" {
  count = var.notifications_email != "" ? 1 : 0
  name  = "${var.bot_name}_notifications"
  provisioner "local-exec" {
    command = "aws --region ${var.AWS_REGION} sns subscribe --topic-arn ${self.arn} --protocol email --notification-endpoint ${var.notifications_email}"
  }
}

resource "aws_cloudwatch_metric_alarm" "errors" {
  count               = var.notifications_email != "" ? 1 : 0
  alarm_name          = "${aws_lambda_function.main.id}_errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "60"
  statistic           = "Average"
  threshold           = "0"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.main.id
  }

  alarm_actions = [
    aws_sns_topic.notifications[0].arn,
  ]
}

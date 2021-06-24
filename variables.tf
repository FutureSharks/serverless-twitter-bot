variable "AWS_REGION" {}

variable "TWITTER_CONSUMER_KEY" {}

variable "TWITTER_CONSUMER_SECRET" {}

variable "TWITTER_ACCESS_TOKEN" {}

variable "TWITTER_ACCESS_TOKEN_SECRET" {}

variable "resource_name" {
  default = "serverless-twitter-bot"
}

variable "schedule_hours" {
  default = "14,16,17,19,20,21,22,23"
}

variable "schedule_mins" {
  default = "07,13,21,31,37,41,49,55"
}

variable "notifications_email" {
  default = ""
}

variable "enable_schedule" {
  default = false
}

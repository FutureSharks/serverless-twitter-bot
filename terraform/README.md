# serverless-twitter-bot Terraform setup

Here you will find example [Terraform](https://www.terraform.io/) code to setup the twitter bot.

You will need to:

- Install Terraform version `0.14.6` or higher
- Update [terraform.tfvars](terraform.tfvars) with your Twitter application auth details
- Authenticate to AWS [somehow](https://registry.terraform.io/providers/hashicorp/aws/latest/docs#authentication)

First create the zip file containing the code for the Lambda function:

```
./create-aws-lambda-zip.sh
```

Edit [terraform.tfvars](terraform.tfvars) to add your values.

Then you can apply the Terraform configuration:

```
terraform init
terraform apply
```

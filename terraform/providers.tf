terraform {
  required_version = "~> 1.5.4"
  backend "s3" {
    bucket         = "terraform-state-080723"
    key            = "ansible/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.20.0"
    }
  }
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.92"
      region= "aws-west-1"
    }
  }

  required_version = ">= 1.2"
}

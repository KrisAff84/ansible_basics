#####################################
# Provider
#####################################

provider "aws" {
  region = var.region
}

#####################################
# Data Sources
#####################################

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

#####################################
# Resources
#####################################

resource "aws_instance" "ansible" {
  count           = var.num_of_instances
  ami             = var.ami
  key_name        = var.key_pair
  instance_type   = "t2.micro"
  subnet_id       = data.aws_subnets.default.ids[count.index]
  security_groups = ["Ansible Security Group"]
  tags = {
    Name = "ansible_server_${count.index + 1}"
  }
}

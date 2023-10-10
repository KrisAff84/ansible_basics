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
  security_groups = [resource.aws_security_group.ansible.id]
  tags = {
    Name = "ansible_server_${count.index + 1}"
    Type = "ansible"
  }
}

resource "aws_security_group" "ansible" {
  name        = "Ansible_SG"
  description = "Allow SSH, HTTP inbound traffic, and in network communication"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
  }

  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "In network communication"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [data.aws_vpc.default.cidr_block]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

#####################################
# outputs
#####################################

output "ansible_server_instance_ids" {
  value = aws_instance.ansible.*.id
}
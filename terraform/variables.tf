variable "region" {
  type    = string
  default = "us-west-2"
}

variable "num_of_instances" {
  description = "Number of instances to create"
  type        = number
  default     = 3
}

variable "ami" {
  description = "AMI to use for instances"
  type        = string
  default     = "ami-00aa0673b34e3c150"
}

variable "key_pair" {
  description = "SSH key pair to use for instances"
  type        = string
  default     = "ansible_key"
}
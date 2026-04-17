# ------------------------------------------------------------------
# General
# ------------------------------------------------------------------
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "project_name" {
  description = "Project name used as a naming prefix for all resources"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev, qa, prod)"
  type        = string
}

# ------------------------------------------------------------------
# EC2
# ------------------------------------------------------------------
variable "ami_id" {
  description = "AMI ID for EC2 instances"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "key_pair_name" {
  description = "Name of an existing EC2 key pair (leave empty to omit)"
  type        = string
  default     = ""
}

variable "ebs_volume_size" {
  description = "Root EBS volume size in GiB"
  type        = number
  default     = 20
}

variable "app_port" {
  description = "Port the application listens on"
  type        = number
}

# ------------------------------------------------------------------
# Existing infrastructure (supply after deploying the base stack)
# ------------------------------------------------------------------
variable "vpc_id" {
  description = "ID of the existing VPC"
  type        = string
}

variable "ec2_sg_id" {
  description = "ID of the existing EC2 security group (e.g. loginapp-prod-sg-ec2)"
  type        = string
}

variable "subnet_id" {
  description = "ID of the subnet to launch the EC2 instance into"
  type        = string
}

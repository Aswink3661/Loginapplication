variable "project_name" {
  description = "Project name used as a naming prefix"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev, qa, prod)"
  type        = string
}

variable "ami_id" {
  description = "AMI ID for EC2 instances"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "key_pair_name" {
  description = "Name of an existing EC2 key pair for SSH access (leave empty to omit)"
  type        = string
  default     = ""
}

variable "ec2_sg_id" {
  description = "ID of the EC2 security group to attach to instances"
  type        = string
}

variable "app_port" {
  description = "Port the application listens on (used in health checks)"
  type        = number
}

variable "ebs_volume_size" {
  description = "Root EBS volume size in GiB"
  type        = number
  default     = 20
}

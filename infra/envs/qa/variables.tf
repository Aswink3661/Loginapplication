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
# VPC
# ------------------------------------------------------------------
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets"
  type        = list(string)
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
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
}

# ------------------------------------------------------------------
# ALB
# ------------------------------------------------------------------
variable "app_port" {
  description = "Port the application listens on"
  type        = number
}

variable "health_check_path" {
  description = "HTTP path used by the ALB health check"
  type        = string
}

variable "enable_deletion_protection" {
  description = "Enable ALB deletion protection"
  type        = bool
}

# ------------------------------------------------------------------
# Auto Scaling Group
# ------------------------------------------------------------------
variable "asg_min_size" {
  description = "Minimum number of instances in the ASG"
  type        = number
}

variable "asg_max_size" {
  description = "Maximum number of instances in the ASG"
  type        = number
}

variable "asg_desired_capacity" {
  description = "Desired number of instances in the ASG"
  type        = number
}

variable "scale_out_cpu_threshold" {
  description = "CPU % threshold to trigger scale-out"
  type        = number
}

variable "scale_in_cpu_threshold" {
  description = "CPU % threshold to trigger scale-in"
  type        = number
}

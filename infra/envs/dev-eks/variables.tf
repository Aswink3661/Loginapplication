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
# EKS
# ------------------------------------------------------------------
variable "kubernetes_version" {
  description = "Kubernetes version for the EKS cluster"
  type        = string
}

variable "node_instance_type" {
  description = "EC2 instance type for worker nodes"
  type        = string
}

variable "node_min_size" {
  description = "Minimum number of worker nodes"
  type        = number
}

variable "node_max_size" {
  description = "Maximum number of worker nodes"
  type        = number
}

variable "node_desired_size" {
  description = "Desired number of worker nodes"
  type        = number
}

variable "node_disk_size" {
  description = "Root EBS disk size in GiB for each worker node"
  type        = number
}

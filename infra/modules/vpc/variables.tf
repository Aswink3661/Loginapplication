variable "project_name" {
  description = "Project name used as a naming prefix"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev, qa, prod)"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets (one per AZ)"
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets (one per AZ)"
  type        = list(string)
}

variable "availability_zones" {
  description = "List of availability zones to deploy subnets into"
  type        = list(string)
}

variable "eks_cluster_name" {
  description = "EKS cluster name used to add required Kubernetes subnet discovery tags. Leave empty for non-EKS VPCs."
  type        = string
  default     = ""
}

variable "project_name" {
  description = "Project name used as a naming prefix"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev, qa, prod)"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC to create security groups in"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC (used to restrict SSH access)"
  type        = string
}

variable "app_port" {
  description = "Port the application listens on"
  type        = number
}

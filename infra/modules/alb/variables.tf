variable "project_name" {
  description = "Project name used as a naming prefix"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev, qa, prod)"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for the ALB"
  type        = list(string)
}

variable "alb_sg_id" {
  description = "ID of the ALB security group"
  type        = string
}

variable "app_port" {
  description = "Port the application listens on"
  type        = number
}

variable "health_check_path" {
  description = "HTTP path for target group health checks"
  type        = string
  default     = "/"
}

variable "enable_deletion_protection" {
  description = "Whether to enable ALB deletion protection"
  type        = bool
  default     = false
}

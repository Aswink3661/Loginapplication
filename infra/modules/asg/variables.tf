variable "project_name" {
  description = "Project name used as a naming prefix"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev, qa, prod)"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for EC2 instances"
  type        = list(string)
}

variable "target_group_arn" {
  description = "ARN of the ALB target group to attach instances to"
  type        = string
}

variable "launch_template_id" {
  description = "ID of the Launch Template"
  type        = string
}

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
  description = "CPU % above which a scale-out alarm is triggered"
  type        = number
  default     = 70
}

variable "scale_in_cpu_threshold" {
  description = "CPU % below which a scale-in alarm is triggered"
  type        = number
  default     = 30
}

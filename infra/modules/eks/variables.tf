variable "project_name" {
  description = "Project name used as a naming prefix for all resources"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev, qa, prod)"
  type        = string
}

variable "private_subnet_ids" {
  description = "IDs of private subnets where worker nodes are placed"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "IDs of public subnets included in the cluster VPC config for load balancers"
  type        = list(string)
}

variable "kubernetes_version" {
  description = "Kubernetes version for the EKS cluster"
  type        = string
  default     = "1.33"
}

# ------------------------------------------------------------------
# Node Group
# ------------------------------------------------------------------
variable "node_instance_type" {
  description = "EC2 instance type for worker nodes (t3.medium is the minimum recommended for EKS)"
  type        = string
  default     = "t3.medium"
}

variable "node_min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 2
}

variable "node_desired_size" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 1
}

variable "node_disk_size" {
  description = "Root EBS disk size in GiB for each worker node"
  type        = number
  default     = 20
}

# ---------------------------------------------------------------
# DEV-EKS environment – variable values
# ---------------------------------------------------------------

aws_region   = "ap-south-1"
project_name = "loginapp"
environment  = "dev"

# VPC – separate CIDR space from the dev EC2 environment (10.0.0.0/16)
vpc_cidr             = "10.1.0.0/16"
public_subnet_cidrs  = ["10.1.1.0/24", "10.1.2.0/24"]
private_subnet_cidrs = ["10.1.11.0/24", "10.1.12.0/24"]
availability_zones   = ["ap-south-1a", "ap-south-1b"]

# EKS
kubernetes_version = "1.33"

# Node group – minimum viable configuration for dev
# t3.micro is insufficient for EKS system pods; t3.medium is the minimum
node_instance_type = "t3.medium"
node_min_size      = 1
node_max_size      = 2
node_desired_size  = 1
node_disk_size     = 20

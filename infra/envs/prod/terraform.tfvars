# ---------------------------------------------------------------
# PROD environment – variable values
# ---------------------------------------------------------------

aws_region   = "us-east-1"
project_name = "loginapp"
environment  = "prod"

# VPC
vpc_cidr             = "10.2.0.0/16"
public_subnet_cidrs  = ["10.2.1.0/24", "10.2.2.0/24"]
private_subnet_cidrs = ["10.2.11.0/24", "10.2.12.0/24"]
availability_zones   = ["us-east-1a", "us-east-1b"]

# EC2
ami_id          = "ami-0c02fb55956c7d316" # Amazon Linux 2023 – us-east-1
instance_type   = "t3.medium"
key_pair_name   = ""
ebs_volume_size = 30

# ALB
app_port                   = 80
health_check_path          = "/"
enable_deletion_protection = true

# ASG
asg_min_size             = 2
asg_max_size             = 10
asg_desired_capacity     = 3
scale_out_cpu_threshold  = 65
scale_in_cpu_threshold   = 25

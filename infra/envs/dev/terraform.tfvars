# ---------------------------------------------------------------
# DEV environment – variable values
# ---------------------------------------------------------------

aws_region   = "us-east-1"
project_name = "loginapp"
environment  = "dev"

# VPC
vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24"]
availability_zones   = ["us-east-1a", "us-east-1b"]

# EC2
ami_id          = "ami-0c02fb55956c7d316" # Amazon Linux 2023 – us-east-1
instance_type   = "t3.micro"
key_pair_name   = ""
ebs_volume_size = 20

# ALB
app_port                   = 80
health_check_path          = "/"
enable_deletion_protection = false

# ASG
asg_min_size             = 1
asg_max_size             = 2
asg_desired_capacity     = 1
scale_out_cpu_threshold  = 70
scale_in_cpu_threshold   = 30

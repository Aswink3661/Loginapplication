# ---------------------------------------------------------------
# DEV-EC2 environment – variable values
# ---------------------------------------------------------------

aws_region   = "ap-south-1"
project_name = "loginapp"
environment  = "dev"

# EC2
ami_id          = "ami-0e12ffc2dd465f6e4" # Amazon Linux 2023 – ap-south-1
instance_type   = "t3.micro"
key_pair_name   = "Pem_key"
ebs_volume_size = 20
app_port        = 80

# Existing infrastructure – resolved via AWS CLI
vpc_id     = "vpc-092b0d10291014ae3"
ec2_sg_id  = "sg-07ef0129690a48376"
subnet_id  = "subnet-0069d8637a5a7e78e"

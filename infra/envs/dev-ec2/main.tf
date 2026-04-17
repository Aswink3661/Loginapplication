# ------------------------------------------------------------------
# EC2 – launch template + IAM role only
# Provide the IDs of the pre-existing VPC and EC2 security group
# via terraform.tfvars (vpc_id, ec2_sg_id).
# ------------------------------------------------------------------
module "ec2" {
  source = "../../modules/ec2"

  project_name    = var.project_name
  environment     = var.environment
  ami_id          = var.ami_id
  instance_type   = var.instance_type
  key_pair_name   = var.key_pair_name
  ec2_sg_id       = var.ec2_sg_id
  app_port        = var.app_port
  ebs_volume_size = var.ebs_volume_size
}

# ------------------------------------------------------------------
# EC2 Instance – launched from the launch template above
# ------------------------------------------------------------------
resource "aws_instance" "this" {
  subnet_id = var.subnet_id

  launch_template {
    id      = module.ec2.launch_template_id
    version = "$Latest"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-instance"
    Environment = var.environment
  }
}

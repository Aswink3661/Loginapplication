module "vpc" {
  source = "../../modules/vpc"

  project_name         = var.project_name
  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
}

module "security_groups" {
  source = "../../modules/security_groups"

  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  vpc_cidr     = module.vpc.vpc_cidr
  app_port     = var.app_port
}

module "ec2" {
  source = "../../modules/ec2"

  project_name    = var.project_name
  environment     = var.environment
  ami_id          = var.ami_id
  instance_type   = var.instance_type
  key_pair_name   = var.key_pair_name
  ec2_sg_id       = module.security_groups.ec2_sg_id
  app_port        = var.app_port
  ebs_volume_size = var.ebs_volume_size
}

module "alb" {
  source = "../../modules/alb"

  project_name               = var.project_name
  environment                = var.environment
  vpc_id                     = module.vpc.vpc_id
  public_subnet_ids          = module.vpc.public_subnet_ids
  alb_sg_id                  = module.security_groups.alb_sg_id
  app_port                   = var.app_port
  health_check_path          = var.health_check_path
  enable_deletion_protection = var.enable_deletion_protection
}

module "asg" {
  source = "../../modules/asg"

  project_name            = var.project_name
  environment             = var.environment
  private_subnet_ids      = module.vpc.private_subnet_ids
  target_group_arn        = module.alb.target_group_arn
  launch_template_id      = module.ec2.launch_template_id
  asg_min_size            = var.asg_min_size
  asg_max_size            = var.asg_max_size
  asg_desired_capacity    = var.asg_desired_capacity
  scale_out_cpu_threshold = var.scale_out_cpu_threshold
  scale_in_cpu_threshold  = var.scale_in_cpu_threshold
}

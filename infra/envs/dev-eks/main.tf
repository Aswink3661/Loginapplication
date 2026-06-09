locals {
  cluster_name = "${var.project_name}-${var.environment}-eks"
}

module "vpc" {
  source = "../../modules/vpc"

  project_name         = var.project_name
  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
  eks_cluster_name     = local.cluster_name
}

module "eks" {
  source = "../../modules/eks"

  project_name       = var.project_name
  environment        = var.environment
  public_subnet_ids  = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids
  node_subnet_ids    = module.vpc.public_subnet_ids # public subnets → nodes get public IPs
  node_ssh_key_name  = var.node_ssh_key_name
  kubernetes_version = var.kubernetes_version
  node_instance_type = var.node_instance_type
  node_min_size      = var.node_min_size
  node_max_size      = var.node_max_size
  node_desired_size  = var.node_desired_size
  node_disk_size     = var.node_disk_size
  cluster_admin_arns = var.cluster_admin_arns
}

# ------------------------------------------------------------------
# EFS – shared documents volume mounted into the backend at /opt/docs
# ------------------------------------------------------------------
resource "aws_security_group" "efs_docs" {
  name        = "${local.cluster_name}-docs-efs-sg"
  description = "Allow EKS worker nodes to mount the docs EFS file system"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "NFS from the EKS VPC"
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.cluster_name}-docs-efs-sg"
  }
}

resource "aws_efs_file_system" "docs" {
  creation_token   = "${local.cluster_name}-docs"
  encrypted        = true
  performance_mode = "generalPurpose"
  throughput_mode  = "elastic"

  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }

  tags = {
    Name = "${local.cluster_name}-docs-efs"
  }
}

resource "aws_efs_backup_policy" "docs" {
  file_system_id = aws_efs_file_system.docs.id

  backup_policy {
    status = "ENABLED"
  }
}

resource "aws_efs_mount_target" "docs" {
  for_each = zipmap(var.private_subnet_cidrs, module.vpc.private_subnet_ids)

  file_system_id  = aws_efs_file_system.docs.id
  subnet_id       = each.value
  security_groups = [aws_security_group.efs_docs.id]
}

resource "aws_efs_access_point" "docs" {
  file_system_id = aws_efs_file_system.docs.id

  posix_user {
    gid = 10001
    uid = 10001
  }

  root_directory {
    path = "/opt/docs"

    creation_info {
      owner_gid   = 10001
      owner_uid   = 10001
      permissions = "0770"
    }
  }

  tags = {
    Name = "${local.cluster_name}-docs-ap"
  }

  depends_on = [aws_efs_mount_target.docs]
}

output "cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "API server endpoint of the EKS cluster"
  value       = module.eks.cluster_endpoint
}

output "cluster_ca_certificate" {
  description = "Base64-encoded certificate authority data"
  value       = module.eks.cluster_ca_certificate
  sensitive   = true
}

output "cluster_oidc_issuer" {
  description = "OIDC issuer URL (used for IRSA)"
  value       = module.eks.cluster_oidc_issuer
}

output "node_role_arn" {
  description = "ARN of the IAM role assigned to worker nodes"
  value       = module.eks.node_role_arn
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "efs_file_system_id" {
  description = "ID of the EFS file system used for backend /opt/docs storage"
  value       = aws_efs_file_system.docs.id
}

output "efs_access_point_id" {
  description = "ID of the EFS access point rooted at /opt/docs"
  value       = aws_efs_access_point.docs.id
}

output "efs_csi_driver_role_arn" {
  description = "ARN of the IAM role used by the EFS CSI driver"
  value       = module.eks.efs_csi_driver_role_arn
}

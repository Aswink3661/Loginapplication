output "launch_template_id" {
  description = "ID of the EC2 Launch Template"
  value       = module.ec2.launch_template_id
}

output "launch_template_latest_version" {
  description = "Latest version of the EC2 Launch Template"
  value       = module.ec2.launch_template_latest_version
}

output "instance_profile_name" {
  description = "Name of the EC2 IAM instance profile"
  value       = module.ec2.instance_profile_name
}

output "iam_role_arn" {
  description = "ARN of the EC2 IAM role"
  value       = module.ec2.iam_role_arn
}

output "vpc_id" {
  description = "ID of the existing VPC used by this environment"
  value       = var.vpc_id
}

output "ec2_sg_id" {
  description = "ID of the existing EC2 security group used by this environment"
  value       = var.ec2_sg_id
}

output "instance_id" {
  description = "ID of the running EC2 instance"
  value       = aws_instance.this.id
}

output "instance_public_ip" {
  description = "Public IP of the running EC2 instance"
  value       = aws_instance.this.public_ip
}

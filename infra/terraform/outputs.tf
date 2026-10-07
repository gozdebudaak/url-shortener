output "ecr_repository_urls" {
  description = "ECR repository URLs by service"
  value       = { for k, r in aws_ecr_repository.this : k => r.repository_url }
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.this.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = [for s in aws_subnet.public : s.id]
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.this.name
}

output "kubeconfig_command" {
  description = "Command to configure kubectl for the EKS cluster"
  value       = "aws eks update-kubeconfig --name ${aws_eks_cluster.this.name} --region ${var.region} --alias url-shortener-eks"
}
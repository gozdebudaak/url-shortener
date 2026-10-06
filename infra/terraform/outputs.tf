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
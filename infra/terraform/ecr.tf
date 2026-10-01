resource "aws_ecr_repository" "this" {
  for_each = toset(["backend", "frontend"])

  name                 = "url-shortener-${each.key}"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  force_delete = true # Should be false in production
}
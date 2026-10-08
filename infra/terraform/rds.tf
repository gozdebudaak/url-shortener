resource "random_password" "db" {
  length  = 32
  special = false
}

resource "aws_db_subnet_group" "this" {
  name       = "url-shortener"
  subnet_ids = [for s in aws_subnet.public : s.id]

  tags = {
    Name = "url-shortener"
  }
}

resource "aws_security_group" "db" {
  name        = "url-shortener-db"
  description = "PostgreSQL access from EKS"
  vpc_id      = aws_vpc.this.id

  tags = {
    Name = "url-shortener-db"
  }
}

resource "aws_vpc_security_group_ingress_rule" "db_from_eks" {
  security_group_id            = aws_security_group.db.id
  referenced_security_group_id = aws_eks_cluster.this.vpc_config[0].cluster_security_group_id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
  description                  = "PostgreSQL from EKS nodes and pods"
}

resource "aws_db_instance" "this" {
  identifier     = "url-shortener"
  engine         = "postgres"
  engine_version = "17"

  instance_class    = "db.t4g.micro"
  allocated_storage = 20
  storage_type      = "gp3"

  db_name  = "urlshortener"
  username = "app"
  password = random_password.db.result

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.db.id]
  publicly_accessible    = false

  skip_final_snapshot     = true  # Production value should be false and a final snapshot should be taken
  deletion_protection     = false # Production value should be true to prevent accidental deletion
  backup_retention_period = 0     # Production value should be greater than 0 to enable backups
  multi_az                = false # Production value should be true for high availability
  apply_immediately       = true  # Production value should be false to avoid downtime during maintenance
}
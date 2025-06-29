# ===================================================================
# 🏗️ AI Teddy Bear - Regional Infrastructure Module
# Enterprise-Grade Regional Services for Multi-Region Deployment
# Infrastructure Team Lead: Senior Infrastructure Engineer
# Date: January 2025
# ===================================================================

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.30"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.24"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
  }
}

# ===================================================================
# 🌐 VPC AND NETWORKING
# ===================================================================

# VPC for the region
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_config.cidr_block
  enable_dns_hostnames = var.vpc_config.enable_dns_hostnames
  enable_dns_support   = var.vpc_config.enable_dns_support
  
  tags = merge(var.global_tags, {
    Name                                               = "${var.project_name}-${var.region_name}-vpc"
    Type                                               = "vpc"
    "kubernetes.io/cluster/${var.eks_config.cluster_name}" = "shared"
  })
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-igw"
    Type = "internet-gateway"
  })
}

# Public Subnets
resource "aws_subnet" "public" {
  count = length(var.region_config.availability_zones)
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_config.cidr_block, 8, count.index)
  availability_zone       = var.region_config.availability_zones[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(var.global_tags, {
    Name                                               = "${var.project_name}-${var.region_name}-public-${count.index + 1}"
    Type                                               = "public-subnet"
    "kubernetes.io/cluster/${var.eks_config.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                           = "1"
  })
}

# Private Subnets
resource "aws_subnet" "private" {
  count = length(var.region_config.availability_zones)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_config.cidr_block, 8, count.index + 10)
  availability_zone = var.region_config.availability_zones[count.index]
  
  tags = merge(var.global_tags, {
    Name                                               = "${var.project_name}-${var.region_name}-private-${count.index + 1}"
    Type                                               = "private-subnet"
    "kubernetes.io/cluster/${var.eks_config.cluster_name}" = "owned"
    "kubernetes.io/role/internal-elb"                  = "1"
  })
}

# Database Subnets
resource "aws_subnet" "database" {
  count = length(var.region_config.availability_zones)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_config.cidr_block, 8, count.index + 20)
  availability_zone = var.region_config.availability_zones[count.index]
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-database-${count.index + 1}"
    Type = "database-subnet"
  })
}

# Elastic IPs for NAT Gateways
resource "aws_eip" "nat" {
  count = var.vpc_config.single_nat_gateway ? 1 : length(aws_subnet.public)
  
  domain = "vpc"
  
  depends_on = [aws_internet_gateway.main]
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-nat-eip-${count.index + 1}"
    Type = "elastic-ip"
  })
}

# NAT Gateways
resource "aws_nat_gateway" "main" {
  count = var.vpc_config.enable_nat_gateway ? (var.vpc_config.single_nat_gateway ? 1 : length(aws_subnet.public)) : 0
  
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  depends_on = [aws_internet_gateway.main]
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-nat-${count.index + 1}"
    Type = "nat-gateway"
  })
}

# Route Table for Public Subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-public-rt"
    Type = "route-table"
  })
}

# Route Tables for Private Subnets
resource "aws_route_table" "private" {
  count = length(aws_subnet.private)
  
  vpc_id = aws_vpc.main.id
  
  dynamic "route" {
    for_each = var.vpc_config.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = aws_nat_gateway.main[var.vpc_config.single_nat_gateway ? 0 : count.index].id
    }
  }
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-private-rt-${count.index + 1}"
    Type = "route-table"
  })
}

# Route Table for Database Subnets
resource "aws_route_table" "database" {
  vpc_id = aws_vpc.main.id
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-database-rt"
    Type = "route-table"
  })
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)
  
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count = length(aws_subnet.private)
  
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

resource "aws_route_table_association" "database" {
  count = length(aws_subnet.database)
  
  subnet_id      = aws_subnet.database[count.index].id
  route_table_id = aws_route_table.database.id
}

# ===================================================================
# 🔐 SECURITY GROUPS
# ===================================================================

# Security Group for EKS Cluster
resource "aws_security_group" "eks_cluster" {
  name_prefix = "${var.project_name}-${var.region_name}-eks-cluster-"
  vpc_id      = aws_vpc.main.id
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-eks-cluster-sg"
    Type = "security-group"
  })
}

# Security Group for EKS Nodes
resource "aws_security_group" "eks_nodes" {
  name_prefix = "${var.project_name}-${var.region_name}-eks-nodes-"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port = 0
    to_port   = 65535
    protocol  = "tcp"
    self      = true
  }
  
  ingress {
    from_port       = 1025
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-eks-nodes-sg"
    Type = "security-group"
  })
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  count = var.enable_rds ? 1 : 0
  
  name_prefix = "${var.project_name}-${var.region_name}-rds-"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_nodes.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-rds-sg"
    Type = "security-group"
  })
}

# Security Group for ElastiCache
resource "aws_security_group" "elasticache" {
  count = var.enable_elasticache ? 1 : 0
  
  name_prefix = "${var.project_name}-${var.region_name}-elasticache-"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_nodes.id]
  }
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-elasticache-sg"
    Type = "security-group"
  })
}

# Security Group for ALB
resource "aws_security_group" "alb" {
  count = var.enable_alb ? 1 : 0
  
  name_prefix = "${var.project_name}-${var.region_name}-alb-"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-alb-sg"
    Type = "security-group"
  })
}

# ===================================================================
# 🔐 KMS ENCRYPTION KEYS
# ===================================================================

# KMS Key for EKS encryption
resource "aws_kms_key" "eks" {
  description             = "KMS key for EKS cluster encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  
  tags = merge(var.global_tags, {
    Name    = "${var.project_name}-${var.region_name}-eks-key"
    Type    = "kms-key"
    Purpose = "eks-encryption"
  })
}

resource "aws_kms_alias" "eks" {
  name          = "alias/${var.project_name}-${var.region_name}-eks"
  target_key_id = aws_kms_key.eks.key_id
}

# KMS Key for S3 encryption
resource "aws_kms_key" "s3" {
  description             = "KMS key for S3 bucket encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  
  tags = merge(var.global_tags, {
    Name    = "${var.project_name}-${var.region_name}-s3-key"
    Type    = "kms-key"
    Purpose = "s3-encryption"
  })
}

resource "aws_kms_alias" "s3" {
  name          = "alias/${var.project_name}-${var.region_name}-s3"
  target_key_id = aws_kms_key.s3.key_id
}

# ===================================================================
# 🏗️ EKS CLUSTER
# ===================================================================

# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = var.eks_config.cluster_name
  version  = var.eks_config.cluster_version
  role_arn = aws_iam_role.eks_cluster.arn
  
  vpc_config {
    subnet_ids              = concat(aws_subnet.private[*].id, aws_subnet.public[*].id)
    endpoint_private_access = var.eks_config.cluster_endpoint_private_access
    endpoint_public_access  = var.eks_config.cluster_endpoint_public_access
    public_access_cidrs     = var.eks_config.cluster_endpoint_public_access_cidrs
    security_group_ids      = [aws_security_group.eks_cluster.id]
  }
  
  # Encryption configuration
  encryption_config {
    provider {
      key_arn = aws_kms_key.eks.arn
    }
    resources = ["secrets"]
  }
  
  # Logging configuration
  enabled_cluster_log_types = var.eks_config.cluster_enabled_log_types
  
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_vpc_resource_controller,
    aws_cloudwatch_log_group.eks_cluster
  ]
  
  tags = merge(var.global_tags, {
    Name = var.eks_config.cluster_name
    Type = "eks-cluster"
  })
}

# CloudWatch Log Group for EKS
resource "aws_cloudwatch_log_group" "eks_cluster" {
  name              = "/aws/eks/${var.eks_config.cluster_name}/cluster"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.eks.arn
  
  tags = merge(var.global_tags, {
    Name = "${var.eks_config.cluster_name}-logs"
    Type = "cloudwatch-log-group"
  })
}

# EKS Node Groups
resource "aws_eks_node_group" "main" {
  for_each = var.node_groups
  
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = each.value.name
  node_role_arn   = aws_iam_role.eks_node_group.arn
  subnet_ids      = aws_subnet.private[*].id
  
  capacity_type  = each.value.capacity_type
  instance_types = each.value.instance_types
  ami_type       = lookup(each.value, "ami_type", "AL2_x86_64")
  disk_size      = each.value.disk_size
  
  scaling_config {
    desired_size = each.value.desired_size
    max_size     = each.value.max_size
    min_size     = each.value.min_size
  }
  
  update_config {
    max_unavailable_percentage = each.value.max_unavailable_percentage
  }
  
  # Remote access configuration
  dynamic "remote_access" {
    for_each = lookup(each.value, "remote_access", null) != null ? [each.value.remote_access] : []
    content {
      ec2_ssh_key               = remote_access.value.ec2_ssh_key
      source_security_group_ids = remote_access.value.source_security_group_ids
    }
  }
  
  # Labels
  labels = merge(
    lookup(each.value, "k8s_labels", {}),
    {
      "role" = each.key
    }
  )
  
  # Taints
  dynamic "taint" {
    for_each = lookup(each.value, "taints", {})
    content {
      key    = taint.value.key
      value  = taint.value.value
      effect = taint.value.effect
    }
  }
  
  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy,
  ]
  
  tags = merge(var.global_tags, each.value.tags)
}

# ===================================================================
# 🗄️ RDS POSTGRESQL
# ===================================================================

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  count = var.enable_rds ? 1 : 0
  
  name       = "${var.project_name}-${var.region_name}-db-subnet-group"
  subnet_ids = aws_subnet.database[*].id
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-db-subnet-group"
    Type = "db-subnet-group"
  })
}

# RDS Instance
resource "aws_db_instance" "main" {
  count = var.enable_rds ? 1 : 0
  
  identifier = var.rds_config.identifier
  
  # Database configuration
  engine              = var.rds_config.engine
  engine_version      = var.rds_config.engine_version
  instance_class      = var.rds_config.instance_class
  allocated_storage   = var.rds_config.allocated_storage
  max_allocated_storage = var.rds_config.max_allocated_storage
  storage_type        = var.rds_config.storage_type
  storage_encrypted   = var.rds_config.storage_encrypted
  kms_key_id          = aws_kms_key.s3.arn
  
  # Database details
  db_name  = var.rds_config.db_name
  username = var.rds_config.username
  password = random_password.rds_password[0].result
  
  # Networking
  vpc_security_group_ids = [aws_security_group.rds[0].id]
  db_subnet_group_name   = aws_db_subnet_group.main[0].name
  multi_az               = var.rds_config.multi_az
  
  # Backup configuration
  backup_retention_period = var.rds_config.backup_retention_period
  backup_window          = var.rds_config.backup_window
  maintenance_window     = var.rds_config.maintenance_window
  delete_automated_backups = var.rds_config.delete_automated_backups
  
  # Security
  deletion_protection    = var.rds_config.deletion_protection
  skip_final_snapshot   = var.rds_config.skip_final_snapshot
  copy_tags_to_snapshot = var.rds_config.copy_tags_to_snapshot
  
  # Performance insights
  performance_insights_enabled    = var.rds_config.performance_insights_enabled
  performance_insights_retention_period = var.rds_config.performance_insights_retention_period
  
  # Monitoring
  monitoring_interval = var.rds_config.monitoring_interval
  monitoring_role_arn = aws_iam_role.rds_enhanced_monitoring[0].arn
  enabled_cloudwatch_logs_exports = var.rds_config.enabled_cloudwatch_logs_exports
  
  tags = merge(var.global_tags, {
    Name = var.rds_config.identifier
    Type = "rds-instance"
  })
}

# Random password for RDS
resource "random_password" "rds_password" {
  count = var.enable_rds ? 1 : 0
  
  length  = 32
  special = true
}

# Store RDS password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "rds_password" {
  count = var.enable_rds ? 1 : 0
  
  name = "${var.project_name}-${var.region_name}-rds-password"
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-rds-password"
    Type = "secret"
  })
}

resource "aws_secretsmanager_secret_version" "rds_password" {
  count = var.enable_rds ? 1 : 0
  
  secret_id     = aws_secretsmanager_secret.rds_password[0].id
  secret_string = random_password.rds_password[0].result
}

# ===================================================================
# 📊 ELASTICACHE REDIS
# ===================================================================

# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  count = var.enable_elasticache ? 1 : 0
  
  name       = "${var.project_name}-${var.region_name}-cache-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  
  tags = merge(var.global_tags, {
    Name = "${var.project_name}-${var.region_name}-cache-subnet-group"
    Type = "elasticache-subnet-group"
  })
}

# ElastiCache Replication Group
resource "aws_elasticache_replication_group" "main" {
  count = var.enable_elasticache ? 1 : 0
  
  replication_group_id         = var.elasticache_config.cluster_id
  description                  = "Redis cluster for AI Teddy Bear ${var.region_name}"
  
  # Configuration
  engine               = var.elasticache_config.engine
  engine_version       = var.elasticache_config.engine_version
  node_type           = var.elasticache_config.node_type
  port                = var.elasticache_config.port
  parameter_group_name = var.elasticache_config.parameter_group_name
  
  # Clustering
  num_cache_clusters = var.elasticache_config.num_cache_nodes
  
  # High availability
  multi_az_enabled = var.elasticache_config.multi_az_enabled
  
  # Security
  subnet_group_name     = aws_elasticache_subnet_group.main[0].name
  security_group_ids    = [aws_security_group.elasticache[0].id]
  at_rest_encryption_enabled = var.elasticache_config.at_rest_encryption_enabled
  transit_encryption_enabled = var.elasticache_config.transit_encryption_enabled
  auth_token            = var.elasticache_config.auth_token_enabled ? random_password.redis_auth_token[0].result : null
  
  # Backup
  snapshot_retention_limit = var.elasticache_config.snapshot_retention_limit
  snapshot_window         = var.elasticache_config.snapshot_window
  
  # Maintenance
  maintenance_window = var.elasticache_config.maintenance_window
  
  # Notifications
  notification_topic_arn = var.elasticache_config.notification_topic_arn
  
  tags = merge(var.global_tags, {
    Name = var.elasticache_config.cluster_id
    Type = "elasticache-replication-group"
  })
}

# Random password for Redis auth token
resource "random_password" "redis_auth_token" {
  count = var.enable_elasticache && var.elasticache_config.auth_token_enabled ? 1 : 0
  
  length  = 128
  special = false
}

# ===================================================================
# 🔄 APPLICATION LOAD BALANCER
# ===================================================================

# Application Load Balancer
resource "aws_lb" "main" {
  count = var.enable_alb ? 1 : 0
  
  name               = var.alb_config.name
  load_balancer_type = var.alb_config.load_balancer_type
  scheme             = var.alb_config.scheme
  
  subnets         = aws_subnet.public[*].id
  security_groups = [aws_security_group.alb[0].id]
  
  enable_deletion_protection = var.alb_config.enable_deletion_protection
  enable_http2              = var.alb_config.enable_http2
  idle_timeout              = var.alb_config.idle_timeout
  
  # Access logs
  dynamic "access_logs" {
    for_each = var.alb_config.access_logs.enabled ? [var.alb_config.access_logs] : []
    content {
      bucket  = aws_s3_bucket.alb_logs[0].bucket
      prefix  = access_logs.value.prefix
      enabled = access_logs.value.enabled
    }
  }
  
  tags = merge(var.global_tags, {
    Name = var.alb_config.name
    Type = "application-load-balancer"
  })
}

# S3 bucket for ALB access logs
resource "aws_s3_bucket" "alb_logs" {
  count = var.enable_alb && var.alb_config.access_logs.enabled ? 1 : 0
  
  bucket        = var.alb_config.access_logs.bucket
  force_destroy = false
  
  tags = merge(var.global_tags, {
    Name = var.alb_config.access_logs.bucket
    Type = "alb-logs-bucket"
  })
}

# ===================================================================
# 📦 S3 BUCKETS
# ===================================================================

# S3 Buckets for regional data
resource "aws_s3_bucket" "regional_buckets" {
  for_each = var.s3_buckets
  
  bucket        = each.value.name
  force_destroy = false
  
  tags = merge(var.global_tags, {
    Name    = each.value.name
    Type    = "s3-bucket"
    Purpose = each.key
  })
}

# S3 Bucket versioning
resource "aws_s3_bucket_versioning" "regional_buckets" {
  for_each = var.s3_buckets
  
  bucket = aws_s3_bucket.regional_buckets[each.key].id
  versioning_configuration {
    status = each.value.versioning_enabled ? "Enabled" : "Disabled"
  }
}

# S3 Bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "regional_buckets" {
  for_each = var.s3_buckets
  
  bucket = aws_s3_bucket.regional_buckets[each.key].id
  
  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.s3.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

# S3 Bucket public access block
resource "aws_s3_bucket_public_access_block" "regional_buckets" {
  for_each = var.s3_buckets
  
  bucket = aws_s3_bucket.regional_buckets[each.key].id
  
  block_public_acls       = lookup(each.value, "block_public_acls", true)
  block_public_policy     = lookup(each.value, "block_public_policy", true)
  ignore_public_acls      = lookup(each.value, "ignore_public_acls", true)
  restrict_public_buckets = lookup(each.value, "restrict_public_buckets", true)
}

# S3 Bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "regional_buckets" {
  for_each = { for k, v in var.s3_buckets : k => v if lookup(v, "lifecycle_configuration", null) != null }
  
  bucket = aws_s3_bucket.regional_buckets[each.key].id
  
  rule {
    id     = "lifecycle_rule"
    status = "Enabled"
    
    transition {
      days          = each.value.lifecycle_configuration.transition_to_ia_days
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = each.value.lifecycle_configuration.transition_to_glacier_days
      storage_class = "GLACIER"
    }
    
    dynamic "transition" {
      for_each = lookup(each.value.lifecycle_configuration, "transition_to_deep_archive_days", null) != null ? [1] : []
      content {
        days          = each.value.lifecycle_configuration.transition_to_deep_archive_days
        storage_class = "DEEP_ARCHIVE"
      }
    }
    
    expiration {
      days = each.value.lifecycle_configuration.expiration_days
    }
  }
}

# S3 Bucket CORS configuration
resource "aws_s3_bucket_cors_configuration" "regional_buckets" {
  for_each = { for k, v in var.s3_buckets : k => v if lookup(v, "cors_configuration", null) != null }
  
  bucket = aws_s3_bucket.regional_buckets[each.key].id
  
  cors_rule {
    allowed_headers = each.value.cors_configuration.allowed_headers
    allowed_methods = each.value.cors_configuration.allowed_methods
    allowed_origins = each.value.cors_configuration.allowed_origins
    expose_headers  = each.value.cors_configuration.expose_headers
    max_age_seconds = each.value.cors_configuration.max_age_seconds
  }
} 
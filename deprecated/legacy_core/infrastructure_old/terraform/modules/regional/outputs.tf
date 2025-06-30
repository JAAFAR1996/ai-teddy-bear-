# Regional Infrastructure Module Outputs

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "Database subnet IDs"
  value       = aws_subnet.database[*].id
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_certificate_authority_data" {
  description = "EKS cluster certificate authority data"
  value       = aws_eks_cluster.main.certificate_authority[0].data
}

output "cluster_arn" {
  description = "EKS cluster ARN"
  value       = aws_eks_cluster.main.arn
}

output "cluster_oidc_issuer_url" {
  description = "EKS cluster OIDC issuer URL"
  value       = aws_eks_cluster.main.identity[0].oidc[0].issuer
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = var.enable_rds ? aws_db_instance.main[0].endpoint : null
}

output "rds_arn" {
  description = "RDS instance ARN"
  value       = var.enable_rds ? aws_db_instance.main[0].arn : null
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = var.enable_elasticache ? aws_elasticache_replication_group.main[0].primary_endpoint_address : null
}

output "redis_port" {
  description = "Redis cluster port"
  value       = var.enable_elasticache ? aws_elasticache_replication_group.main[0].port : null
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = var.enable_alb ? aws_lb.main[0].dns_name : null
}

output "alb_zone_id" {
  description = "ALB zone ID"
  value       = var.enable_alb ? aws_lb.main[0].zone_id : null
}

output "alb_arn" {
  description = "ALB ARN"
  value       = var.enable_alb ? aws_lb.main[0].arn : null
}

output "kms_key_arn" {
  description = "KMS key ARN"
  value       = aws_kms_key.eks.arn
}

output "security_group_ids" {
  description = "Security group IDs"
  value = {
    eks_cluster   = aws_security_group.eks_cluster.id
    eks_nodes     = aws_security_group.eks_nodes.id
    rds          = var.enable_rds ? aws_security_group.rds[0].id : null
    elasticache  = var.enable_elasticache ? aws_security_group.elasticache[0].id : null
    alb          = var.enable_alb ? aws_security_group.alb[0].id : null
  }
}

output "iam_role_arns" {
  description = "IAM role ARNs"
  value = {
    eks_cluster_role     = aws_iam_role.eks_cluster.arn
    eks_node_group_role  = aws_iam_role.eks_node_group.arn
    ai_service_role      = aws_iam_role.ai_service_role.arn
    child_service_role   = aws_iam_role.child_service_role.arn
    safety_service_role  = aws_iam_role.safety_service_role.arn
    alb_controller_role  = aws_iam_role.alb_controller_role.arn
    rds_monitoring_role  = var.enable_rds ? aws_iam_role.rds_enhanced_monitoring[0].arn : null
  }
}

output "s3_bucket_names" {
  description = "S3 bucket names"
  value = {
    for bucket_key, bucket in aws_s3_bucket.regional_buckets : bucket_key => bucket.bucket
  }
}

output "s3_bucket_arns" {
  description = "S3 bucket ARNs"
  value = {
    for bucket_key, bucket in aws_s3_bucket.regional_buckets : bucket_key => bucket.arn
  }
}

output "cloudwatch_log_groups" {
  description = "CloudWatch log group names"
  value = [
    aws_cloudwatch_log_group.eks_cluster.name
  ]
}

output "nat_gateway_ips" {
  description = "NAT Gateway public IPs"
  value       = aws_eip.nat[*].public_ip
}

output "prometheus_endpoint" {
  description = "Prometheus endpoint URL"
  value       = "http://prometheus.${var.region_name}.local:9090"
}

output "grafana_endpoint" {
  description = "Grafana endpoint URL"
  value       = "http://grafana.${var.region_name}.local:3000"
}

output "jaeger_endpoint" {
  description = "Jaeger endpoint URL"
  value       = "http://jaeger.${var.region_name}.local:16686"
}

output "regional_summary" {
  description = "Summary of regional infrastructure"
  value = {
    region_name = var.region_name
    vpc = {
      id         = aws_vpc.main.id
      cidr_block = aws_vpc.main.cidr_block
      subnets = {
        public   = length(aws_subnet.public)
        private  = length(aws_subnet.private)
        database = length(aws_subnet.database)
      }
    }
    eks = {
      cluster_name    = aws_eks_cluster.main.name
      cluster_version = aws_eks_cluster.main.version
      node_groups     = length(var.node_groups)
    }
    databases = {
      rds_enabled         = var.enable_rds
      elasticache_enabled = var.enable_elasticache
    }
    load_balancer = {
      alb_enabled = var.enable_alb
    }
    storage = {
      s3_buckets = length(var.s3_buckets)
    }
  }
} 
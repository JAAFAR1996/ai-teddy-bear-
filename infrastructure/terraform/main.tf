# ===================================================================
# 🌍 AI Teddy Bear - Multi-Region Infrastructure
# Enterprise-Grade Production Deployment
# Infrastructure Team Lead: Senior Infrastructure Engineer
# Date: January 2025
# ===================================================================

terraform {
  required_version = ">= 1.6.0"
  
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
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }

  # S3 Backend Configuration for Enterprise State Management
  backend "s3" {
    bucket         = "ai-teddy-terraform-state-prod"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "ai-teddy-terraform-locks"
    
    # Versioning and lifecycle management
    versioning_enabled = true
    force_path_style   = false
    
    # Security
    server_side_encryption_configuration {
      rule {
        apply_server_side_encryption_by_default {
          sse_algorithm = "AES256"
        }
      }
    }
  }
}

# ===================================================================
# 🌐 GLOBAL CONFIGURATION
# ===================================================================

locals {
  # Project Configuration
  project_name = "ai-teddy-bear"
  environment  = var.environment
  
  # Global Tags - Enterprise Standard
  global_tags = {
    Project             = local.project_name
    Environment         = local.environment
    ManagedBy          = "Terraform"
    Owner              = "Infrastructure-Team"
    BusinessUnit       = "AI-Products"
    CostCenter         = "AITECH-001"
    ComplianceLevel    = "SOC2-COPPA"
    DataClassification = "Confidential"
    BackupPolicy       = "Critical"
    MonitoringLevel    = "Enhanced"
    SecurityLevel      = "High"
    
    # Child Safety Tags - Critical for COPPA Compliance
    ChildSafetyEnabled = "true"
    COPPACompliant     = "true"
    DataRetention      = "7-years"
    AuditRequired      = "true"
  }
  
  # Regions Configuration
  regions = {
    primary = {
      name               = "us-east-1"
      description        = "Primary Region - North America"
      availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
      is_primary         = true
      disaster_recovery  = true
    }
    europe = {
      name               = "eu-west-1"
      description        = "Europe Region - GDPR Compliance"
      availability_zones = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
      is_primary         = false
      disaster_recovery  = true
    }
    asia = {
      name               = "ap-southeast-1"
      description        = "Asia Pacific Region"
      availability_zones = ["ap-southeast-1a", "ap-southeast-1b", "ap-southeast-1c"]
      is_primary         = false
      disaster_recovery  = false
    }
  }
}

# ===================================================================
# 🔐 RANDOM GENERATORS FOR SECURITY
# ===================================================================

resource "random_id" "global_suffix" {
  byte_length = 4
}

resource "random_password" "master_key" {
  length  = 32
  special = true
}

# ===================================================================
# 🌍 GLOBAL INFRASTRUCTURE MODULE
# ===================================================================

module "global_infrastructure" {
  source = "./modules/global"
  
  # Global Configuration
  project_name    = local.project_name
  environment     = local.environment
  global_tags     = local.global_tags
  random_suffix   = random_id.global_suffix.hex
  
  # Domain and DNS
  domain_name     = var.domain_name
  hosted_zone_id  = var.hosted_zone_id
  
  # Global Accelerator Configuration
  enable_global_accelerator = var.enable_global_accelerator
  accelerator_config = {
    enabled               = true
    flow_logs_enabled     = true
    flow_logs_s3_bucket   = "ai-teddy-global-accelerator-logs"
    ip_address_type       = "IPV4"
    client_affinity       = "SOURCE_IP"
  }
  
  # CloudFront Distribution
  enable_cloudfront = var.enable_cloudfront
  cloudfront_config = {
    price_class                = "PriceClass_All"
    minimum_protocol_version   = "TLSv1.2_2021"
    ssl_support_method         = "sni-only"
    compress                   = true
    viewer_protocol_policy     = "redirect-to-https"
    allowed_methods           = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods            = ["GET", "HEAD"]
  }
  
  # DynamoDB Global Tables
  enable_global_tables = var.enable_global_tables
  global_tables = {
    children = {
      name               = "ai-teddy-children"
      billing_mode       = "PAY_PER_REQUEST"
      deletion_protection = true
      point_in_time_recovery = true
      server_side_encryption = true
      stream_enabled     = true
      stream_view_type   = "NEW_AND_OLD_IMAGES"
      
      # Global Secondary Indexes
      global_secondary_indexes = [
        {
          name               = "udid-index"
          hash_key          = "udid"
          projection_type   = "ALL"
        },
        {
          name               = "parent-email-index"
          hash_key          = "parent_email"
          projection_type   = "INCLUDE"
          non_key_attributes = ["child_name", "age", "created_at"]
        }
      ]
    }
    
    conversations = {
      name               = "ai-teddy-conversations"
      billing_mode       = "PAY_PER_REQUEST"
      deletion_protection = true
      point_in_time_recovery = true
      server_side_encryption = true
      stream_enabled     = true
      stream_view_type   = "NEW_AND_OLD_IMAGES"
      ttl_enabled        = true
      ttl_attribute_name = "expires_at"
      
      global_secondary_indexes = [
        {
          name               = "child-timestamp-index"
          hash_key          = "child_id"
          range_key         = "timestamp"
          projection_type   = "ALL"
        }
      ]
    }
    
    safety_events = {
      name               = "ai-teddy-safety-events"
      billing_mode       = "PAY_PER_REQUEST"
      deletion_protection = true
      point_in_time_recovery = true
      server_side_encryption = true
      stream_enabled     = true
      stream_view_type   = "NEW_AND_OLD_IMAGES"
      
      global_secondary_indexes = [
        {
          name               = "severity-timestamp-index"
          hash_key          = "severity"
          range_key         = "timestamp"
          projection_type   = "ALL"
        }
      ]
    }
  }
  
  # WAF Configuration
  enable_waf = var.enable_waf
  waf_config = {
    name = "ai-teddy-global-waf"
    rules = [
      {
        name     = "AWSManagedRulesCommonRuleSet"
        priority = 1
        vendor   = "AWS"
      },
      {
        name     = "AWSManagedRulesKnownBadInputsRuleSet"
        priority = 2
        vendor   = "AWS"
      },
      {
        name     = "AWSManagedRulesSQLiRuleSet"
        priority = 3
        vendor   = "AWS"
      }
    ]
  }
  
  # Certificate Manager
  enable_acm = var.enable_acm
  certificates = {
    primary = {
      domain_name               = var.domain_name
      subject_alternative_names = ["*.${var.domain_name}"]
      validation_method         = "DNS"
    }
  }
  
  # Global monitoring
  enable_global_monitoring = true
  
  depends_on = [random_id.global_suffix]
}

# ===================================================================
# 🏗️ REGIONAL DEPLOYMENTS
# ===================================================================

module "regional_infrastructure" {
  source = "./modules/regional"
  
  for_each = local.regions
  
  # Basic Configuration
  project_name     = local.project_name
  environment      = local.environment
  region_name      = each.value.name
  region_config    = each.value
  global_tags      = local.global_tags
  random_suffix    = random_id.global_suffix.hex
  
  # Global dependencies
  global_accelerator_arn = module.global_infrastructure.global_accelerator_arn
  cloudfront_domain      = module.global_infrastructure.cloudfront_domain_name
  global_waf_arn        = module.global_infrastructure.waf_arn
  
  # Network Configuration
  vpc_config = {
    cidr_block           = var.region_vpc_cidrs[each.key]
    enable_dns_hostnames = true
    enable_dns_support   = true
    enable_nat_gateway   = true
    single_nat_gateway   = false
    enable_vpn_gateway   = false
    
    # Flow logs for security
    enable_flow_log                      = true
    flow_log_destination_type           = "cloud-watch-logs"
    flow_log_log_format                 = null
    flow_log_traffic_type               = "ALL"
    flow_log_max_aggregation_interval   = 60
  }
  
  # EKS Configuration
  eks_config = {
    cluster_name                    = "ai-teddy-${each.key}"
    cluster_version                 = var.eks_cluster_version
    cluster_endpoint_private_access = true
    cluster_endpoint_public_access  = true
    cluster_endpoint_public_access_cidrs = var.eks_public_access_cidrs
    
    # Enhanced security
    cluster_encryption_config = [
      {
        provider_key_arn = module.regional_infrastructure[each.key].kms_key_arn
        resources        = ["secrets"]
      }
    ]
    
    # Logging configuration
    cluster_enabled_log_types = [
      "api", "audit", "authenticator", "controllerManager", "scheduler"
    ]
    
    # IRSA (IAM Roles for Service Accounts)
    enable_irsa = true
    
    # Cluster security group
    cluster_security_group_additional_rules = {
      ingress_nodes_ephemeral_ports_tcp = {
        description                = "Node groups to cluster API"
        protocol                   = "tcp"
        from_port                  = 1025
        to_port                    = 65535
        type                       = "ingress"
        source_node_security_group = true
      }
    }
  }
  
  # Node Groups Configuration
  node_groups = {
    # General purpose nodes
    general = {
      name            = "general-${each.key}"
      instance_types  = var.node_group_instance_types.general
      capacity_type   = "ON_DEMAND"
      disk_size       = 50
      disk_type       = "gp3"
      
      # Scaling configuration
      min_size         = var.node_group_scaling.general.min_size
      max_size         = var.node_group_scaling.general.max_size
      desired_size     = var.node_group_scaling.general.desired_size
      
      # Update configuration
      max_unavailable_percentage = 25
      
      # Security
      remote_access = {
        ec2_ssh_key               = var.ec2_key_name
        source_security_group_ids = []
      }
      
      # Labels and taints
      k8s_labels = {
        "role"                          = "general"
        "node.kubernetes.io/node-type"  = "general"
      }
      
      tags = merge(local.global_tags, {
        Name = "ai-teddy-general-${each.key}"
        Type = "general-node-group"
      })
    }
    
    # AI processing nodes with GPU support
    ai_processing = {
      name            = "ai-processing-${each.key}"
      instance_types  = var.node_group_instance_types.ai_processing
      capacity_type   = "ON_DEMAND"
      disk_size       = 100
      disk_type       = "gp3"
      
      # Scaling configuration
      min_size         = var.node_group_scaling.ai_processing.min_size
      max_size         = var.node_group_scaling.ai_processing.max_size
      desired_size     = var.node_group_scaling.ai_processing.desired_size
      
      # Update configuration
      max_unavailable_percentage = 25
      
      # GPU-specific configuration
      ami_type = "AL2_x86_64_GPU"
      
      # Security
      remote_access = {
        ec2_ssh_key               = var.ec2_key_name
        source_security_group_ids = []
      }
      
      # Labels and taints for AI workloads
      k8s_labels = {
        "role"                          = "ai-processing"
        "node.kubernetes.io/node-type"  = "gpu"
        "nvidia.com/gpu.present"        = "true"
      }
      
      taints = {
        ai_workload = {
          key    = "ai-workload"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }
      
      tags = merge(local.global_tags, {
        Name = "ai-teddy-ai-processing-${each.key}"
        Type = "ai-processing-node-group"
      })
    }
    
    # Memory optimized nodes for caching
    memory_optimized = {
      name            = "memory-optimized-${each.key}"
      instance_types  = var.node_group_instance_types.memory_optimized
      capacity_type   = "SPOT"
      disk_size       = 50
      disk_type       = "gp3"
      
      # Scaling configuration
      min_size         = var.node_group_scaling.memory_optimized.min_size
      max_size         = var.node_group_scaling.memory_optimized.max_size
      desired_size     = var.node_group_scaling.memory_optimized.desired_size
      
      # Update configuration
      max_unavailable_percentage = 50  # Higher for spot instances
      
      # Security
      remote_access = {
        ec2_ssh_key               = var.ec2_key_name
        source_security_group_ids = []
      }
      
      # Labels and taints
      k8s_labels = {
        "role"                          = "memory-optimized"
        "node.kubernetes.io/node-type"  = "memory-optimized"
        "spot"                          = "true"
      }
      
      taints = {
        spot_instance = {
          key    = "spot-instance"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }
      
      tags = merge(local.global_tags, {
        Name = "ai-teddy-memory-optimized-${each.key}"
        Type = "memory-optimized-node-group"
      })
    }
  }
  
  # RDS Configuration
  enable_rds = var.enable_rds
  rds_config = {
    identifier             = "ai-teddy-${each.key}"
    engine                = "postgres"
    engine_version        = "15.4"
    instance_class        = var.rds_instance_class
    allocated_storage     = var.rds_allocated_storage
    max_allocated_storage = var.rds_max_allocated_storage
    storage_type          = "gp3"
    storage_encrypted     = true
    
    # Database configuration
    db_name  = "ai_teddy_${replace(each.key, "-", "_")}"
    username = "ai_teddy_admin"
    
    # Backup configuration
    backup_retention_period = 35
    backup_window          = "03:00-04:00"
    maintenance_window     = "sun:04:00-sun:05:00"
    delete_automated_backups = false
    
    # High availability
    multi_az               = each.value.is_primary ? true : false
    
    # Security
    deletion_protection    = true
    skip_final_snapshot   = false
    copy_tags_to_snapshot = true
    
    # Performance insights
    performance_insights_enabled    = true
    performance_insights_retention_period = 7
    
    # Monitoring
    monitoring_interval = 60
    enabled_cloudwatch_logs_exports = ["postgresql"]
  }
  
  # ElastiCache Configuration
  enable_elasticache = var.enable_elasticache
  elasticache_config = {
    cluster_id           = "ai-teddy-${each.key}"
    engine              = "redis"
    engine_version      = "7.0"
    node_type           = var.elasticache_node_type
    num_cache_nodes     = var.elasticache_num_nodes
    parameter_group_name = "default.redis7"
    port                = 6379
    
    # High availability
    multi_az_enabled    = each.value.is_primary ? true : false
    
    # Security
    at_rest_encryption_enabled = true
    transit_encryption_enabled = true
    auth_token_enabled         = true
    
    # Backup
    snapshot_retention_limit = 7
    snapshot_window         = "05:00-06:00"
    
    # Maintenance
    maintenance_window = "sun:06:00-sun:07:00"
    
    # Notifications
    notification_topic_arn = ""
  }
  
  # Application Load Balancer
  enable_alb = var.enable_alb
  alb_config = {
    name               = "ai-teddy-${each.key}"
    load_balancer_type = "application"
    scheme             = "internet-facing"
    
    # Security
    enable_deletion_protection = true
    enable_http2              = true
    idle_timeout              = 60
    
    # Access logs
    access_logs = {
      bucket  = "ai-teddy-alb-logs-${each.key}"
      enabled = true
      prefix  = "alb-logs"
    }
  }
  
  # S3 Buckets for regional data
  s3_buckets = {
    # Audio recordings bucket
    audio_recordings = {
      name                    = "ai-teddy-audio-recordings-${each.key}"
      versioning_enabled      = true
      server_side_encryption  = true
      kms_key_id             = "alias/ai-teddy-s3-key"
      lifecycle_configuration = {
        transition_to_ia_days      = 30
        transition_to_glacier_days = 90
        expiration_days           = 2555  # 7 years for COPPA compliance
      }
      
      # CORS configuration for web uploads
      cors_configuration = {
        allowed_headers = ["*"]
        allowed_methods = ["GET", "PUT", "POST"]
        allowed_origins = ["https://*.${var.domain_name}"]
        expose_headers  = ["ETag"]
        max_age_seconds = 3000
      }
      
      # Public access block
      block_public_acls       = true
      block_public_policy     = true
      ignore_public_acls      = true
      restrict_public_buckets = true
    }
    
    # Application logs bucket
    application_logs = {
      name                   = "ai-teddy-app-logs-${each.key}"
      versioning_enabled     = true
      server_side_encryption = true
      lifecycle_configuration = {
        transition_to_ia_days      = 30
        transition_to_glacier_days = 90
        expiration_days           = 365
      }
    }
    
    # Backup bucket
    backups = {
      name                   = "ai-teddy-backups-${each.key}"
      versioning_enabled     = true
      server_side_encryption = true
      lifecycle_configuration = {
        transition_to_ia_days        = 30
        transition_to_glacier_days   = 90
        transition_to_deep_archive_days = 365
        expiration_days             = 2555  # 7 years
      }
    }
  }
  
  # Monitoring and observability
  enable_monitoring = true
  monitoring_config = {
    # CloudWatch configuration
    cloudwatch = {
      log_groups = [
        "/aws/eks/ai-teddy-${each.key}/cluster",
        "/aws/rds/instance/ai-teddy-${each.key}/postgresql",
        "/aws/elasticache/ai-teddy-${each.key}"
      ]
      retention_in_days = 30
    }
    
    # X-Ray tracing
    xray = {
      enabled = true
      sampling_rate = 0.1
    }
    
    # Custom metrics
    custom_metrics = [
      "ChildSafetyViolations",
      "AIResponseLatency",
      "COPPAComplianceRate",
      "SystemAvailability"
    ]
  }
  
  # Disaster recovery configuration
  disaster_recovery = {
    enabled                = each.value.disaster_recovery
    backup_schedule       = "cron(0 2 * * ? *)"  # Daily at 2 AM
    cross_region_backup   = each.value.is_primary ? false : true
    rpo_minutes          = 60  # Recovery Point Objective
    rto_minutes          = 30  # Recovery Time Objective
  }
  
  # Cost optimization
  cost_optimization = {
    enable_spot_instances    = true
    enable_scheduled_scaling = true
    enable_cost_alerts      = true
    monthly_budget_usd      = var.monthly_budget_per_region
  }
  
  providers = {
    aws = aws
  }
  
  depends_on = [
    module.global_infrastructure,
    random_id.global_suffix
  ]
}

# ===================================================================
# 🔗 CROSS-REGION DEPENDENCIES
# ===================================================================

# VPC Peering between regions for disaster recovery
resource "aws_vpc_peering_connection" "cross_region" {
  for_each = {
    for pair in [
      { from = "primary", to = "europe" },
      { from = "primary", to = "asia" },
      { from = "europe", to = "asia" }
    ] : "${pair.from}-${pair.to}" => pair
  }
  
  provider = aws.us-east-1
  
  vpc_id        = module.regional_infrastructure[each.value.from].vpc_id
  peer_vpc_id   = module.regional_infrastructure[each.value.to].vpc_id
  peer_region   = local.regions[each.value.to].name
  auto_accept   = false
  
  tags = merge(local.global_tags, {
    Name = "ai-teddy-peering-${each.value.from}-${each.value.to}"
    Type = "cross-region-peering"
  })
}

# ===================================================================
# 📊 OUTPUTS
# ===================================================================

output "global_infrastructure" {
  description = "Global infrastructure outputs"
  value = {
    global_accelerator_dns = module.global_infrastructure.global_accelerator_dns_name
    cloudfront_domain      = module.global_infrastructure.cloudfront_domain_name
    route53_zone_id       = module.global_infrastructure.route53_zone_id
    waf_arn               = module.global_infrastructure.waf_arn
    certificates          = module.global_infrastructure.certificates
  }
}

output "regional_infrastructure" {
  description = "Regional infrastructure outputs"
  value = {
    for region_key, region in local.regions : region_key => {
      region_name      = region.name
      vpc_id          = module.regional_infrastructure[region_key].vpc_id
      vpc_cidr        = module.regional_infrastructure[region_key].vpc_cidr_block
      eks_cluster_name = module.regional_infrastructure[region_key].cluster_name
      eks_endpoint    = module.regional_infrastructure[region_key].cluster_endpoint
      rds_endpoint    = module.regional_infrastructure[region_key].rds_endpoint
      redis_endpoint  = module.regional_infrastructure[region_key].redis_endpoint
      alb_dns_name    = module.regional_infrastructure[region_key].alb_dns_name
      s3_buckets      = module.regional_infrastructure[region_key].s3_bucket_names
    }
  }
  sensitive = true
}

output "security_configuration" {
  description = "Security configuration details"
  value = {
    kms_key_arns          = { for k, v in module.regional_infrastructure : k => v.kms_key_arn }
    security_group_ids    = { for k, v in module.regional_infrastructure : k => v.security_group_ids }
    iam_role_arns        = { for k, v in module.regional_infrastructure : k => v.iam_role_arns }
    ssl_certificate_arns = module.global_infrastructure.certificates
  }
  sensitive = true
}

output "monitoring_endpoints" {
  description = "Monitoring and observability endpoints"
  value = {
    cloudwatch_log_groups = { for k, v in module.regional_infrastructure : k => v.cloudwatch_log_groups }
    prometheus_endpoints  = { for k, v in module.regional_infrastructure : k => v.prometheus_endpoint }
    grafana_endpoints    = { for k, v in module.regional_infrastructure : k => v.grafana_endpoint }
    jaeger_endpoints     = { for k, v in module.regional_infrastructure : k => v.jaeger_endpoint }
  }
} 
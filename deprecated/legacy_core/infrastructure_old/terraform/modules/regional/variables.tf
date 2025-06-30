# Regional Infrastructure Module Variables

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "region_name" {
  description = "AWS region name"
  type        = string
}

variable "region_config" {
  description = "Region configuration"
  type = object({
    name               = string
    description        = string
    availability_zones = list(string)
    is_primary         = bool
    disaster_recovery  = bool
  })
}

variable "global_tags" {
  description = "Global tags to apply to all resources"
  type        = map(string)
}

variable "random_suffix" {
  description = "Random suffix for unique resource naming"
  type        = string
}

variable "vpc_config" {
  description = "VPC configuration"
  type = object({
    cidr_block           = string
    enable_dns_hostnames = bool
    enable_dns_support   = bool
    enable_nat_gateway   = bool
    single_nat_gateway   = bool
    enable_vpn_gateway   = bool
  })
}

variable "eks_config" {
  description = "EKS cluster configuration"
  type = object({
    cluster_name                    = string
    cluster_version                 = string
    cluster_endpoint_private_access = bool
    cluster_endpoint_public_access  = bool
    cluster_endpoint_public_access_cidrs = list(string)
    cluster_enabled_log_types       = list(string)
    enable_irsa                     = bool
  })
}

variable "node_groups" {
  description = "EKS node groups configuration"
  type = map(object({
    name            = string
    instance_types  = list(string)
    capacity_type   = string
    disk_size       = number
    disk_type       = string
    min_size        = number
    max_size        = number
    desired_size    = number
    max_unavailable_percentage = number
    ami_type        = optional(string)
    remote_access   = optional(object({
      ec2_ssh_key               = string
      source_security_group_ids = list(string)
    }))
    k8s_labels = optional(map(string))
    taints = optional(map(object({
      key    = string
      value  = string
      effect = string
    })))
    tags = map(string)
  }))
}

variable "enable_rds" {
  description = "Enable RDS PostgreSQL instance"
  type        = bool
  default     = true
}

variable "rds_config" {
  description = "RDS configuration"
  type = object({
    identifier             = string
    engine                = string
    engine_version        = string
    instance_class        = string
    allocated_storage     = number
    max_allocated_storage = number
    storage_type          = string
    storage_encrypted     = bool
    db_name               = string
    username              = string
    backup_retention_period = number
    backup_window         = string
    maintenance_window    = string
    delete_automated_backups = bool
    multi_az              = bool
    deletion_protection   = bool
    skip_final_snapshot   = bool
    copy_tags_to_snapshot = bool
    performance_insights_enabled = bool
    performance_insights_retention_period = number
    monitoring_interval   = number
    enabled_cloudwatch_logs_exports = list(string)
  })
}

variable "enable_elasticache" {
  description = "Enable ElastiCache Redis cluster"
  type        = bool
  default     = true
}

variable "elasticache_config" {
  description = "ElastiCache configuration"
  type = object({
    cluster_id           = string
    engine              = string
    engine_version      = string
    node_type           = string
    num_cache_nodes     = number
    parameter_group_name = string
    port                = number
    multi_az_enabled    = bool
    at_rest_encryption_enabled = bool
    transit_encryption_enabled = bool
    auth_token_enabled  = bool
    snapshot_retention_limit = number
    snapshot_window     = string
    maintenance_window  = string
    notification_topic_arn = string
  })
}

variable "enable_alb" {
  description = "Enable Application Load Balancer"
  type        = bool
  default     = true
}

variable "alb_config" {
  description = "ALB configuration"
  type = object({
    name                       = string
    load_balancer_type         = string
    scheme                     = string
    enable_deletion_protection = bool
    enable_http2              = bool
    idle_timeout              = number
    access_logs = object({
      bucket  = string
      enabled = bool
      prefix  = string
    })
  })
}

variable "s3_buckets" {
  description = "S3 buckets configuration"
  type = map(object({
    name                   = string
    versioning_enabled     = bool
    server_side_encryption = bool
    kms_key_id            = optional(string)
    lifecycle_configuration = optional(object({
      transition_to_ia_days      = number
      transition_to_glacier_days = number
      transition_to_deep_archive_days = optional(number)
      expiration_days           = number
    }))
    cors_configuration = optional(object({
      allowed_headers = list(string)
      allowed_methods = list(string)
      allowed_origins = list(string)
      expose_headers  = list(string)
      max_age_seconds = number
    }))
    block_public_acls       = optional(bool)
    block_public_policy     = optional(bool)
    ignore_public_acls      = optional(bool)
    restrict_public_buckets = optional(bool)
  }))
  default = {}
}

variable "enable_monitoring" {
  description = "Enable monitoring features"
  type        = bool
  default     = true
}

variable "monitoring_config" {
  description = "Monitoring configuration"
  type = object({
    cloudwatch = object({
      log_groups        = list(string)
      retention_in_days = number
    })
    xray = object({
      enabled       = bool
      sampling_rate = number
    })
    custom_metrics = list(string)
  })
  default = {
    cloudwatch = {
      log_groups        = []
      retention_in_days = 30
    }
    xray = {
      enabled       = true
      sampling_rate = 0.1
    }
    custom_metrics = []
  }
}

variable "disaster_recovery" {
  description = "Disaster recovery configuration"
  type = object({
    enabled                = bool
    backup_schedule       = string
    cross_region_backup   = bool
    rpo_minutes          = number
    rto_minutes          = number
  })
  default = {
    enabled                = true
    backup_schedule       = "cron(0 2 * * ? *)"
    cross_region_backup   = false
    rpo_minutes          = 60
    rto_minutes          = 30
  }
}

variable "cost_optimization" {
  description = "Cost optimization configuration"
  type = object({
    enable_spot_instances    = bool
    enable_scheduled_scaling = bool
    enable_cost_alerts      = bool
    monthly_budget_usd      = number
  })
  default = {
    enable_spot_instances    = true
    enable_scheduled_scaling = true
    enable_cost_alerts      = true
    monthly_budget_usd      = 5000
  }
}

# Dependencies from global infrastructure
variable "global_accelerator_arn" {
  description = "Global Accelerator ARN from global module"
  type        = string
  default     = ""
}

variable "cloudfront_domain" {
  description = "CloudFront domain name from global module"
  type        = string
  default     = ""
}

variable "global_waf_arn" {
  description = "Global WAF ARN from global module"
  type        = string
  default     = ""
} 
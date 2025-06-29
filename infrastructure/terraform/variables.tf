# ===================================================================
# 🔧 AI Teddy Bear - Terraform Variables
# Enterprise-Grade Multi-Region Variables Configuration
# Infrastructure Team Lead: Senior Infrastructure Engineer
# Date: January 2025
# ===================================================================

# ===================================================================
# 🌐 GLOBAL VARIABLES
# ===================================================================

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "domain_name" {
  description = "Primary domain name for the application"
  type        = string
  default     = "ai-teddy.com"
  
  validation {
    condition     = can(regex("^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\\.[a-z]{2,}$", var.domain_name))
    error_message = "Domain name must be a valid DNS name."
  }
}

variable "hosted_zone_id" {
  description = "Route53 hosted zone ID for the domain"
  type        = string
  default     = ""
}

variable "aws_account_id" {
  description = "AWS Account ID for resource naming and security"
  type        = string
  default     = ""
  
  validation {
    condition     = can(regex("^[0-9]{12}$", var.aws_account_id)) || var.aws_account_id == ""
    error_message = "AWS Account ID must be a 12-digit number."
  }
}

# ===================================================================
# 🌍 REGIONAL CONFIGURATION
# ===================================================================

variable "region_vpc_cidrs" {
  description = "VPC CIDR blocks for each region"
  type        = map(string)
  default = {
    primary = "10.0.0.0/16"   # us-east-1
    europe  = "10.1.0.0/16"   # eu-west-1
    asia    = "10.2.0.0/16"   # ap-southeast-1
  }
  
  validation {
    condition = alltrue([
      for cidr in values(var.region_vpc_cidrs) : can(cidrhost(cidr, 0))
    ])
    error_message = "All CIDR blocks must be valid IPv4 CIDR notation."
  }
}

# ===================================================================
# 🔐 SECURITY VARIABLES
# ===================================================================

variable "ec2_key_name" {
  description = "EC2 Key Pair name for instance access"
  type        = string
  default     = "ai-teddy-keypair"
}

variable "eks_public_access_cidrs" {
  description = "CIDR blocks allowed to access EKS API server"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Restrict in production
  
  validation {
    condition = alltrue([
      for cidr in var.eks_public_access_cidrs : can(cidrhost(cidr, 0))
    ])
    error_message = "All CIDR blocks must be valid IPv4 CIDR notation."
  }
}

variable "enable_encryption_at_rest" {
  description = "Enable encryption at rest for all storage services"
  type        = bool
  default     = true
}

variable "enable_encryption_in_transit" {
  description = "Enable encryption in transit for all communications"
  type        = bool
  default     = true
}

# ===================================================================
# 🏗️ EKS CLUSTER CONFIGURATION
# ===================================================================

variable "eks_cluster_version" {
  description = "Kubernetes version for EKS clusters"
  type        = string
  default     = "1.28"
  
  validation {
    condition     = can(regex("^1\\.(2[4-9]|[3-9][0-9])$", var.eks_cluster_version))
    error_message = "EKS cluster version must be 1.24 or higher."
  }
}

variable "node_group_instance_types" {
  description = "Instance types for different node groups"
  type = object({
    general          = list(string)
    ai_processing    = list(string)
    memory_optimized = list(string)
  })
  default = {
    general          = ["t3.large", "t3.xlarge"]
    ai_processing    = ["g4dn.xlarge", "g4dn.2xlarge"]
    memory_optimized = ["r5.large", "r5.xlarge"]
  }
}

variable "node_group_scaling" {
  description = "Scaling configuration for node groups"
  type = object({
    general = object({
      min_size     = number
      max_size     = number
      desired_size = number
    })
    ai_processing = object({
      min_size     = number
      max_size     = number
      desired_size = number
    })
    memory_optimized = object({
      min_size     = number
      max_size     = number
      desired_size = number
    })
  })
  default = {
    general = {
      min_size     = 2
      max_size     = 10
      desired_size = 3
    }
    ai_processing = {
      min_size     = 1
      max_size     = 5
      desired_size = 2
    }
    memory_optimized = {
      min_size     = 1
      max_size     = 8
      desired_size = 2
    }
  }
  
  validation {
    condition = alltrue([
      var.node_group_scaling.general.min_size <= var.node_group_scaling.general.desired_size,
      var.node_group_scaling.general.desired_size <= var.node_group_scaling.general.max_size,
      var.node_group_scaling.ai_processing.min_size <= var.node_group_scaling.ai_processing.desired_size,
      var.node_group_scaling.ai_processing.desired_size <= var.node_group_scaling.ai_processing.max_size,
      var.node_group_scaling.memory_optimized.min_size <= var.node_group_scaling.memory_optimized.desired_size,
      var.node_group_scaling.memory_optimized.desired_size <= var.node_group_scaling.memory_optimized.max_size
    ])
    error_message = "Node group scaling: min_size <= desired_size <= max_size."
  }
}

# ===================================================================
# 🗄️ DATABASE CONFIGURATION
# ===================================================================

variable "enable_rds" {
  description = "Enable RDS PostgreSQL instances"
  type        = bool
  default     = true
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.large"
  
  validation {
    condition     = can(regex("^db\\.[a-z0-9]+\\.(micro|small|medium|large|xlarge|[0-9]+xlarge)$", var.rds_instance_class))
    error_message = "RDS instance class must be a valid AWS RDS instance type."
  }
}

variable "rds_allocated_storage" {
  description = "Initial allocated storage for RDS instances (GB)"
  type        = number
  default     = 100
  
  validation {
    condition     = var.rds_allocated_storage >= 20 && var.rds_allocated_storage <= 65536
    error_message = "RDS allocated storage must be between 20 and 65536 GB."
  }
}

variable "rds_max_allocated_storage" {
  description = "Maximum allocated storage for RDS auto-scaling (GB)"
  type        = number
  default     = 1000
  
  validation {
    condition     = var.rds_max_allocated_storage >= var.rds_allocated_storage
    error_message = "RDS max allocated storage must be >= allocated storage."
  }
}

# ===================================================================
# 📊 CACHE CONFIGURATION
# ===================================================================

variable "enable_elasticache" {
  description = "Enable ElastiCache Redis clusters"
  type        = bool
  default     = true
}

variable "elasticache_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.r6g.large"
  
  validation {
    condition     = can(regex("^cache\\.[a-z0-9]+\\.(micro|small|medium|large|xlarge|[0-9]+xlarge)$", var.elasticache_node_type))
    error_message = "ElastiCache node type must be a valid AWS ElastiCache instance type."
  }
}

variable "elasticache_num_nodes" {
  description = "Number of ElastiCache nodes"
  type        = number
  default     = 2
  
  validation {
    condition     = var.elasticache_num_nodes >= 1 && var.elasticache_num_nodes <= 20
    error_message = "ElastiCache number of nodes must be between 1 and 20."
  }
}

# ===================================================================
# 🌐 GLOBAL SERVICES CONFIGURATION
# ===================================================================

variable "enable_global_accelerator" {
  description = "Enable AWS Global Accelerator for low latency"
  type        = bool
  default     = true
}

variable "enable_cloudfront" {
  description = "Enable CloudFront CDN distribution"
  type        = bool
  default     = true
}

variable "enable_global_tables" {
  description = "Enable DynamoDB Global Tables"
  type        = bool
  default     = true
}

variable "enable_waf" {
  description = "Enable AWS WAF for application protection"
  type        = bool
  default     = true
}

variable "enable_acm" {
  description = "Enable AWS Certificate Manager for SSL/TLS certificates"
  type        = bool
  default     = true
}

# ===================================================================
# 🔄 LOAD BALANCER CONFIGURATION
# ===================================================================

variable "enable_alb" {
  description = "Enable Application Load Balancer in each region"
  type        = bool
  default     = true
}

variable "alb_access_logs_retention_days" {
  description = "Retention period for ALB access logs"
  type        = number
  default     = 30
  
  validation {
    condition     = var.alb_access_logs_retention_days >= 1 && var.alb_access_logs_retention_days <= 3653
    error_message = "ALB access logs retention must be between 1 and 3653 days."
  }
}

# ===================================================================
# 📊 MONITORING CONFIGURATION
# ===================================================================

variable "enable_enhanced_monitoring" {
  description = "Enable enhanced monitoring for all services"
  type        = bool
  default     = true
}

variable "cloudwatch_log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 30
  
  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653
    ], var.cloudwatch_log_retention_days)
    error_message = "CloudWatch log retention must be a valid retention period."
  }
}

variable "enable_xray_tracing" {
  description = "Enable AWS X-Ray distributed tracing"
  type        = bool
  default     = true
}

variable "xray_sampling_rate" {
  description = "X-Ray sampling rate (0.0 to 1.0)"
  type        = number
  default     = 0.1
  
  validation {
    condition     = var.xray_sampling_rate >= 0.0 && var.xray_sampling_rate <= 1.0
    error_message = "X-Ray sampling rate must be between 0.0 and 1.0."
  }
}

# ===================================================================
# 💰 COST OPTIMIZATION
# ===================================================================

variable "monthly_budget_per_region" {
  description = "Monthly budget per region in USD"
  type        = number
  default     = 5000
  
  validation {
    condition     = var.monthly_budget_per_region >= 100
    error_message = "Monthly budget per region must be at least $100."
  }
}

variable "enable_cost_optimization" {
  description = "Enable cost optimization features (spot instances, scheduled scaling)"
  type        = bool
  default     = true
}

variable "enable_reserved_instances" {
  description = "Enable recommendations for reserved instances"
  type        = bool
  default     = false
}

# ===================================================================
# 🔄 BACKUP AND DISASTER RECOVERY
# ===================================================================

variable "enable_cross_region_backup" {
  description = "Enable cross-region backup for disaster recovery"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 35
  
  validation {
    condition     = var.backup_retention_days >= 1 && var.backup_retention_days <= 35
    error_message = "Backup retention must be between 1 and 35 days."
  }
}

variable "point_in_time_recovery_enabled" {
  description = "Enable point-in-time recovery for databases"
  type        = bool
  default     = true
}

# ===================================================================
# 🏷️ TAGGING CONFIGURATION
# ===================================================================

variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "cost_center" {
  description = "Cost center for billing purposes"
  type        = string
  default     = "AITECH-001"
}

variable "business_unit" {
  description = "Business unit responsible for the resources"
  type        = string
  default     = "AI-Products"
}

variable "data_classification" {
  description = "Data classification level (Public, Internal, Confidential, Restricted)"
  type        = string
  default     = "Confidential"
  
  validation {
    condition     = contains(["Public", "Internal", "Confidential", "Restricted"], var.data_classification)
    error_message = "Data classification must be one of: Public, Internal, Confidential, Restricted."
  }
}

# ===================================================================
# 🔒 COMPLIANCE CONFIGURATION
# ===================================================================

variable "enable_coppa_compliance" {
  description = "Enable COPPA compliance features"
  type        = bool
  default     = true
}

variable "enable_gdpr_compliance" {
  description = "Enable GDPR compliance features"
  type        = bool
  default     = true
}

variable "enable_soc2_compliance" {
  description = "Enable SOC2 compliance features"
  type        = bool
  default     = true
}

variable "data_retention_years" {
  description = "Data retention period in years (for COPPA compliance)"
  type        = number
  default     = 7
  
  validation {
    condition     = var.data_retention_years >= 1 && var.data_retention_years <= 10
    error_message = "Data retention period must be between 1 and 10 years."
  }
}

# ===================================================================
# 🛡️ SECURITY CONFIGURATION
# ===================================================================

variable "enable_advanced_security" {
  description = "Enable advanced security features (GuardDuty, SecurityHub, etc.)"
  type        = bool
  default     = true
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC Flow Logs for network monitoring"
  type        = bool
  default     = true
}

variable "enable_config_rules" {
  description = "Enable AWS Config rules for compliance monitoring"
  type        = bool
  default     = true
}

variable "enable_cloudtrail" {
  description = "Enable CloudTrail for API logging"
  type        = bool
  default     = true
}

# ===================================================================
# 🌍 FEATURE FLAGS
# ===================================================================

variable "enable_dev_features" {
  description = "Enable development and debugging features"
  type        = bool
  default     = false
}

variable "enable_experimental_features" {
  description = "Enable experimental features (use with caution)"
  type        = bool
  default     = false
}

variable "enable_multi_region_deployment" {
  description = "Enable multi-region deployment (set to false for single region)"
  type        = bool
  default     = true
}

# ===================================================================
# 🔧 PERFORMANCE CONFIGURATION
# ===================================================================

variable "enable_performance_insights" {
  description = "Enable Performance Insights for databases"
  type        = bool
  default     = true
}

variable "enable_enhanced_networking" {
  description = "Enable enhanced networking features"
  type        = bool
  default     = true
}

variable "enable_gpu_optimizations" {
  description = "Enable GPU optimizations for AI workloads"
  type        = bool
  default     = true
}

# ===================================================================
# 📱 APPLICATION CONFIGURATION
# ===================================================================

variable "application_name" {
  description = "Application name for resource naming"
  type        = string
  default     = "ai-teddy-bear"
  
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.application_name))
    error_message = "Application name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "application_version" {
  description = "Application version for deployment tracking"
  type        = string
  default     = "1.0.0"
  
  validation {
    condition     = can(regex("^[0-9]+\\.[0-9]+\\.[0-9]+$", var.application_version))
    error_message = "Application version must follow semantic versioning (x.y.z)."
  }
}

# ===================================================================
# 🔧 TERRAFORM CONFIGURATION
# ===================================================================

variable "terraform_state_bucket" {
  description = "S3 bucket for Terraform state storage"
  type        = string
  default     = "ai-teddy-terraform-state-prod"
}

variable "terraform_state_lock_table" {
  description = "DynamoDB table for Terraform state locking"
  type        = string
  default     = "ai-teddy-terraform-locks"
}

variable "enable_state_encryption" {
  description = "Enable encryption for Terraform state"
  type        = bool
  default     = true
} 
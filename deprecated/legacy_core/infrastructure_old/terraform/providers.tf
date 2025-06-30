# ===================================================================
# 🌍 AI Teddy Bear - Multi-Region Providers Configuration
# Enterprise-Grade Provider Setup for AWS Multi-Region Deployment
# Infrastructure Team Lead: Senior Infrastructure Engineer
# Date: January 2025
# ===================================================================

# ===================================================================
# 🏗️ AWS PROVIDERS FOR MULTI-REGION DEPLOYMENT
# ===================================================================

# Primary Region: US East 1 (N. Virginia)
# Primary data center for North America operations
provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
  
  # Enhanced security and compliance
  assume_role {
    role_arn     = var.aws_assume_role_arn != "" ? var.aws_assume_role_arn : null
    session_name = "ai-teddy-terraform-us-east-1"
  }
  
  # Default tags applied to all resources in this region
  default_tags {
    tags = {
      ManagedBy           = "Terraform"
      Project             = "AI-Teddy-Bear"
      Environment         = var.environment
      Region              = "us-east-1"
      PrimaryRegion       = "true"
      BusinessUnit        = "AI-Products"
      CostCenter          = "AITECH-001"
      SecurityLevel       = "High"
      ComplianceLevel     = "SOC2-COPPA"
      DataClassification  = "Confidential"
      ChildSafetyEnabled  = "true"
      COPPACompliant      = "true"
      BackupPolicy        = "Critical"
      MonitoringLevel     = "Enhanced"
      TerraformWorkspace  = terraform.workspace
      CreatedDate         = formatdate("YYYY-MM-DD", timestamp())
    }
  }
  
  # Security and retry configuration
  retry_mode = "adaptive"
  
  # Enhanced request configuration
  max_retries = 3
  
  # Skip metadata API check for faster initialization
  skip_metadata_api_check = false
  
  # Regional services configuration
  skip_requesting_account_id  = false
  skip_credentials_validation = false
  skip_region_validation     = false
}

# Europe Region: EU West 1 (Ireland)
# GDPR compliance and European operations
provider "aws" {
  alias  = "eu-west-1"
  region = "eu-west-1"
  
  # Enhanced security and compliance
  assume_role {
    role_arn     = var.aws_assume_role_arn != "" ? var.aws_assume_role_arn : null
    session_name = "ai-teddy-terraform-eu-west-1"
  }
  
  # Default tags applied to all resources in this region
  default_tags {
    tags = {
      ManagedBy           = "Terraform"
      Project             = "AI-Teddy-Bear"
      Environment         = var.environment
      Region              = "eu-west-1"
      PrimaryRegion       = "false"
      BusinessUnit        = "AI-Products"
      CostCenter          = "AITECH-001"
      SecurityLevel       = "High"
      ComplianceLevel     = "GDPR-SOC2-COPPA"
      DataClassification  = "Confidential"
      ChildSafetyEnabled  = "true"
      COPPACompliant      = "true"
      GDPRCompliant       = "true"
      BackupPolicy        = "Critical"
      MonitoringLevel     = "Enhanced"
      DataResidency       = "EU"
      TerraformWorkspace  = terraform.workspace
      CreatedDate         = formatdate("YYYY-MM-DD", timestamp())
    }
  }
  
  # Security and retry configuration
  retry_mode = "adaptive"
  max_retries = 3
  
  # Regional services configuration
  skip_metadata_api_check     = false
  skip_requesting_account_id  = false
  skip_credentials_validation = false
  skip_region_validation     = false
}

# Asia Pacific Region: AP Southeast 1 (Singapore)
# Asia Pacific operations and low latency for regional users
provider "aws" {
  alias  = "ap-southeast-1"
  region = "ap-southeast-1"
  
  # Enhanced security and compliance
  assume_role {
    role_arn     = var.aws_assume_role_arn != "" ? var.aws_assume_role_arn : null
    session_name = "ai-teddy-terraform-ap-southeast-1"
  }
  
  # Default tags applied to all resources in this region
  default_tags {
    tags = {
      ManagedBy           = "Terraform"
      Project             = "AI-Teddy-Bear"
      Environment         = var.environment
      Region              = "ap-southeast-1"
      PrimaryRegion       = "false"
      BusinessUnit        = "AI-Products"
      CostCenter          = "AITECH-001"
      SecurityLevel       = "High"
      ComplianceLevel     = "SOC2-COPPA"
      DataClassification  = "Confidential"
      ChildSafetyEnabled  = "true"
      COPPACompliant      = "true"
      BackupPolicy        = "Critical"
      MonitoringLevel     = "Enhanced"
      TerraformWorkspace  = terraform.workspace
      CreatedDate         = formatdate("YYYY-MM-DD", timestamp())
    }
  }
  
  # Security and retry configuration
  retry_mode = "adaptive"
  max_retries = 3
  
  # Regional services configuration
  skip_metadata_api_check     = false
  skip_requesting_account_id  = false
  skip_credentials_validation = false
  skip_region_validation     = false
}

# ===================================================================
# 🔧 KUBERNETES PROVIDERS FOR EACH REGION
# ===================================================================

# Kubernetes provider for US East 1
provider "kubernetes" {
  alias = "us-east-1"
  
  host                   = module.regional_infrastructure["primary"].cluster_endpoint
  cluster_ca_certificate = base64decode(module.regional_infrastructure["primary"].cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      module.regional_infrastructure["primary"].cluster_name,
      "--region",
      "us-east-1"
    ]
  }
}

# Kubernetes provider for EU West 1
provider "kubernetes" {
  alias = "eu-west-1"
  
  host                   = module.regional_infrastructure["europe"].cluster_endpoint
  cluster_ca_certificate = base64decode(module.regional_infrastructure["europe"].cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      module.regional_infrastructure["europe"].cluster_name,
      "--region",
      "eu-west-1"
    ]
  }
}

# Kubernetes provider for AP Southeast 1
provider "kubernetes" {
  alias = "ap-southeast-1"
  
  host                   = module.regional_infrastructure["asia"].cluster_endpoint
  cluster_ca_certificate = base64decode(module.regional_infrastructure["asia"].cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      module.regional_infrastructure["asia"].cluster_name,
      "--region",
      "ap-southeast-1"
    ]
  }
}

# ===================================================================
# 🎛️ HELM PROVIDERS FOR EACH REGION
# ===================================================================

# Helm provider for US East 1
provider "helm" {
  alias = "us-east-1"
  
  kubernetes {
    host                   = module.regional_infrastructure["primary"].cluster_endpoint
    cluster_ca_certificate = base64decode(module.regional_infrastructure["primary"].cluster_certificate_authority_data)
    
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = [
        "eks",
        "get-token",
        "--cluster-name",
        module.regional_infrastructure["primary"].cluster_name,
        "--region",
        "us-east-1"
      ]
    }
  }
}

# Helm provider for EU West 1
provider "helm" {
  alias = "eu-west-1"
  
  kubernetes {
    host                   = module.regional_infrastructure["europe"].cluster_endpoint
    cluster_ca_certificate = base64decode(module.regional_infrastructure["europe"].cluster_certificate_authority_data)
    
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = [
        "eks",
        "get-token",
        "--cluster-name",
        module.regional_infrastructure["europe"].cluster_name,
        "--region",
        "eu-west-1"
      ]
    }
  }
}

# Helm provider for AP Southeast 1
provider "helm" {
  alias = "ap-southeast-1"
  
  kubernetes {
    host                   = module.regional_infrastructure["asia"].cluster_endpoint
    cluster_ca_certificate = base64decode(module.regional_infrastructure["asia"].cluster_certificate_authority_data)
    
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = [
        "eks",
        "get-token",
        "--cluster-name",
        module.regional_infrastructure["asia"].cluster_name,
        "--region",
        "ap-southeast-1"
      ]
    }
  }
}

# ===================================================================
# 🔐 TLS PROVIDER FOR CERTIFICATE GENERATION
# ===================================================================

provider "tls" {
  # Global TLS provider for certificate generation and management
  # Used for creating internal certificates, SSH keys, and other cryptographic materials
}

# ===================================================================
# 🎲 RANDOM PROVIDER FOR SECURE RANDOM GENERATION
# ===================================================================

provider "random" {
  # Global random provider for generating secure random values
  # Used for passwords, keys, and unique identifiers
}

# ===================================================================
# ⚙️ ADDITIONAL PROVIDER VARIABLES
# ===================================================================

variable "aws_assume_role_arn" {
  description = "ARN of the AWS role to assume for Terraform operations"
  type        = string
  default     = ""
  
  validation {
    condition = var.aws_assume_role_arn == "" || can(regex("^arn:aws:iam::[0-9]{12}:role/.*", var.aws_assume_role_arn))
    error_message = "AWS assume role ARN must be a valid IAM role ARN or empty string."
  }
}

variable "aws_profile" {
  description = "AWS profile to use for authentication"
  type        = string
  default     = ""
}

variable "terraform_version_constraint" {
  description = "Terraform version constraint for compatibility"
  type        = string
  default     = ">= 1.6.0"
}

# ===================================================================
# 🏷️ PROVIDER CONFIGURATION METADATA
# ===================================================================

locals {
  provider_metadata = {
    terraform_version = terraform.version
    aws_regions = [
      "us-east-1",
      "eu-west-1", 
      "ap-southeast-1"
    ]
    primary_region = "us-east-1"
    total_regions  = 3
    deployment_timestamp = timestamp()
    configuration_checksum = sha256(jsonencode({
      regions = local.provider_metadata.aws_regions
      environment = var.environment
      project = "ai-teddy-bear"
    }))
  }
} 
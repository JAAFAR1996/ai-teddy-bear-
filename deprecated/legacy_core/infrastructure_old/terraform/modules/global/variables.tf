# Global Infrastructure Module Variables

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "global_tags" {
  description = "Global tags to apply to all resources"
  type        = map(string)
}

variable "random_suffix" {
  description = "Random suffix for unique resource naming"
  type        = string
}

variable "domain_name" {
  description = "Primary domain name"
  type        = string
}

variable "hosted_zone_id" {
  description = "Route53 hosted zone ID"
  type        = string
}

variable "enable_global_accelerator" {
  description = "Enable AWS Global Accelerator"
  type        = bool
  default     = true
}

variable "accelerator_config" {
  description = "Global Accelerator configuration"
  type = object({
    enabled               = bool
    flow_logs_enabled     = bool
    flow_logs_s3_bucket   = string
    ip_address_type       = string
    client_affinity       = string
  })
  default = {
    enabled               = true
    flow_logs_enabled     = true
    flow_logs_s3_bucket   = "ai-teddy-global-accelerator-logs"
    ip_address_type       = "IPV4"
    client_affinity       = "SOURCE_IP"
  }
}

variable "enable_cloudfront" {
  description = "Enable CloudFront CDN"
  type        = bool
  default     = true
}

variable "cloudfront_config" {
  description = "CloudFront configuration"
  type = object({
    price_class                = string
    minimum_protocol_version   = string
    ssl_support_method         = string
    compress                   = bool
    viewer_protocol_policy     = string
    allowed_methods           = list(string)
    cached_methods            = list(string)
  })
}

variable "enable_global_tables" {
  description = "Enable DynamoDB Global Tables"
  type        = bool
  default     = true
}

variable "global_tables" {
  description = "DynamoDB Global Tables configuration"
  type = map(object({
    name               = string
    billing_mode       = string
    hash_key          = string
    range_key         = optional(string)
    deletion_protection = bool
    point_in_time_recovery = bool
    server_side_encryption = bool
    stream_enabled     = bool
    stream_view_type   = string
    ttl_enabled        = optional(bool)
    ttl_attribute_name = optional(string)
    attributes = list(object({
      name = string
      type = string
    }))
    global_secondary_indexes = list(object({
      name               = string
      hash_key          = string
      range_key         = optional(string)
      projection_type   = string
      non_key_attributes = optional(list(string))
    }))
  }))
  default = {}
}

variable "enable_waf" {
  description = "Enable AWS WAF"
  type        = bool
  default     = true
}

variable "waf_config" {
  description = "WAF configuration"
  type = object({
    name = string
    rules = list(object({
      name     = string
      priority = number
      vendor   = string
    }))
  })
}

variable "enable_acm" {
  description = "Enable AWS Certificate Manager"
  type        = bool
  default     = true
}

variable "certificates" {
  description = "ACM certificates configuration"
  type = object({
    primary = object({
      domain_name               = string
      subject_alternative_names = list(string)
      validation_method         = string
    })
  })
}

variable "regional_endpoints" {
  description = "Regional endpoint configurations"
  type = map(object({
    region           = string
    fqdn            = string
    alb_dns_name    = string
    alb_zone_id     = string
    alb_arn         = string
    continent       = optional(string)
    country         = optional(string)
    subdivision     = optional(string)
    traffic_percentage = number
    weight          = number
    shield_region   = string
  }))
  default = {}
}

variable "enable_global_monitoring" {
  description = "Enable global monitoring features"
  type        = bool
  default     = true
} 
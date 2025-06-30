# ===================================================================
# 🌍 AI Teddy Bear - Global Infrastructure Module
# Enterprise-Grade Global Services for Multi-Region Deployment
# Infrastructure Team Lead: Senior Infrastructure Engineer
# Date: January 2025
# ===================================================================

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.30"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

# ===================================================================
# 🌐 ROUTE53 DNS CONFIGURATION
# ===================================================================

# Primary hosted zone for the domain
resource "aws_route53_zone" "primary" {
  count = var.hosted_zone_id == "" ? 1 : 0
  
  name              = var.domain_name
  comment           = "AI Teddy Bear - Primary DNS Zone"
  delegation_set_id = aws_route53_delegation_set.primary[0].id
  
  tags = merge(var.global_tags, {
    Name        = "ai-teddy-primary-zone"
    Type        = "primary-dns-zone"
    Service     = "route53"
    GlobalScope = "true"
  })
}

# Reusable delegation set for DNS
resource "aws_route53_delegation_set" "primary" {
  count = var.hosted_zone_id == "" ? 1 : 0
  
  reference_name = "ai-teddy-delegation-set"
}

# Health checks for each region
resource "aws_route53_health_check" "regional_health_checks" {
  for_each = var.regional_endpoints
  
  fqdn                            = each.value.fqdn
  port                           = 443
  type                           = "HTTPS"
  resource_path                  = "/health"
  failure_threshold              = 3
  request_interval               = 30
  measure_latency                = true
  invert_healthcheck             = false
  disabled                       = false
  enable_sni                     = true
  
  tags = merge(var.global_tags, {
    Name        = "ai-teddy-health-check-${each.key}"
    Type        = "health-check"
    Region      = each.key
    Service     = "route53-health-check"
    GlobalScope = "true"
  })
}

# Geo-routing records for optimal latency
resource "aws_route53_record" "geo_routing" {
  for_each = var.regional_endpoints
  
  zone_id = var.hosted_zone_id != "" ? var.hosted_zone_id : aws_route53_zone.primary[0].zone_id
  name    = "api.${var.domain_name}"
  type    = "A"
  
  geolocation_routing_policy {
    continent   = each.value.continent
    country     = each.value.country
    subdivision = each.value.subdivision
  }
  
  alias {
    name                   = each.value.alb_dns_name
    zone_id                = each.value.alb_zone_id
    evaluate_target_health = true
  }
  
  health_check_id = aws_route53_health_check.regional_health_checks[each.key].id
  set_identifier  = "geo-${each.key}"
}

# Failover record for primary region
resource "aws_route53_record" "failover_primary" {
  zone_id = var.hosted_zone_id != "" ? var.hosted_zone_id : aws_route53_zone.primary[0].zone_id
  name    = "api.${var.domain_name}"
  type    = "A"
  
  failover_routing_policy {
    type = "PRIMARY"
  }
  
  alias {
    name                   = var.regional_endpoints["primary"].alb_dns_name
    zone_id                = var.regional_endpoints["primary"].alb_zone_id
    evaluate_target_health = true
  }
  
  health_check_id = aws_route53_health_check.regional_health_checks["primary"].id
  set_identifier  = "failover-primary"
}

# ===================================================================
# 🚀 AWS GLOBAL ACCELERATOR
# ===================================================================

resource "aws_globalaccelerator_accelerator" "main" {
  count = var.enable_global_accelerator ? 1 : 0
  
  name            = "ai-teddy-global-accelerator"
  ip_address_type = var.accelerator_config.ip_address_type
  enabled         = var.accelerator_config.enabled
  
  attributes {
    flow_logs_enabled   = var.accelerator_config.flow_logs_enabled
    flow_logs_s3_bucket = aws_s3_bucket.global_accelerator_logs[0].bucket
    flow_logs_s3_prefix = "flow-logs/"
  }
  
  tags = merge(var.global_tags, {
    Name        = "ai-teddy-global-accelerator"
    Type        = "global-accelerator"
    Service     = "global-accelerator"
    GlobalScope = "true"
  })
}

# Global Accelerator listener
resource "aws_globalaccelerator_listener" "main" {
  count = var.enable_global_accelerator ? 1 : 0
  
  accelerator_arn = aws_globalaccelerator_accelerator.main[0].id
  client_affinity = var.accelerator_config.client_affinity
  protocol        = "TCP"
  
  port_range {
    from = 80
    to   = 80
  }
  
  port_range {
    from = 443
    to   = 443
  }
}

# Global Accelerator endpoint groups for each region
resource "aws_globalaccelerator_endpoint_group" "regional" {
  for_each = var.enable_global_accelerator ? var.regional_endpoints : {}
  
  listener_arn = aws_globalaccelerator_listener.main[0].id
  endpoint_group_region = each.value.region
  traffic_dial_percentage = each.value.traffic_percentage
  health_check_grace_period_seconds = 30
  
  endpoint_configuration {
    endpoint_id = each.value.alb_arn
    weight      = each.value.weight
  }
  
  health_check_path                = "/health"
  health_check_interval_seconds    = 30
  healthy_threshold_count          = 3
  unhealthy_threshold_count        = 3
  health_check_protocol            = "HTTPS"
  health_check_port                = 443
}

# S3 bucket for Global Accelerator flow logs
resource "aws_s3_bucket" "global_accelerator_logs" {
  count = var.enable_global_accelerator ? 1 : 0
  
  bucket        = "ai-teddy-global-accelerator-logs-${var.random_suffix}"
  force_destroy = false
  
  tags = merge(var.global_tags, {
    Name        = "ai-teddy-global-accelerator-logs"
    Type        = "logs-bucket"
    Service     = "s3"
    Purpose     = "global-accelerator-logs"
    GlobalScope = "true"
  })
}

# ===================================================================
# 🌐 CLOUDFRONT CDN DISTRIBUTION
# ===================================================================

resource "aws_cloudfront_distribution" "main" {
  count = var.enable_cloudfront ? 1 : 0
  
  comment             = "AI Teddy Bear - Global CDN Distribution"
  default_root_object = "index.html"
  enabled             = true
  http_version        = "http2and3"
  is_ipv6_enabled     = true
  price_class         = var.cloudfront_config.price_class
  web_acl_id          = var.enable_waf ? aws_wafv2_web_acl.global[0].arn : null
  
  # Origin configuration for each region
  dynamic "origin" {
    for_each = var.regional_endpoints
    content {
      domain_name = origin.value.alb_dns_name
      origin_id   = "ALB-${origin.key}"
      
      custom_origin_config {
        http_port              = 80
        https_port             = 443
        origin_protocol_policy = "https-only"
        origin_ssl_protocols   = ["TLSv1.2"]
      }
      
      origin_shield {
        enabled              = true
        origin_shield_region = origin.value.shield_region
      }
    }
  }
  
  # Default cache behavior
  default_cache_behavior {
    allowed_methods        = var.cloudfront_config.allowed_methods
    cached_methods         = var.cloudfront_config.cached_methods
    target_origin_id       = "ALB-primary"
    compress               = var.cloudfront_config.compress
    viewer_protocol_policy = var.cloudfront_config.viewer_protocol_policy
    
    forwarded_values {
      query_string = true
      headers      = ["Host", "Authorization", "CloudFront-Forwarded-Proto", "X-Forwarded-For"]
      
      cookies {
        forward = "all"
      }
    }
    
    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
    
    # Response headers policy
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security[0].id
  }
  
  # API cache behavior
  ordered_cache_behavior {
    path_pattern           = "/api/*"
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "ALB-primary"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    
    forwarded_values {
      query_string = true
      headers      = ["*"]
      
      cookies {
        forward = "all"
      }
    }
    
    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0
  }
  
  # Geographic restrictions
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  # SSL/TLS configuration
  viewer_certificate {
    acm_certificate_arn            = var.enable_acm ? aws_acm_certificate.primary[0].arn : null
    ssl_support_method             = var.cloudfront_config.ssl_support_method
    minimum_protocol_version       = var.cloudfront_config.minimum_protocol_version
    cloudfront_default_certificate = var.enable_acm ? false : true
  }
  
  # Logging configuration
  logging_config {
    bucket          = aws_s3_bucket.cloudfront_logs[0].bucket_domain_name
    include_cookies = false
    prefix          = "cloudfront-logs/"
  }
  
  tags = merge(var.global_tags, {
    Name        = "ai-teddy-cloudfront"
    Type        = "cloudfront-distribution"
    Service     = "cloudfront"
    GlobalScope = "true"
  })
}

# CloudFront response headers policy for security
resource "aws_cloudfront_response_headers_policy" "security" {
  count = var.enable_cloudfront ? 1 : 0
  
  name    = "ai-teddy-security-headers"
  comment = "Security headers for AI Teddy Bear application"
  
  security_headers_config {
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      preload                   = true
    }
    
    content_type_options {
      override = true
    }
    
    frame_options {
      frame_option = "DENY"
    }
    
    referrer_policy {
      referrer_policy = "strict-origin-when-cross-origin"
    }
  }
  
  custom_headers_config {
    items {
      header   = "X-Content-Security-Policy"
      value    = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
      override = true
    }
  }
}

# S3 bucket for CloudFront logs
resource "aws_s3_bucket" "cloudfront_logs" {
  count = var.enable_cloudfront ? 1 : 0
  
  bucket        = "ai-teddy-cloudfront-logs-${var.random_suffix}"
  force_destroy = false
  
  tags = merge(var.global_tags, {
    Name        = "ai-teddy-cloudfront-logs"
    Type        = "logs-bucket"
    Service     = "s3"
    Purpose     = "cloudfront-logs"
    GlobalScope = "true"
  })
}

# ===================================================================
# 🗄️ DYNAMODB GLOBAL TABLES
# ===================================================================

# Create DynamoDB tables with global tables enabled
resource "aws_dynamodb_table" "global_tables" {
  for_each = var.enable_global_tables ? var.global_tables : {}
  
  name                        = each.value.name
  billing_mode               = each.value.billing_mode
  hash_key                   = each.value.hash_key
  range_key                  = each.value.range_key
  deletion_protection_enabled = each.value.deletion_protection
  stream_enabled             = each.value.stream_enabled
  stream_view_type           = each.value.stream_view_type
  
  # Attributes definition
  dynamic "attribute" {
    for_each = each.value.attributes
    content {
      name = attribute.value.name
      type = attribute.value.type
    }
  }
  
  # Global Secondary Indexes
  dynamic "global_secondary_index" {
    for_each = each.value.global_secondary_indexes
    content {
      name            = global_secondary_index.value.name
      hash_key        = global_secondary_index.value.hash_key
      range_key       = global_secondary_index.value.range_key
      projection_type = global_secondary_index.value.projection_type
      
      non_key_attributes = lookup(global_secondary_index.value, "non_key_attributes", null)
    }
  }
  
  # Point-in-time recovery
  point_in_time_recovery {
    enabled = each.value.point_in_time_recovery
  }
  
  # Server-side encryption
  server_side_encryption {
    enabled     = each.value.server_side_encryption
    kms_key_arn = aws_kms_key.dynamodb[0].arn
  }
  
  # TTL configuration
  dynamic "ttl" {
    for_each = each.value.ttl_enabled ? [1] : []
    content {
      attribute_name = each.value.ttl_attribute_name
      enabled        = true
    }
  }
  
  tags = merge(var.global_tags, {
    Name        = each.value.name
    Type        = "dynamodb-global-table"
    Service     = "dynamodb"
    GlobalScope = "true"
    Purpose     = each.key
  })
  
  replica {
    region_name = "us-east-1"
    point_in_time_recovery = each.value.point_in_time_recovery
  }
  
  replica {
    region_name = "eu-west-1"
    point_in_time_recovery = each.value.point_in_time_recovery
  }
  
  replica {
    region_name = "ap-southeast-1"
    point_in_time_recovery = each.value.point_in_time_recovery
  }
}

# KMS key for DynamoDB encryption
resource "aws_kms_key" "dynamodb" {
  count = var.enable_global_tables ? 1 : 0
  
  description             = "KMS key for DynamoDB Global Tables encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  
  tags = merge(var.global_tags, {
    Name        = "ai-teddy-dynamodb-key"
    Type        = "kms-key"
    Service     = "kms"
    Purpose     = "dynamodb-encryption"
    GlobalScope = "true"
  })
}

# KMS key alias
resource "aws_kms_alias" "dynamodb" {
  count = var.enable_global_tables ? 1 : 0
  
  name          = "alias/ai-teddy-dynamodb"
  target_key_id = aws_kms_key.dynamodb[0].key_id
}

# ===================================================================
# 🛡️ AWS WAF GLOBAL CONFIGURATION
# ===================================================================

resource "aws_wafv2_web_acl" "global" {
  count = var.enable_waf ? 1 : 0
  
  name        = var.waf_config.name
  description = "WAF for AI Teddy Bear global protection"
  scope       = "CLOUDFRONT"
  
  default_action {
    allow {}
  }
  
  # AWS Managed Rule Sets
  dynamic "rule" {
    for_each = var.waf_config.rules
    content {
      name     = rule.value.name
      priority = rule.value.priority
      
      override_action {
        none {}
      }
      
      statement {
        managed_rule_group_statement {
          name        = rule.value.name
          vendor_name = rule.value.vendor
        }
      }
      
      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = rule.value.name
        sampled_requests_enabled   = true
      }
    }
  }
  
  # Rate limiting rule
  rule {
    name     = "RateLimitRule"
    priority = 100
    
    action {
      block {}
    }
    
    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }
  
  # Child safety custom rule
  rule {
    name     = "ChildSafetyRule"
    priority = 10
    
    action {
      block {}
    }
    
    statement {
      byte_match_statement {
        search_string = "unsafe_content"
        field_to_match {
          body {}
        }
        text_transformation {
          priority = 0
          type     = "LOWERCASE"
        }
        positional_constraint = "CONTAINS"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "ChildSafetyRule"
      sampled_requests_enabled   = true
    }
  }
  
  tags = merge(var.global_tags, {
    Name        = var.waf_config.name
    Type        = "waf-web-acl"
    Service     = "waf"
    GlobalScope = "true"
    Purpose     = "global-protection"
  })
  
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "ai-teddy-waf"
    sampled_requests_enabled   = true
  }
}

# ===================================================================
# 🔐 ACM CERTIFICATES
# ===================================================================

resource "aws_acm_certificate" "primary" {
  count = var.enable_acm ? 1 : 0
  
  domain_name               = var.certificates.primary.domain_name
  subject_alternative_names = var.certificates.primary.subject_alternative_names
  validation_method         = var.certificates.primary.validation_method
  
  lifecycle {
    create_before_destroy = true
  }
  
  tags = merge(var.global_tags, {
    Name        = "ai-teddy-primary-certificate"
    Type        = "acm-certificate"
    Service     = "acm"
    Domain      = var.certificates.primary.domain_name
    GlobalScope = "true"
  })
}

# Certificate validation
resource "aws_acm_certificate_validation" "primary" {
  count = var.enable_acm ? 1 : 0
  
  certificate_arn         = aws_acm_certificate.primary[0].arn
  validation_record_fqdns = [for record in aws_route53_record.certificate_validation : record.fqdn]
  
  timeouts {
    create = "5m"
  }
}

# Route53 records for certificate validation
resource "aws_route53_record" "certificate_validation" {
  for_each = var.enable_acm ? {
    for dvo in aws_acm_certificate.primary[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}
  
  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = var.hosted_zone_id != "" ? var.hosted_zone_id : aws_route53_zone.primary[0].zone_id
} 
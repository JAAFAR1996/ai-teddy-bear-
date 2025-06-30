# Global Infrastructure Module Outputs

output "route53_zone_id" {
  description = "Route53 hosted zone ID"
  value       = var.hosted_zone_id != "" ? var.hosted_zone_id : aws_route53_zone.primary[0].zone_id
}

output "route53_zone_name" {
  description = "Route53 hosted zone name"
  value       = var.domain_name
}

output "route53_name_servers" {
  description = "Route53 name servers"
  value       = var.hosted_zone_id != "" ? [] : aws_route53_zone.primary[0].name_servers
}

output "global_accelerator_arn" {
  description = "Global Accelerator ARN"
  value       = var.enable_global_accelerator ? aws_globalaccelerator_accelerator.main[0].id : null
}

output "global_accelerator_dns_name" {
  description = "Global Accelerator DNS name"
  value       = var.enable_global_accelerator ? aws_globalaccelerator_accelerator.main[0].dns_name : null
}

output "global_accelerator_hosted_zone_id" {
  description = "Global Accelerator hosted zone ID"
  value       = var.enable_global_accelerator ? aws_globalaccelerator_accelerator.main[0].hosted_zone_id : null
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].id : null
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].domain_name : null
}

output "cloudfront_hosted_zone_id" {
  description = "CloudFront distribution hosted zone ID"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].hosted_zone_id : null
}

output "cloudfront_distribution_arn" {
  description = "CloudFront distribution ARN"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].arn : null
}

output "waf_arn" {
  description = "WAF Web ACL ARN"
  value       = var.enable_waf ? aws_wafv2_web_acl.global[0].arn : null
}

output "waf_id" {
  description = "WAF Web ACL ID"
  value       = var.enable_waf ? aws_wafv2_web_acl.global[0].id : null
}

output "certificates" {
  description = "ACM certificate ARNs"
  value = var.enable_acm ? {
    primary = aws_acm_certificate.primary[0].arn
  } : {}
}

output "certificate_validation_arns" {
  description = "ACM certificate validation ARNs"
  value = var.enable_acm ? {
    primary = aws_acm_certificate_validation.primary[0].certificate_arn
  } : {}
}

output "dynamodb_global_tables" {
  description = "DynamoDB Global Tables information"
  value = var.enable_global_tables ? {
    for table_name, table in aws_dynamodb_table.global_tables : table_name => {
      name       = table.name
      arn        = table.arn
      stream_arn = table.stream_arn
    }
  } : {}
}

output "kms_key_arn" {
  description = "KMS key ARN for DynamoDB encryption"
  value       = var.enable_global_tables ? aws_kms_key.dynamodb[0].arn : null
}

output "kms_key_id" {
  description = "KMS key ID for DynamoDB encryption"
  value       = var.enable_global_tables ? aws_kms_key.dynamodb[0].key_id : null
}

output "kms_alias_arn" {
  description = "KMS key alias ARN"
  value       = var.enable_global_tables ? aws_kms_alias.dynamodb[0].arn : null
}

output "s3_bucket_names" {
  description = "S3 bucket names for logging"
  value = {
    global_accelerator_logs = var.enable_global_accelerator ? aws_s3_bucket.global_accelerator_logs[0].bucket : null
    cloudfront_logs        = var.enable_cloudfront ? aws_s3_bucket.cloudfront_logs[0].bucket : null
  }
}

output "health_check_ids" {
  description = "Route53 health check IDs"
  value = {
    for region, check in aws_route53_health_check.regional_health_checks : region => check.id
  }
}

output "global_infrastructure_summary" {
  description = "Summary of global infrastructure components"
  value = {
    dns = {
      enabled    = true
      zone_id    = var.hosted_zone_id != "" ? var.hosted_zone_id : aws_route53_zone.primary[0].zone_id
      domain     = var.domain_name
    }
    cdn = {
      enabled       = var.enable_cloudfront
      distribution_id = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].id : null
      domain_name   = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].domain_name : null
    }
    accelerator = {
      enabled   = var.enable_global_accelerator
      dns_name  = var.enable_global_accelerator ? aws_globalaccelerator_accelerator.main[0].dns_name : null
    }
    waf = {
      enabled = var.enable_waf
      arn     = var.enable_waf ? aws_wafv2_web_acl.global[0].arn : null
    }
    ssl = {
      enabled      = var.enable_acm
      certificate_arn = var.enable_acm ? aws_acm_certificate.primary[0].arn : null
    }
    database = {
      global_tables_enabled = var.enable_global_tables
      table_count          = var.enable_global_tables ? length(aws_dynamodb_table.global_tables) : 0
      kms_encryption       = var.enable_global_tables
    }
  }
} 
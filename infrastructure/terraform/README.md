# 🌍 AI Teddy Bear - Multi-Region Infrastructure

## Enterprise-Grade Multi-Region Deployment with Terraform

This Terraform configuration deploys a comprehensive multi-region infrastructure for the AI Teddy Bear application across three AWS regions with global services for optimal performance, reliability, and child safety compliance.

## 🏗️ Architecture Overview

### Global Services
- **AWS Global Accelerator** - Low latency global access
- **CloudFront CDN** - Content delivery optimization
- **Route53** - DNS with geo-routing and health checks
- **DynamoDB Global Tables** - Multi-region data replication
- **AWS WAF** - Global application protection
- **ACM Certificates** - SSL/TLS certificate management

### Regional Infrastructure
Each region (us-east-1, eu-west-1, ap-southeast-1) includes:
- **VPC** with public, private, and database subnets
- **EKS Cluster** with multiple node groups (general, AI processing, memory optimized)
- **RDS PostgreSQL** with multi-AZ deployment
- **ElastiCache Redis** for caching and session management
- **Application Load Balancer** for traffic distribution
- **S3 Buckets** for audio recordings, logs, and backups
- **KMS Keys** for encryption at rest
- **Comprehensive IAM roles** with IRSA support

## 📋 Prerequisites

### Required Tools
- **Terraform** >= 1.6.0
- **AWS CLI** >= 2.0
- **kubectl** >= 1.24
- **Helm** >= 3.8

### AWS Account Setup
1. AWS Account with appropriate permissions
2. AWS CLI configured with credentials
3. Route53 hosted zone (optional - can be created)
4. EC2 Key Pair for node access

### Required Permissions
The deployment requires extensive AWS permissions including:
- EC2, VPC, EKS, RDS, ElastiCache
- Route53, CloudFront, Global Accelerator
- DynamoDB, S3, KMS, IAM
- CloudWatch, WAF, ACM

## 🚀 Quick Start

### 1. Clone and Setup
```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
```

### 2. Configure Variables
Edit `terraform.tfvars` with your specific values:
```hcl
domain_name = "your-domain.com"
ec2_key_name = "your-key-pair"
```

### 3. Initialize Terraform
```bash
terraform init
```

### 4. Plan Deployment
```bash
terraform plan
```

### 5. Deploy Infrastructure
```bash
terraform apply
```

## 📁 Project Structure

```
infrastructure/terraform/
├── main.tf                    # Main configuration
├── variables.tf              # Variable definitions
├── providers.tf              # Provider configurations
├── terraform.tfvars.example  # Example variables
├── modules/
│   ├── global/               # Global infrastructure
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── regional/             # Regional infrastructure
│       ├── main.tf
│       ├── variables.tf
│       ├── iam.tf
│       └── outputs.tf
└── README.md                 # This file
```

## 🌐 Global Infrastructure

### DNS and Traffic Management
- **Route53** hosted zone with delegation set
- **Geo-routing** policies for optimal latency
- **Health checks** for each regional endpoint
- **Failover** configuration for high availability

### Content Delivery
- **CloudFront** distribution with multiple origins
- **Origin Shield** for improved cache hit ratio
- **Security headers** policy for enhanced protection
- **Access logging** to S3 buckets

### Global Accelerator
- **Anycast** IP addresses for consistent entry points
- **Traffic dial** controls for gradual traffic shifting
- **Health checks** and automatic failover
- **Flow logs** for network analysis

### Global Data Storage
- **DynamoDB Global Tables** for:
  - Children profiles and settings
  - Conversation history with TTL
  - Safety events and alerts
- **Cross-region replication** with eventual consistency
- **Point-in-time recovery** enabled

## 🏗️ Regional Infrastructure

### Networking
- **Multi-AZ VPC** with three subnet types
- **NAT Gateways** for high availability
- **Internet Gateway** for public access
- **Route tables** with appropriate routing

### Container Orchestration
- **EKS Cluster** with latest Kubernetes version
- **Multiple node groups**:
  - General purpose nodes (t3.large/xlarge)
  - AI processing nodes with GPU (g4dn.xlarge/2xlarge)
  - Memory optimized nodes (r5.large/xlarge)
- **Auto Scaling** based on demand
- **Spot instances** for cost optimization

### Data Storage
- **RDS PostgreSQL** with:
  - Multi-AZ deployment for HA
  - Performance Insights enabled
  - Automated backups (35 days retention)
  - Enhanced monitoring
- **ElastiCache Redis** with:
  - Cluster mode for scalability
  - At-rest and in-transit encryption
  - Automated failover

### Load Balancing
- **Application Load Balancer** with:
  - SSL termination
  - Target group routing
  - Health checks
  - Access logging to S3

## 🔐 Security Features

### Encryption
- **KMS keys** for all encryption needs
- **EKS secrets encryption** at cluster level
- **S3 server-side encryption** with KMS
- **RDS encryption** at rest
- **ElastiCache encryption** at rest and in transit

### Network Security
- **Security Groups** with minimal required access
- **NACLs** for additional network protection
- **Private subnets** for sensitive resources
- **VPC Flow Logs** for network monitoring

### Identity and Access Management
- **Service Account roles** (IRSA) for workloads
- **Least privilege** IAM policies
- **Cross-account roles** support
- **MFA requirements** for sensitive operations

### Application Protection
- **AWS WAF** with managed rule sets
- **Rate limiting** to prevent abuse
- **Custom rules** for child safety
- **DDoS protection** via AWS Shield

## 📊 Monitoring and Observability

### CloudWatch
- **Log groups** for all services
- **Custom metrics** for business KPIs
- **Alarms** for critical thresholds
- **Dashboards** for operational visibility

### Distributed Tracing
- **AWS X-Ray** integration
- **Sampling configuration** for cost optimization
- **Service maps** for dependency visualization

### Infrastructure Monitoring
- **VPC Flow Logs** for network analysis
- **CloudTrail** for API audit logging
- **Config** for compliance monitoring
- **GuardDuty** for threat detection

## 💰 Cost Optimization

### Resource Optimization
- **Spot instances** for non-critical workloads
- **Scheduled scaling** for predictable patterns
- **Reserved instances** recommendations
- **Right-sizing** based on utilization

### Budget Controls
- **AWS Budgets** with alerts
- **Cost allocation tags** for tracking
- **Resource lifecycle** management
- **Unused resource** identification

## 🔄 Disaster Recovery

### Backup Strategy
- **Automated RDS backups** (35 days retention)
- **DynamoDB point-in-time recovery**
- **S3 cross-region replication** for critical data
- **EBS snapshot** policies

### Recovery Procedures
- **Multi-region deployment** for availability
- **Database failover** automation
- **Application-level** health checks
- **Traffic routing** during outages

## 🛠️ Maintenance and Updates

### Terraform State Management
```bash
# Initialize with S3 backend
terraform init -backend-config="bucket=your-state-bucket"

# Plan with specific variable file
terraform plan -var-file="prod.tfvars"

# Apply with auto-approval
terraform apply -auto-approve
```

### Rolling Updates
```bash
# Update EKS cluster version
terraform plan -target=module.regional_infrastructure

# Update node groups
terraform apply -target=module.regional_infrastructure["primary"].aws_eks_node_group
```

### Scaling Operations
```bash
# Scale node groups
terraform apply -var='node_group_scaling={"general":{"desired_size":5}}'

# Update instance types
terraform apply -var='node_group_instance_types={"general":["t3.xlarge"]}'
```

## 🔧 Troubleshooting

### Common Issues

1. **EKS Access Denied**
   ```bash
   aws eks update-kubeconfig --region us-east-1 --name ai-teddy-primary
   ```

2. **RDS Connection Issues**
   - Check security group rules
   - Verify subnet group configuration
   - Confirm VPC routing

3. **DynamoDB Global Tables**
   - Ensure consistent table schemas
   - Check IAM permissions
   - Verify stream settings

### Useful Commands
```bash
# Check EKS cluster status
kubectl get nodes

# View RDS instances
aws rds describe-db-instances

# Check Global Accelerator
aws globalaccelerator list-accelerators

# DynamoDB Global Tables
aws dynamodb list-global-tables
```

## 📚 Additional Resources

- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [COPPA Compliance Guide](https://www.ftc.gov/enforcement/rules/rulemaking-regulatory-reform-proceedings/childrens-online-privacy-protection-rule)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the Infrastructure Team
- Check the troubleshooting guide above

---

**Infrastructure Team Lead: Senior Infrastructure Engineer**  
**Date: January 2025**  
**Version: 1.0.0** 
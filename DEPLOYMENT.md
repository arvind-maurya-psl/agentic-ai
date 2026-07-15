# Deployment Guide

This guide covers deploying the Agentic AI application to various environments.

## Prerequisites

- AWS Account with Bedrock access
- AWS CLI configured with credentials
- GitHub repository with admin access
- Docker and Docker Compose (for local/container deployment)

## AWS Infrastructure Setup

### Step 1: Configure AWS Account

1. **Enable Bedrock in your region**
   - Log into AWS Console
   - Navigate to Bedrock > Model Access
   - Request access to Claude, Nova, or Titan models

2. **Run setup script**
   ```bash
   bash infrastructure/setup-aws.sh
   ```

   This will:
   - Create S3 bucket for deployments
   - Create IAM role with necessary permissions
   - Set up OIDC provider for GitHub Actions
   - Create CloudWatch log groups

### Step 2: Configure GitHub Secrets

Add the following secrets to your GitHub repository:

```
AWS_ROLE_ARN=arn:aws:iam::ACCOUNT_ID:role/agentic-ai-role
AWS_REGION=us-east-1
DEPLOYMENT_BUCKET=agentic-ai-deployment-ACCOUNT_ID
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

Navigate to: Repository Settings > Secrets and Variables > Actions

### Step 3: Create GitHub Environments

Create two environments in GitHub (Settings > Environments):

**Staging Environment**
- Deployment branch protection: develop
- Reviewers: (optional)
- Environment secrets: (inherit from repository)

**Production Environment**
- Deployment branch protection: main
- Reviewers: Required (at least 1)
- Environment secrets: Additional prod-specific secrets

## Deployment Strategies

### Strategy 1: GitHub Actions Auto-Deployment

Automatic deployment on push to main/develop branches.

1. **Configure branch protection rules**
   - Require PR reviews
   - Require status checks to pass
   - Dismiss stale PR approvals

2. **Push to branch**
   ```bash
   git push origin main
   ```

3. **Workflow executes automatically**
   - PR validation
   - Docker build
   - Deploy to environment
   - Run health checks

### Strategy 2: Manual Deployment

Trigger deployment manually via workflow dispatch.

1. **Go to Actions tab**
2. **Select Deploy workflow**
3. **Click "Run workflow"**
4. **Select environment and branch**
5. **Monitor deployment progress**

### Strategy 3: Scheduled Deployment

Deploy automatically on schedule.

Update `.github/workflows/deploy.yml`:

```yaml
on:
  schedule:
    - cron: '0 2 * * MON'  # Every Monday at 2 AM

jobs:
  deploy:
    # ... existing configuration
```

## Deployment to Different Platforms

### AWS Lambda

1. **Update IAM role**
   - Add Lambda execution permissions
   - Add Bedrock invoke permissions

2. **Configure Lambda function**
   ```bash
   aws lambda create-function \
     --function-name agentic-ai \
     --runtime python3.12 \
     --handler app.lambda_handler \
     --zip-file fileb://deployment.zip \
     --role arn:aws:iam::ACCOUNT_ID:role/agentic-ai-role \
     --timeout 900 \
     --memory-size 1024 \
     --environment Variables={ENVIRONMENT=production}
   ```

3. **Set up API Gateway** (optional)
   ```bash
   aws apigateway create-rest-api \
     --name agentic-ai-api \
     --description "Agentic AI API"
   ```

### AWS EC2

1. **Launch EC2 instance**
   ```bash
   aws ec2 run-instances \
     --image-id ami-0c55b159cbfafe1f0 \
     --instance-type t3.medium \
     --iam-instance-profile Name=agentic-ai-role \
     --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=agentic-ai}]'
   ```

2. **SSH into instance and deploy**
   ```bash
   ssh ec2-user@instance-ip
   git clone https://github.com/org/agentic-ai.git
   cd agentic-ai
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m agentic_ai.app
   ```

### AWS ECS/Fargate

1. **Create ECR repository**
   ```bash
   aws ecr create-repository --repository-name agentic-ai
   ```

2. **Push Docker image**
   ```bash
   docker tag agentic-ai:latest ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/agentic-ai:latest
   docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/agentic-ai:latest
   ```

3. **Create ECS task definition** (create `ecs-task-def.json`)
   ```json
   {
     "family": "agentic-ai",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "containerDefinitions": [
       {
         "name": "agentic-ai",
         "image": "ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/agentic-ai:latest",
         "environment": [
           {"name": "ENVIRONMENT", "value": "production"}
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/agentic-ai",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

4. **Register task definition**
   ```bash
   aws ecs register-task-definition --cli-input-json file://ecs-task-def.json
   ```

### Docker Local/On-Premise

1. **Build Docker image**
   ```bash
   docker build -t agentic-ai:1.0.0 .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. **Monitor container**
   ```bash
   docker logs -f agentic-ai-app
   docker stats agentic-ai-app
   ```

## Post-Deployment

### Verification Checklist

- [ ] Application is running without errors
- [ ] Health check endpoint responds
- [ ] Can invoke agent tasks
- [ ] Logs are being collected
- [ ] CloudWatch alarms are configured
- [ ] Database connections (if applicable) are working

### Health Check

```bash
# Container health check
curl http://localhost:8000/health

# AWS Lambda
aws lambda invoke \
  --function-name agentic-ai \
  --payload '{"action":"health"}' \
  response.json

cat response.json
```

### Monitoring Setup

1. **CloudWatch Dashboard**
   ```bash
   aws cloudwatch put-dashboard \
     --dashboard-name agentic-ai \
     --dashboard-body file://dashboard-config.json
   ```

2. **Set up alarms**
   ```bash
   aws cloudwatch put-metric-alarm \
     --alarm-name agentic-ai-errors \
     --alarm-description "Alert on high error rate" \
     --metric-name Errors \
     --namespace AWS/Lambda \
     --statistic Sum \
     --period 300 \
     --threshold 10 \
     --comparison-operator GreaterThanThreshold
   ```

## Rollback Procedures

### Rollback from GitHub

```bash
# Revert to previous version
git revert <commit-sha>
git push origin main

# Or reset to specific tag
git reset --hard v1.0.0
git push -f origin main
```

### Rollback Lambda

```bash
# Update to previous version alias
aws lambda update-alias \
  --function-name agentic-ai \
  --name prod \
  --function-version 5

# Or rollback to previous deployment
aws lambda get-alias --function-name agentic-ai --name prod
```

### Rollback Docker

```bash
# Pull previous image version
docker pull REGISTRY/agentic-ai:v1.0.0

# Update service
docker service update \
  --image REGISTRY/agentic-ai:v1.0.0 \
  agentic-ai-service
```

## Troubleshooting Deployments

### Issue: Deployment fails with authentication error

```
Solution:
1. Verify AWS_ROLE_ARN is correct
2. Check OIDC provider is configured
3. Ensure role trust policy includes GitHub repository
```

### Issue: Lambda timeout

```
Solution:
1. Increase timeout in Lambda configuration (max 900 seconds)
2. Optimize agent execution time
3. Use streaming responses for long-running tasks
```

### Issue: High memory usage

```
Solution:
1. Reduce AGENT_MAX_ITERATIONS
2. Clear memory more frequently
3. Increase container/Lambda memory allocation
```

### Issue: Model not responding

```
Solution:
1. Verify Bedrock model access
2. Check AWS region configuration
3. Check rate limits (Bedrock has provisioned throughput)
4. Review CloudWatch logs for detailed errors
```

## Performance Tuning

### Optimization Tips

1. **Reduce agent iterations**
   ```
   AGENT_MAX_ITERATIONS=5
   ```

2. **Enable streaming for large responses**
   ```python
   response = bedrock_service.invoke_model_streaming(...)
   ```

3. **Use Redis for memory in production**
   ```
   AGENT_MEMORY_TYPE=redis
   REDIS_HOST=your-redis-endpoint
   ```

4. **Increase concurrency**
   ```
   API_WORKERS=8
   ```

## Cost Optimization

### Bedrock Costs

- **On-Demand**: Pay per token (higher cost)
- **Provisioned Throughput**: Fixed cost for consistent workloads (recommended for production)

### AWS Infrastructure

- Use EC2 spot instances for non-critical workloads
- Use Lambda for sporadic usage
- Use ECS/Fargate for consistent workloads
- Enable auto-scaling based on load

## Security Hardening

1. **Enable VPC endpoints** for AWS services
2. **Use private subnets** for containers/lambdas
3. **Enable encryption** for data in transit and at rest
4. **Implement network ACLs** and security groups
5. **Enable CloudTrail** for audit logging
6. **Rotate credentials** regularly
7. **Keep dependencies updated** (automated via Renovate/Dependabot)

## Next Steps

1. Set up monitoring dashboards
2. Configure alerting and notifications
3. Create runbooks for common operations
4. Document disaster recovery procedures
5. Conduct security audit
6. Set up automated backups (if applicable)

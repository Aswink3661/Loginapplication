# End-to-End Implementation Document
## Loginapp — EC2-Only Deployment with Todo Application

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Prerequisites](#3-prerequisites)
4. [Architecture](#4-architecture)
5. [Terraform Infrastructure](#5-terraform-infrastructure)
   - 5.1 [Module: ec2](#51-module-ec2)
   - 5.2 [Environment: dev-ec2](#52-environment-dev-ec2)
   - 5.3 [Environments: qa-ec2 and prod-ec2](#53-environments-qa-ec2-and-prod-ec2)
6. [AWS Resources Created](#6-aws-resources-created)
7. [Step-by-Step Deployment Guide](#7-step-by-step-deployment-guide)
   - 7.1 [Discover Existing AWS Resources](#71-discover-existing-aws-resources)
   - 7.2 [Terraform Init, Plan, Apply](#72-terraform-init-plan-apply)
   - 7.3 [Attach SSH Key Pair](#73-attach-ssh-key-pair)
   - 7.4 [Deploy Backend (FastAPI)](#74-deploy-backend-fastapi)
   - 7.5 [Deploy Frontend (React)](#75-deploy-frontend-react)
   - 7.6 [Configure nginx](#76-configure-nginx)
8. [Application Stack](#8-application-stack)
9. [Networking and Security](#9-networking-and-security)
10. [Access URLs](#10-access-urls)
11. [Operational Commands](#11-operational-commands)
12. [Troubleshooting](#12-troubleshooting)
13. [Lessons Learned](#13-lessons-learned)

---

## 1. Project Overview

This project provisions an EC2 instance on AWS using Terraform and deploys a full-stack Todo application on it. The backend is a FastAPI (Python) REST API and the frontend is a React + TypeScript SPA built with Vite. nginx acts as the reverse proxy, serving the frontend on port 80 and forwarding `/api/*` calls to the FastAPI backend on port 8000.

**Environments provisioned:** `dev-ec2`, `qa-ec2`, `prod-ec2`

---

## 2. Repository Structure

```
Loginapplication/
├── infra/
│   ├── modules/
│   │   └── ec2/
│   │       ├── main.tf          # IAM Role, Instance Profile, Launch Template
│   │       ├── variables.tf
│   │       └── outputs.tf
│   └── envs/
│       ├── dev-ec2/             # Dev environment (EC2-only)
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   ├── terraform.tfvars
│       │   ├── outputs.tf
│       │   └── provider.tf
│       ├── qa-ec2/              # QA environment (EC2-only)
│       └── prod-ec2/            # Prod environment (EC2-only)
├── todo-app/                    # FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   └── src/
│       ├── api/routes.py
│       ├── config/settings.py
│       ├── models/todo.py
│       ├── repositories/
│       ├── services/
│       └── utils/logger.py
└── todo-app-frontend/           # React + Vite frontend
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx
        ├── api/todoApi.ts
        ├── components/
        ├── hooks/useTodos.ts
        └── types/todo.ts
```

---

## 3. Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Terraform | >= 1.5.0 | Infrastructure provisioning |
| AWS CLI | >= 2.x | Resource discovery and SG management |
| SSH client | any | Remote access to EC2 |
| rsync | any | File transfer (excludes node_modules) |
| AWS account | — | IAM permissions: EC2, IAM, S3 |

**AWS CLI configured for:** `ap-south-1` (Mumbai)

---

## 4. Architecture

```
Internet
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  AWS ap-south-1 (Mumbai)                                │
│                                                         │
│  Default VPC  vpc-092b0d10291014ae3  (172.31.0.0/16)   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Public Subnet  subnet-0069d8637a5a7e78e          │   │
│  │  AZ: ap-south-1c                                 │   │
│  │                                                  │   │
│  │  ┌────────────────────────────────────────────┐  │   │
│  │  │  EC2  i-079c4f67264c22291                   │  │   │
│  │  │  t3.micro  |  Amazon Linux 2023             │  │   │
│  │  │  Public IP: 65.0.69.91                      │  │   │
│  │  │  Key Pair:  Pem_key                         │  │   │
│  │  │                                             │  │   │
│  │  │  ┌─────────────┐    ┌─────────────────────┐ │  │   │
│  │  │  │ nginx :80   │───▶│  FastAPI :8000       │ │  │   │
│  │  │  │ React SPA   │    │  uvicorn + systemd   │ │  │   │
│  │  │  └─────────────┘    └─────────────────────┘ │  │   │
│  │  └────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Request Flow

```
Browser
  │
  ├─ GET /          → nginx → serves /var/www/todo-app/index.html (React)
  ├─ GET /assets/*  → nginx → serves JS/CSS bundles (static)
  └─ ANY /api/*     → nginx → reverse proxy → FastAPI 127.0.0.1:8000
                                                   │
                                            in-memory CRUD
```

---

## 5. Terraform Infrastructure

### 5.1 Module: ec2

**Path:** `infra/modules/ec2/`

This module creates three AWS resources:

#### a) IAM Role (`aws_iam_role`)
Allows the EC2 instance to assume an AWS role.
```hcl
resource "aws_iam_role" "ec2" {
  name = "${var.project_name}-${var.environment}-ec2-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}
```

#### b) IAM Role Policy Attachment
Attaches `AmazonSSMManagedInstanceCore` so the instance is reachable via AWS Systems Manager (no SSH required as fallback).
```hcl
resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
```

#### c) IAM Instance Profile (`aws_iam_instance_profile`)
Binds the IAM role to the EC2 instance.

#### d) Launch Template (`aws_launch_template`)
A blueprint for EC2 instances containing:
- AMI ID, instance type, key pair
- Security group
- Encrypted gp3 EBS root volume (20 GiB)
- IAM instance profile
- Detailed monitoring enabled
- User data script (bootstraps httpd)

**Module Inputs:**

| Variable | Type | Description |
|----------|------|-------------|
| `project_name` | string | Naming prefix |
| `environment` | string | dev / qa / prod |
| `ami_id` | string | AMI ID |
| `instance_type` | string | EC2 instance type |
| `key_pair_name` | string | SSH key pair name |
| `ec2_sg_id` | string | Security group ID |
| `app_port` | number | Application port |
| `ebs_volume_size` | number | Root volume GiB |

**Module Outputs:** `launch_template_id`, `launch_template_latest_version`, `instance_profile_name`, `iam_role_arn`

---

### 5.2 Environment: dev-ec2

**Path:** `infra/envs/dev-ec2/`

#### provider.tf
```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket  = "loginapp-terraform-stateless"
    key     = "dev-ec2/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}
provider "aws" {
  region = var.aws_region
  default_tags {
    tags = { Project = var.project_name, Environment = var.environment, ManagedBy = "Terraform" }
  }
}
```

#### main.tf
```hcl
# Uses the ec2 module (launch template + IAM)
module "ec2" {
  source          = "../../modules/ec2"
  project_name    = var.project_name
  environment     = var.environment
  ami_id          = var.ami_id
  instance_type   = var.instance_type
  key_pair_name   = var.key_pair_name
  ec2_sg_id       = var.ec2_sg_id
  app_port        = var.app_port
  ebs_volume_size = var.ebs_volume_size
}

# Actual running EC2 instance using the launch template
resource "aws_instance" "this" {
  subnet_id = var.subnet_id
  launch_template {
    id      = module.ec2.launch_template_id
    version = "$Latest"
  }
  tags = {
    Name        = "${var.project_name}-${var.environment}-instance"
    Environment = var.environment
  }
}
```

#### terraform.tfvars (dev)
```hcl
aws_region      = "ap-south-1"
project_name    = "loginapp"
environment     = "dev"
ami_id          = "ami-0e12ffc2dd465f6e4"  # Amazon Linux 2023 – ap-south-1
instance_type   = "t3.micro"
key_pair_name   = "Pem_key"
ebs_volume_size = 20
app_port        = 80
vpc_id          = "vpc-092b0d10291014ae3"
ec2_sg_id       = "sg-07ef0129690a48376"
subnet_id       = "subnet-0069d8637a5a7e78e"
```

---

### 5.3 Environments: qa-ec2 and prod-ec2

Same structure as dev-ec2. Key differences:

| Setting | dev | qa | prod |
|---------|-----|----|------|
| `instance_type` | t3.micro | t3.small | t3.medium |
| `ebs_volume_size` | 20 GiB | 20 GiB | 30 GiB |
| State key | `dev-ec2/` | `qa-ec2/` | `prod-ec2/` |

---

## 6. AWS Resources Created

| Resource | ID / Name | Notes |
|----------|-----------|-------|
| EC2 Instance | `i-079c4f67264c22291` | t3.micro, running |
| Launch Template | `lt-009a3e5b05407464d` | v2 (with Pem_key) |
| IAM Role | `loginapp-dev-ec2-role` | SSM managed |
| IAM Instance Profile | `loginapp-dev-ec2-profile` | Bound to role |
| Key Pair (pre-existing) | `Pem_key` | `key-00f84a8d4c4d7317a` |
| VPC (pre-existing) | `vpc-092b0d10291014ae3` | Default VPC |
| Security Group (pre-existing) | `sg-07ef0129690a48376` | Default SG |
| Subnet (pre-existing) | `subnet-0069d8637a5a7e78e` | Public, ap-south-1c |

**Security Group Rules added during deployment:**

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 0-65535 | TCP | 0.0.0.0/0 | Pre-existing rule |
| 8000 | TCP | 0.0.0.0/0 | FastAPI direct access |
| 80 | TCP | 0.0.0.0/0 | nginx / frontend |

---

## 7. Step-by-Step Deployment Guide

### 7.1 Discover Existing AWS Resources

```bash
# Find VPC
aws ec2 describe-vpcs \
  --query 'Vpcs[*].{VpcId:VpcId,CIDR:CidrBlock,Name:Tags[?Key==`Name`]|[0].Value}' \
  --output table

# Find Security Groups
aws ec2 describe-security-groups \
  --query 'SecurityGroups[*].{GroupId:GroupId,GroupName:GroupName,VpcId:VpcId}' \
  --output table

# Find Subnets in a VPC
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=vpc-092b0d10291014ae3" \
  --query 'Subnets[*].{SubnetId:SubnetId,AZ:AvailabilityZone,Public:MapPublicIpOnLaunch}' \
  --output table

# Find existing key pairs
aws ec2 describe-key-pairs \
  --query 'KeyPairs[*].{Name:KeyName,Id:KeyPairId}' \
  --output table

# Find latest Amazon Linux 2023 AMI in ap-south-1
aws ec2 describe-images \
  --region ap-south-1 \
  --owners amazon \
  --filters "Name=name,Values=al2023-ami-2023*-x86_64" "Name=state,Values=available" \
  --query 'sort_by(Images, &CreationDate)[-1].{ImageId:ImageId,Name:Name}' \
  --output table
```

### 7.2 Terraform Init, Plan, Apply

```bash
cd infra/envs/dev-ec2

# Initialise — downloads providers, connects to S3 backend
terraform init

# Preview changes
terraform plan

# Apply — creates IAM role, launch template, EC2 instance
terraform apply -auto-approve

# Check outputs
terraform output
```

**Expected outputs:**
```
ec2_sg_id                      = "sg-07ef0129690a48376"
iam_role_arn                   = "arn:aws:iam::478398889582:role/loginapp-dev-ec2-role"
instance_id                    = "i-079c4f67264c22291"
instance_profile_name          = "loginapp-dev-ec2-profile"
instance_public_ip             = "65.0.69.91"
launch_template_id             = "lt-009a3e5b05407464d"
launch_template_latest_version = 2
vpc_id                         = "vpc-092b0d10291014ae3"
```

### 7.3 Attach SSH Key Pair

Set `key_pair_name = "Pem_key"` in `terraform.tfvars` then re-apply.

> **Important:** SSH key pair cannot be changed on a running instance. The instance must be terminated and re-created. Terraform handles this automatically when the launch template is updated and `terraform apply` is run again.

```bash
# Set correct permissions on PEM file (required by SSH)
chmod 400 /Users/aswin3661/downloads/Pem_key.pem

# Test SSH connection
ssh -i /Users/aswin3661/downloads/Pem_key.pem ec2-user@65.0.69.91
```

### 7.4 Deploy Backend (FastAPI)

```bash
# Open port 8000 on security group
aws ec2 authorize-security-group-ingress \
  --region ap-south-1 \
  --group-id sg-07ef0129690a48376 \
  --protocol tcp --port 8000 --cidr 0.0.0.0/0

# Copy app files to EC2
rsync -avz --exclude='__pycache__' --exclude='*.pyc' \
  -e "ssh -i /Users/aswin3661/downloads/Pem_key.pem -o StrictHostKeyChecking=no" \
  /Users/aswin3661/Documents/Work/Loginapplication/todo-app/ \
  ec2-user@65.0.69.91:/home/ec2-user/todo-app/

# SSH in and set up
ssh -i /Users/aswin3661/downloads/Pem_key.pem -o StrictHostKeyChecking=no -t ec2-user@65.0.69.91 << 'EOF'
# Install Python 3.11
sudo dnf install -y python3.11 python3.11-pip

# Install dependencies
cd /home/ec2-user/todo-app
pip3.11 install -r requirements.txt --quiet

# Create systemd service
sudo tee /etc/systemd/system/todo-app.service > /dev/null << 'SERVICE'
[Unit]
Description=Todo FastAPI App
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/todo-app
ExecStart=/home/ec2-user/.local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
Environment=ENVIRONMENT=development

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable todo-app
sudo systemctl restart todo-app
sudo systemctl status todo-app --no-pager
EOF
```

**Verify backend is running:**
```bash
curl http://65.0.69.91:8000/health
curl http://65.0.69.91:8000/docs   # Swagger UI
```

### 7.5 Deploy Frontend (React)

```bash
# Open port 80
aws ec2 authorize-security-group-ingress \
  --region ap-south-1 \
  --group-id sg-07ef0129690a48376 \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

# Copy source files (exclude node_modules)
rsync -avz --exclude='node_modules' --exclude='.git' \
  -e "ssh -i /Users/aswin3661/downloads/Pem_key.pem -o StrictHostKeyChecking=no" \
  /Users/aswin3661/Documents/Work/Loginapplication/todo-app-frontend/ \
  ec2-user@65.0.69.91:/home/ec2-user/todo-app-frontend/

# Build on the server (Node.js already installed via dnf)
ssh -i /Users/aswin3661/downloads/Pem_key.pem -o StrictHostKeyChecking=no -t ec2-user@65.0.69.91 \
  "cd /home/ec2-user/todo-app-frontend && npm install && npm run build"
```

### 7.6 Configure nginx

```bash
ssh -i /Users/aswin3661/downloads/Pem_key.pem -o StrictHostKeyChecking=no -t ec2-user@65.0.69.91 "

# Install nginx
sudo dnf install -y nginx

# Deploy built files
sudo mkdir -p /var/www/todo-app
sudo cp -r /home/ec2-user/todo-app-frontend/dist/* /var/www/todo-app/
sudo chown -R nginx:nginx /var/www/todo-app

# Write nginx config
sudo tee /etc/nginx/conf.d/todo-app.conf > /dev/null << 'NGINX'
server {
    listen 80 default_server;
    server_name _;

    root /var/www/todo-app;
    index index.html;

    # React SPA — fallback to index.html for client-side routing
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Proxy API requests to FastAPI backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
    }
}
NGINX

# Disable default nginx server block to avoid port conflict
sudo sed -i '/^    server {/,/^    }/{ s/^/#DISABLED#/ }' /etc/nginx/nginx.conf

# Kill anything holding port 80 and start nginx
sudo fuser -k 80/tcp || true
sudo systemctl enable nginx
sudo systemctl restart nginx
"
```

---

## 8. Application Stack

### Backend — FastAPI

| Setting | Value |
|---------|-------|
| Framework | FastAPI 0.111+ |
| Server | Uvicorn (ASGI) |
| Python | 3.11 |
| Port | 8000 |
| Storage | In-memory (list) |
| Process manager | systemd |

**Key files:**
- `main.py` — App factory, CORS middleware, lifespan hooks
- `src/api/routes.py` — REST endpoints (CRUD)
- `src/models/todo.py` — Pydantic models
- `src/services/todo_service.py` — Business logic
- `src/repositories/todo_repository.py` — Data access layer
- `src/config/settings.py` — Pydantic-settings (reads `.env`)

### Frontend — React + Vite

| Setting | Value |
|---------|-------|
| Framework | React 18 + TypeScript |
| Build tool | Vite 5 |
| Served by | nginx (static files) |
| Port | 80 |
| API base | `/api/v1` (proxied by nginx) |

**Key files:**
- `src/api/todoApi.ts` — Fetch wrapper for all API calls
- `src/hooks/useTodos.ts` — React hook managing todo state
- `src/components/` — TodoForm, TodoList, TodoItem, TodoFilters
- `vite.config.ts` — Dev proxy config (`/api` → `:8000`)

---

## 9. Networking and Security

### Port Map

| Port | Service | Open to |
|------|---------|---------|
| 22 | SSH | 0.0.0.0/0 (restrict to your IP in prod) |
| 80 | nginx (frontend + API proxy) | 0.0.0.0/0 |
| 8000 | FastAPI (direct) | 0.0.0.0/0 |

### IAM Permissions (EC2 Role)

The EC2 instance has one managed policy attached:

- **AmazonSSMManagedInstanceCore** — allows AWS Systems Manager to connect to the instance without SSH (useful when SSH access is lost)

---

## 10. Access URLs

| URL | What it serves |
|-----|---------------|
| `http://65.0.69.91` | React frontend (Todo App) |
| `http://65.0.69.91/api/v1/todos` | Todo REST API (via nginx proxy) |
| `http://65.0.69.91:8000/docs` | Swagger UI (FastAPI auto-generated) |
| `http://65.0.69.91:8000/redoc` | ReDoc API documentation |
| `http://65.0.69.91:8000/health` | Health check endpoint |

---

## 11. Operational Commands

### SSH Access
```bash
ssh -i /Users/aswin3661/downloads/Pem_key.pem ec2-user@65.0.69.91
```

### Backend (FastAPI / todo-app)
```bash
sudo systemctl status todo-app      # Check status
sudo systemctl restart todo-app     # Restart
sudo systemctl stop todo-app        # Stop
sudo journalctl -u todo-app -f      # Live logs
sudo journalctl -u todo-app --since "1 hour ago"  # Recent logs
```

### Frontend (nginx)
```bash
sudo systemctl status nginx         # Check status
sudo systemctl restart nginx        # Restart
sudo nginx -t                       # Test config
sudo cat /var/log/nginx/access.log  # Access logs
sudo cat /var/log/nginx/error.log   # Error logs
```

### Re-deploy Frontend (after code changes)
```bash
# From local machine:
rsync -avz --exclude='node_modules' --exclude='.git' \
  -e "ssh -i /Users/aswin3661/downloads/Pem_key.pem" \
  /Users/aswin3661/Documents/Work/Loginapplication/todo-app-frontend/ \
  ec2-user@65.0.69.91:/home/ec2-user/todo-app-frontend/

ssh -i /Users/aswin3661/downloads/Pem_key.pem -t ec2-user@65.0.69.91 \
  "cd /home/ec2-user/todo-app-frontend && npm run build && \
   sudo cp -r dist/* /var/www/todo-app/ && \
   sudo chown -R nginx:nginx /var/www/todo-app"
```

### Re-deploy Backend (after code changes)
```bash
rsync -avz --exclude='__pycache__' \
  -e "ssh -i /Users/aswin3661/downloads/Pem_key.pem" \
  /Users/aswin3661/Documents/Work/Loginapplication/todo-app/ \
  ec2-user@65.0.69.91:/home/ec2-user/todo-app/

ssh -i /Users/aswin3661/downloads/Pem_key.pem -t ec2-user@65.0.69.91 \
  "sudo systemctl restart todo-app"
```

### Terraform Operations
```bash
cd infra/envs/dev-ec2

terraform plan              # Preview changes
terraform apply             # Apply changes
terraform output            # Show outputs
terraform state list        # List managed resources
terraform destroy           # Tear down all resources
```

---

## 12. Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `terraform plan` — no VPC/SG found | Data source lookup failed; resources don't exist yet | Use variable inputs instead of data sources |
| `no matching EC2 VPC found` | AWS CLI region differs from tfvars region | Check `aws configure get region` and match `aws_region` in tfvars |
| `InvalidParameterCombination` on RunInstances | `associate_public_ip_address = true` conflicts with SG set in launch template | Remove `associate_public_ip_address`; subnet default handles it |
| SSH timeout | Old/terminated instance IP | Get fresh IP from `terraform output instance_public_ip` |
| Key pair not attached | Key pair can't change on running instance | Update tfvars and re-apply; Terraform recreates instance |
| nginx `bind() failed (98)` | Another process holds port 80 | `sudo fuser -k 80/tcp && sudo systemctl restart nginx` |
| nginx `conflicting server name` | Default nginx.conf has `server_name _` block | Comment out default server block in `/etc/nginx/nginx.conf` |
| Frontend `Could not resolve entry module index.html` | `scp -r` uploaded into wrong subdirectory due to `node_modules` | Use `rsync --exclude=node_modules` instead of `scp -r` |

---

## 13. Lessons Learned

1. **Use `rsync` over `scp -r` for Node projects** — `scp -r` copies `node_modules` (thousands of files) and fails silently on deeply nested paths. `rsync --exclude=node_modules` transfers only source files.

2. **Launch Template ≠ Running Instance** — A Terraform `ec2` module that only creates a Launch Template does not launch any instance. An explicit `aws_instance` resource referencing the template is required.

3. **Key pairs are immutable on running instances** — AWS does not allow changing the key pair of a running instance. The instance must be terminated and relaunched with the key pair set in the Launch Template from the start.

4. **Region must match everywhere** — The AWS CLI default region (`aws configure get region`), the Terraform `aws_region` variable, and the actual location of VPC/subnet/SG resources must all be consistent. Mismatches cause silent failures (empty VPC lists, data source lookups returning nothing).

5. **`associate_public_ip_address` conflicts with launch template SGs** — When a Launch Template sets `vpc_security_group_ids`, AWS creates a network interface automatically. Setting `associate_public_ip_address = true` on the `aws_instance` tries to create another interface, which conflicts. Remove it — the subnet's `map_public_ip_on_launch = true` handles the public IP.

6. **Systemd for long-running processes** — Using systemd (`Restart=always`) ensures the FastAPI app survives crashes and automatically starts on reboot, which is essential for production-grade deployments.

7. **nginx reverse proxy pattern** — Serving the React SPA and proxying `/api/*` to the backend from the same nginx server on port 80 avoids CORS issues entirely, since the browser sees a single origin.

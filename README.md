# Loginapplication

Full-stack todo application with a FastAPI backend, React/Vite frontend, Terraform infrastructure, Helm deployment charts, and GitHub Actions automation.

## Ordered Repository Layout

```text
Loginapplication/
|-- .github/                 # CI, security scanning, branch automation
|-- docs/                    # Implementation notes and runbooks
|-- helm/                    # Kubernetes deployment charts
|   |-- todo-backend/
|   `-- todo-frontend/
|-- infra/                   # Terraform environments, modules, and IAM policy files
|   |-- envs/
|   |-- iam/
|   `-- modules/
|-- todo-app/                # FastAPI backend service
|-- todo-app-frontend/       # React + TypeScript frontend
|-- .gitignore
`-- README.md
```

## Folder Ownership

| Path | Purpose |
| --- | --- |
| `.github/workflows/` | CI tests, CodeQL scanning, container builds, and dev deployment |
| `.github/scripts/` | Repository automation scripts |
| `docs/` | Human-readable implementation and operations documentation |
| `helm/todo-backend/` | Backend Kubernetes chart and environment values |
| `helm/todo-frontend/` | Frontend Kubernetes chart and environment values |
| `infra/envs/` | Terraform environment entrypoints for dev, qa, prod, EC2, and EKS |
| `infra/modules/` | Reusable Terraform modules for VPC, EC2, EKS, ALB, ASG, and security groups |
| `infra/iam/` | IAM policy documents used by infrastructure |
| `todo-app/` | Backend source, tests, Dockerfile, and Python dependencies |
| `todo-app-frontend/` | Frontend source, tests, Dockerfile, and npm dependencies |

## Common Commands

```bash
# Backend tests
cd todo-app
pip install -r requirements-dev.txt
pytest tests/ -v

# Frontend tests and build
cd todo-app-frontend
npm ci
npm test
npm run build

# Helm validation
helm lint ./helm/todo-backend --values helm/todo-backend/values.yaml --values helm/todo-backend/values-dev.yaml
helm lint ./helm/todo-frontend --values helm/todo-frontend/values.yaml --values helm/todo-frontend/values-dev.yaml

# Terraform plan example
cd infra/envs/dev-ec2
terraform init
terraform plan
```

## Notes

- Keep `todo-app/` and `todo-app-frontend/` paths stable unless workflows and deployment docs are updated at the same time.
- Local generated folders such as `node_modules/`, `dist/`, `.venv/`, `.terraform/`, caches, and logs are ignored.
- Detailed EC2 deployment notes live in [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md).

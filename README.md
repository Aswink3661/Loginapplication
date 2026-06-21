# Loginapplication

Full-stack Todo application deployed through a GitHub Actions, GHCR, Helm, Terraform, and AWS EKS workflow.

The application has:

- FastAPI backend in `todo-app/`
- React + TypeScript + Vite frontend in `todo-app-frontend/`
- Terraform infrastructure in `infra/`
- Helm charts in `helm/`
- CI, CodeQL, image build, and dev deployment workflows in `.github/workflows/`

## Current Workflow

```text
pull request to main/develop
  -> backend tests
  -> frontend tests and coverage
  -> Helm lint and template render
  -> CodeQL scan
  -> merge gate

push to develop or manual workflow dispatch
  -> build backend image
  -> build frontend image
  -> push images to GHCR
  -> update Helm image tags
  -> deploy backend and frontend to dev EKS
  -> verify Kubernetes rollout
```

## Branch Rules

| Branch/Event | Workflow | Purpose |
| --- | --- | --- |
| Pull request to `develop` | `CI` | Validate backend, frontend, Helm, and CodeQL before merge |
| Pull request to `main` | `CI` | Validate release merge and require source branch `develop` |
| Push to `develop` | `Dev - Build, Tag & Deploy` | Build containers, push GHCR images, deploy to dev EKS |
| Manual dispatch | `Dev - Build, Tag & Deploy` | Run the dev deployment workflow on demand |
| Push or PR to `main`/`develop` | `CodeQL Advanced` | Advanced CodeQL analysis for Python and JavaScript/TypeScript |
| Weekly schedule | `CodeQL Advanced` | Scheduled security scan |

## Repository Layout

```text
Loginapplication/
|-- .github/
|   |-- scripts/                 # Repository automation scripts
|   `-- workflows/               # CI, CodeQL, build, and deploy workflows
|-- docs/                        # Implementation notes and runbooks
|-- helm/
|   |-- todo-backend/            # Backend Kubernetes chart
|   `-- todo-frontend/           # Frontend Kubernetes chart
|-- infra/
|   |-- envs/                    # Terraform environment entrypoints
|   |-- iam/                     # IAM policy documents
|   `-- modules/                 # Reusable Terraform modules
|-- todo-app/                    # FastAPI backend service
|-- todo-app-frontend/           # React/Vite frontend service
|-- .gitignore
`-- README.md
```

## CI Workflow

File: `.github/workflows/ci.yml`

The CI workflow runs on pull requests targeting `main` or `develop`.

It performs:

- Backend unit tests with Python 3.12, `pytest`, and coverage upload
- Frontend unit tests with Node.js 20, Vitest, and coverage upload
- Helm lint and render checks for backend and frontend charts
- CodeQL analysis for Python and JavaScript/TypeScript
- Pull request source check so PRs into `main` only come from `develop`
- Final merge gate that fails if required validation jobs do not pass

## Dev Deployment Workflow

File: `.github/workflows/dev-docker-build-deploy.yml`

The dev deployment workflow runs on pushes to `develop` and can also be started manually.

It uses:

| Setting | Value |
| --- | --- |
| Registry | `ghcr.io` |
| Backend image | `ghcr.io/aswink3661/todo-app-backend` |
| Frontend image | `ghcr.io/aswink3661/todo-app-frontend` |
| AWS region | `ap-south-1` |
| EKS cluster | `loginapp-dev-eks` |
| Namespace | `loginapp-dev` |
| Backend release | `todo-backend` |
| Frontend release | `todo-frontend` |

Deployment flow:

1. Build backend image from `todo-app/Dockerfile`.
2. Build frontend image from `todo-app-frontend/Dockerfile`.
3. Tag both images as `sha-<short-sha>`.
4. Push both images to GitHub Container Registry.
5. Check that the dev EKS cluster exists.
6. Update kubeconfig and verify Kubernetes API access.
7. Resolve EFS file system and access point IDs.
8. Lint Helm charts with the new image tags.
9. Update `helm/todo-backend/values.yaml` and `helm/todo-frontend/values.yaml`.
10. Commit the updated image tags back to `develop` with `[skip ci]`.
11. Deploy backend and frontend with `helm upgrade --install --atomic`.
12. Verify Kubernetes rollout for both deployments.

## Required GitHub Secrets

| Secret | Used By | Purpose |
| --- | --- | --- |
| `GH_PAT` | Dev deploy checkout and push | Allows the workflow to commit updated Helm image tags |
| `AWS_ACCESS_KEY_ID` | Dev deploy | Authenticates to AWS |
| `AWS_SECRET_ACCESS_KEY` | Dev deploy | Authenticates to AWS |
| `GITHUB_TOKEN` | Image build jobs | Logs in to GHCR for package push |

The AWS principal must be able to describe the EKS cluster, update kubeconfig, access the Kubernetes API, resolve EFS IDs, and deploy Helm releases.

## Local Validation

Run these before opening a pull request:

```bash
# Backend tests
cd todo-app
pip install -r requirements-dev.txt
pytest tests/ -v

# Frontend tests and production build
cd ../todo-app-frontend
npm ci
npm test
npm run test:coverage
npm run build

# Helm lint and render
cd ..
helm lint ./helm/todo-backend \
  --values helm/todo-backend/values.yaml \
  --values helm/todo-backend/values-dev.yaml \
  --set image.tag=ci \
  --set-string storage.efs.fileSystemId=fs-00000000000000000 \
  --set-string storage.efs.accessPointId=fsap-00000000000000000

helm lint ./helm/todo-frontend \
  --values helm/todo-frontend/values.yaml \
  --values helm/todo-frontend/values-dev.yaml \
  --set image.tag=ci

helm template todo-backend ./helm/todo-backend \
  --namespace loginapp-dev \
  --values helm/todo-backend/values.yaml \
  --values helm/todo-backend/values-dev.yaml \
  --set image.tag=ci \
  --set-string storage.efs.fileSystemId=fs-00000000000000000 \
  --set-string storage.efs.accessPointId=fsap-00000000000000000

helm template todo-frontend ./helm/todo-frontend \
  --namespace loginapp-dev \
  --values helm/todo-frontend/values.yaml \
  --values helm/todo-frontend/values-dev.yaml \
  --set image.tag=ci
```

## Terraform Validation

Terraform environments live under `infra/envs/`; reusable modules live under `infra/modules/`.

```bash
terraform fmt -check -recursive infra

terraform -chdir=infra/envs/dev validate
terraform -chdir=infra/envs/dev-eks validate
terraform -chdir=infra/envs/dev-ec2 validate
terraform -chdir=infra/envs/qa validate
terraform -chdir=infra/envs/qa-ec2 validate
terraform -chdir=infra/envs/prod validate
terraform -chdir=infra/envs/prod-ec2 validate
```

If provider schemas cannot load locally, run `terraform init` in the target environment before validating.

## Deployment Notes

- Apply or verify `infra/envs/dev-eks` before running the dev deployment workflow.
- The dev workflow expects EFS resources named `loginapp-dev-eks-docs-efs` and `loginapp-dev-eks-docs-ap`.
- Helm values files are source controlled and the dev workflow updates image tags automatically.
- Keep `todo-app/` and `todo-app-frontend/` paths stable because workflows use them as Docker build contexts.
- Detailed EC2 deployment notes are in [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md).

## Generated Files

The repo ignores local runtime and build outputs, including:

- Python caches, `.venv/`, `.pytest_cache/`, and logs
- Node `node_modules/`, `dist/`, `coverage/`, and Vite cache
- Terraform `.terraform/`, state files, and lock files
- Local `.env` files

# Migration Guide: DockerHub to Private AWS ECR

## Current State

Three Docker images are built and pushed to DockerHub (`docker.io/radixdlt/`):

| Image | Dockerfile | Registry Path |
|-------|-----------|---------------|
| `airflow` | `airflow/Dockerfile` | `docker.io/radixdlt/airflow` |
| `token-price-service` | `consumers/token-price-service/Dockerfile` | `docker.io/radixdlt/token-price-service` |
| `airflow-migration` | `database/Dockerfile` | `docker.io/radixdlt/airflow-migration` |

**CI builds** use a reusable workflow from `trellisarch/public-iac-resuable-artifacts/.github/workflows/docker-build.yml`, which authenticates to DockerHub via an IAM role (`DOCKERHUB_RELEASER_ROLE`).

**EKS clusters** pull images using a `docker-hub-dev` imagePullSecret created via ExternalSecrets from AWS Secrets Manager.



## Target State

Push to private AWS ECR in the target AWS account (passed as input). EKS nodes authenticate via IAM — no imagePullSecrets needed.

Target image URLs: `<account_id>.dkr.ecr.eu-west-2.amazonaws.com/<image_name>:<tag>`

---

## Phase 1: AWS Infrastructure (Terraform)

**Repo:** `trellisarch/trellisarch-iac`

All Terraform changes go in as a **new separate stack** for ECR, following the existing pattern:

```
terraform/
├── modules/aws/ecr/              # New reusable module
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── stacks/ecr/                   # New deployable stack
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── providers.tf
│   └── versions.tf
└── env/prod/ecr.tfvars           # Environment config
```

### 1.1 ECR Module (`terraform/modules/aws/ecr/`)

**variables.tf:**

```hcl
variable "repositories" {
  description = "List of ECR repository names to create"
  type        = list(string)
}

variable "image_tag_mutability" {
  description = "Tag mutability setting"
  type        = string
  default     = "IMMUTABLE"
}

variable "max_tagged_image_count" {
  description = "Max number of tagged images to retain"
  type        = number
  default     = 50
}

variable "untagged_expiry_days" {
  description = "Days before untagged images expire"
  type        = number
  default     = 7
}

variable "github_oidc_provider_arn" {
  description = "ARN of the GitHub Actions OIDC provider"
  type        = string
  default     = ""
}

variable "github_org" {
  description = "GitHub organization name for OIDC trust"
  type        = string
  default     = "trellisarch"
}

variable "github_repo" {
  description = "GitHub repo name for OIDC trust (e.g., token-pricing-service)"
  type        = string
  default     = "*"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
```

**main.tf:**

```hcl
# ECR Repositories
resource "aws_ecr_repository" "this" {
  for_each = toset(var.repositories)

  name                 = each.value
  image_tag_mutability = var.image_tag_mutability

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.tags
}

# Lifecycle policy for each repo
resource "aws_ecr_lifecycle_policy" "this" {
  for_each   = aws_ecr_repository.this
  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire untagged images after ${var.untagged_expiry_days} days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = var.untagged_expiry_days
        }
        action = { type = "expire" }
      },
      {
        rulePriority = 2
        description  = "Keep last ${var.max_tagged_image_count} tagged images"
        selection = {
          tagStatus      = "tagged"
          tagPrefixList  = ["sha-"]
          countType      = "imageCountMoreThan"
          countNumber    = var.max_tagged_image_count
        }
        action = { type = "expire" }
      }
    ]
  })
}

# GitHub Actions OIDC provider (if not already created)
resource "aws_iam_openid_connect_provider" "github" {
  count = var.github_oidc_provider_arn == "" ? 1 : 0

  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]

  tags = var.tags
}

locals {
  oidc_provider_arn = var.github_oidc_provider_arn != "" ? var.github_oidc_provider_arn : aws_iam_openid_connect_provider.github[0].arn
  oidc_provider     = replace(local.oidc_provider_arn, "/^(.*provider/)/", "")
}

# IAM role for GitHub Actions CI to push images
resource "aws_iam_role" "gh_ecr_pusher" {
  name = "gh-ecr-pusher"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = local.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringLike = {
            "${local.oidc_provider}:sub" = "repo:${var.github_org}/${var.github_repo}:*"
          }
          StringEquals = {
            "${local.oidc_provider}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "ecr_push" {
  name = "ecr-push"
  role = aws_iam_role.gh_ecr_pusher.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ecr:GetAuthorizationToken"]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = [for repo in aws_ecr_repository.this : repo.arn]
      }
    ]
  })
}
```

**outputs.tf:**

```hcl
output "repository_urls" {
  description = "Map of repository name to URL"
  value       = { for k, v in aws_ecr_repository.this : k => v.repository_url }
}

output "ecr_pusher_role_arn" {
  description = "ARN of the GitHub Actions ECR push role"
  value       = aws_iam_role.gh_ecr_pusher.arn
}

output "oidc_provider_arn" {
  description = "ARN of the GitHub Actions OIDC provider"
  value       = local.oidc_provider_arn
}
```

### 1.2 ECR Stack (`terraform/stacks/ecr/`)

**main.tf:**

```hcl
module "ecr" {
  source = "../../modules/aws/ecr"

  repositories = var.repositories

  image_tag_mutability   = var.image_tag_mutability
  max_tagged_image_count = var.max_tagged_image_count
  untagged_expiry_days   = var.untagged_expiry_days

  github_oidc_provider_arn = var.github_oidc_provider_arn
  github_org               = var.github_org
  github_repo              = var.github_repo

  tags = {
    project     = "trellisarch"
    environment = var.environment
    managed_by  = "terraform"
    stack       = "ecr"
  }
}
```

**variables.tf:**

```hcl
variable "environment" {
  type    = string
  default = "prod"
}

variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "repositories" {
  type = list(string)
}

variable "image_tag_mutability" {
  type    = string
  default = "IMMUTABLE"
}

variable "max_tagged_image_count" {
  type    = number
  default = 50
}

variable "untagged_expiry_days" {
  type    = number
  default = 7
}

variable "github_oidc_provider_arn" {
  type    = string
  default = ""
}

variable "github_org" {
  type    = string
  default = "trellisarch"
}

variable "github_repo" {
  type    = string
  default = "token-pricing-service"
}
```

**providers.tf:**

```hcl
provider "aws" {
  region = var.region
}
```

**versions.tf:**

```hcl
terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
  }
}
```

### 1.3 Environment Config (`terraform/env/prod/ecr.tfvars`)

```hcl
environment = "prod"
region      = "eu-west-2"

repositories = [
  "airflow",
  "token-price-service",
  "airflow-migration",
]

github_org  = "trellisarch"
github_repo = "token-pricing-service"
```

### 1.4 Deploy the Stack

```bash
cd terraform/stacks/ecr

terraform init \
  -backend-config="bucket=trellisarch-iac" \
  -backend-config="key=ecr/terraform.tfstate" \
  -backend-config="region=eu-west-1" \
  -backend-config="dynamodb_table=trellisarch-iac"

terraform plan -var-file="../../env/prod/ecr.tfvars"
terraform apply -var-file="../../env/prod/ecr.tfvars"
```

After apply, note the outputs:
- `ecr_pusher_role_arn` — add as GitHub secret `ECR_PUSHER_ROLE`
- `repository_urls` — use the registry prefix as GitHub variable `AWS_ECR_REGISTRY`

### 1.5 EKS Node Role

Ensure the EKS managed node group IAM role has ECR pull permissions (standard in most setups). This is typically already present via the `AmazonEC2ContainerRegistryReadOnly` managed policy on the EKS node group in the existing AWS stack.

### 1.6 GitHub Secrets/Variables

Add to the `trellisarch/token-pricing-service` GitHub repo settings:

| Type | Name | Value |
|------|------|-------|
| Secret | `ECR_PUSHER_ROLE` | Output from `terraform output ecr_pusher_role_arn` |
| Variable | `AWS_ECR_REGISTRY` | `<ACCOUNT_ID>.dkr.ecr.eu-west-2.amazonaws.com` |

---

## Phase 2: Reusable Workflow

**Repo:** `trellisarch/public-iac-resuable-artifacts`
**File:** `.github/workflows/docker-build.yml`

Add an ECR login step after the existing `configure-aws-credentials` step:

```yaml
- if: ${{ contains(inputs.image_registry, 'ecr') }}
  name: Login to Amazon ECR
  uses: aws-actions/amazon-ecr-login@v2
```

This uses the already-assumed IAM role credentials. The step only runs when `image_registry` contains `ecr`, so existing DockerHub consumers are unaffected.

No new inputs needed — the existing `image_registry`, `image_organization`, `image_name`, and `role_to_assume` inputs are sufficient.

---

## Phase 3: CI Workflow Changes (this repo)

### 3.1 `airflow-ci.yml`

**Tags job** — Update metadata-action images (line 48):

```yaml
# FROM:
images: |
  docker.io/radixdlt/airflow-service

# TO:
images: |
  ${{ vars.AWS_ECR_REGISTRY }}/airflow-service
```

**Build jobs** (`build-airflow`, `build-token-service`, `build-airflow-migrations`) — Change registry and auth:

```yaml
# FROM:
with:
  image_registry: "docker.io"
  image_organization: "radixdlt"
  image_name: "airflow"
  # ...
secrets:
  role_to_assume: ${{ secrets.DOCKERHUB_RELEASER_ROLE }}

# TO:
with:
  image_registry: ${{ vars.AWS_ECR_REGISTRY }}
  image_organization: ""
  image_name: "airflow"
  # ...
secrets:
  role_to_assume: ${{ secrets.ECR_PUSHER_ROLE }}
```

Repeat for all 3 build jobs. The `image_organization` becomes empty because ECR URLs are `<registry>/<repo_name>` with no org level.

### 3.2 `airflow-db-migrations.yml`

Same changes as above for the `tags` job (line 38) and `build-airflow-migrations` job (lines 50-64).

### 3.3 `helm-changes.yml`

No changes needed — this workflow doesn't build images, it uses tags from live deployments.

---

## Phase 4: Helm Config Changes (this repo)

### 4.1 Image References

| File | Line | From | To |
|------|------|------|----|
| `deploy/helm/airflow/helmfile.yaml` | 43 | `radixdlt/airflow` | `$ECR_REGISTRY/airflow` (see note) |
| `deploy/helm/airflow/airflow-resources/values.yaml` | 11 | `docker.io/radixdlt/airflow` | Remove (override per-environment) |
| `deploy/helm/airflow/token-price/values.yaml` | 4 | `docker.io/radixdlt/token-price-service` | Remove (override per-environment) |
| `deploy/helm/airflow/db-migrations/values.yaml` | 2 | `radixdlt/airflow-migration` | Remove (override per-environment) |
| `deploy/helm/airflow/environments/dev/db-migrations.yaml.gotmpl` | 2 | `radixdlt/airflow-migration` | `308190735829.dkr.ecr.eu-west-2.amazonaws.com/airflow-migration` |
| `deploy/helm/airflow/environments/prod/db-migrations.yaml.gotmpl` | 2 | `radixdlt/airflow-migration` | `821496737932.dkr.ecr.eu-west-2.amazonaws.com/airflow-migration` |
| `deploy/helm/airflow/environments/pr/db-migrations.yaml.gotmpl` | 2 | `radixdlt/airflow-migration` | `308190735829.dkr.ecr.eu-west-2.amazonaws.com/airflow-migration` |

**Note on helmfile.yaml:** The airflow image repository is currently hardcoded at line 43. Since dev and prod use different AWS accounts, this should be moved into per-environment values or use a helmfile variable:

```yaml
# Option: Pass via CI vars
repository: {{ .StateValues.ci.ecr_registry }}/airflow
```

Then add `ci.ecr_registry=<account>.dkr.ecr.eu-west-2.amazonaws.com` to `helmfile_extra_vars` in CI workflows.

### 4.2 Init Container Image References

**File:** `deploy/helm/airflow/environments/dev/values.yaml.gotmpl` (line ~60)

```yaml
# FROM:
image: radixdlt/airflow-migration:{{ .StateValues.ci.AIRFLOW_MIGRATION_IMAGE_TAG }}

# TO:
image: 308190735829.dkr.ecr.eu-west-2.amazonaws.com/airflow-migration:{{ .StateValues.ci.AIRFLOW_MIGRATION_IMAGE_TAG }}
```

Same change in `environments/pr/values.yaml.gotmpl`.

### 4.3 Remove DockerHub Pull Secrets

With private ECR in the same AWS account, EKS authenticates via the node IAM role. No imagePullSecrets needed.

**Remove `imagePullSecrets` from:**

| File | Lines |
|------|-------|
| `deploy/helm/airflow/airflow-resources/values.yaml` | 16-17 |
| `deploy/helm/airflow/token-price/values.yaml` | 7-8 |
| `deploy/helm/airflow/db-migrations/templates/job.yaml` | 12-13 |

**Remove `docker.secrets` config from:**

| File | Lines |
|------|-------|
| `deploy/helm/airflow/airflow-resources/values.yaml` | 41-44 |
| `deploy/helm/airflow/token-price/values.yaml` | 13-15 |
| `deploy/helm/airflow/environments/dev/values.yaml.gotmpl` | 41-44 |
| `deploy/helm/airflow/environments/pr/values.yaml.gotmpl` | 14-17 |
| `deploy/helm/airflow/environments/prod/values.yaml.gotmpl` | 55-58 |

**Remove `registry.secretName` from:**

| File | Lines |
|------|-------|
| `deploy/helm/airflow/environments/dev/values.yaml.gotmpl` | 55-56 |
| `deploy/helm/airflow/environments/pr/values.yaml.gotmpl` | 33-34 |
| `deploy/helm/airflow/environments/prod/values.yaml.gotmpl` | 70-71 |

**Delete ExternalSecret templates:**

| File | Reason |
|------|--------|
| `deploy/helm/airflow/airflow-resources/templates/docker-secret.yaml` | No longer needed |
| `deploy/helm/airflow/token-price/templates/docker-secret.yaml` | No longer needed |

---

## Migration Sequence

| Step | What | Risk | Rollback |
|------|------|------|----------|
| 1 | Create ECR repos + IAM roles (Terraform) | None — additive | Delete resources |
| 2 | Add ECR login step to reusable workflow | None — conditional, existing consumers unaffected | Revert commit |
| 3 | Add GitHub secrets/variables | None | Remove them |
| 4 | Update CI workflows to push to ECR | Images stop going to DockerHub | Revert to DockerHub params |
| 5 | Verify images appear in ECR | — | — |
| 6 | Update Helm configs (image refs + remove pull secrets) | Pods fail if ECR pull doesn't work | Revert Helm changes |
| 7 | Deploy to dev, verify | — | Revert Helm, redeploy |
| 8 | Deploy to prod, verify | — | Revert Helm, redeploy |
| 9 | Remove `DOCKERHUB_RELEASER_ROLE` secret | Can't push to DockerHub anymore | Re-add secret |
| 10 | Remove DockerHub creds from AWS Secrets Manager | — | — |

**Recommended approach:** Do steps 4 + 6 in a single PR. During the transition, images from previous deploys (on DockerHub) remain available, so existing pods won't be affected. New deployments will pull from ECR.

## Verification Checklist

- [ ] ECR repos exist in target AWS account(s)
- [ ] CI push role can authenticate and push to ECR
- [ ] After CI runs: images visible in ECR (`aws ecr describe-images --repository-name airflow`)
- [ ] After dev deploy: `kubectl get pods -n airflow-dev -o jsonpath='{.items[*].spec.containers[*].image}'` shows ECR URLs
- [ ] After dev deploy: `ledger_current_price` DAG runs successfully
- [ ] After prod deploy: same checks
- [ ] No `docker-hub-dev` or `dockerhub-dev` secrets remain in Kubernetes

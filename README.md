<<<<<<< HEAD
# SARPS – AI-Assisted Student Academic Risk Prediction (DevSecOps edition)
Website + Docker + Jenkins CI/CD + Terraform (AWS) + SonarQube + Trivy. SDG 4 / SDG 9.

## Run locally
    python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
    pip install -r requirements-dev.txt
    python train_pipeline.py        # creates models/risk_model.joblib
    python -m pytest -v             # 19 tests
    python wsgi.py                  # http://127.0.0.1:5000   (dev server)

## Run with Docker
    docker build -t sarps-web .
    docker run -d --name sarps -p 8000:8000 sarps-web
    curl http://localhost:8000/health

## Repo layout
| Path | Purpose |
|---|---|
| app/ | Flask website (routes, templates, static) |
| sarps/ | ML modules: ingestion+privacy, preprocessing, model, risk engine, reporting |
| tests/ | pytest unit + web tests |
| Dockerfile, .dockerignore | Container build (non-root, healthcheck, gunicorn) |
| Jenkinsfile | CI/CD pipeline (test, SonarQube, Trivy, build, push, Terraform plan, deploy) |
| terraform/ | AWS: security group + EC2 (IMDSv2, encrypted disk) |
| sonar-project.properties | SonarQube config |
| docs/ | Diagrams, screenshots, demo CSV, JIRA backlog CSV |

## Security notes
Set `SARPS_SALT` (secret) in production. Never commit `terraform.tfvars`, `*.tfstate` or `*.pem`.
=======
# devsecops
>>>>>>> 9274b6a41132cde909378fd7043337cc08dab8ad

# RUNBOOK – do these on YOUR machine (the tools below cannot run in the build sandbox)
Deadline 17/10/2026. Suggested plan: Day 1 (15 Oct) = steps 1-5 · Day 2 (16 Oct) = steps 6-9 · 17 Oct = submit.
Never show passwords, tokens, AWS keys or .pem files in screenshots or the video.

## 1. GitHub (15 min)
    cd sarps-devsecops
    git init && git add . && git commit -m "Initial commit: SARPS DevSecOps"
    git branch -M main
    git remote add origin https://github.com/<you>/sarps-devsecops.git
    git push -u origin main
Make 2-3 small extra commits on a branch (e.g. `feature/security-headers`) and merge via a Pull Request - screenshot the commit history + PR.

## 2. Docker (15 min)
    docker build -t <dockerhub-user>/sarps-web:latest .
    docker run -d --name sarps -p 8000:8000 <dockerhub-user>/sarps-web:latest
    docker ps && curl http://localhost:8000/health
Screenshot: build output, `docker ps` (shows "healthy"), browser at localhost:8000.
    docker login && docker push <dockerhub-user>/sarps-web:latest

## 3. SonarQube (20 min)
    docker run -d --name sonarqube -p 9000:9000 sonarqube:community
Open http://localhost:9000 (admin/admin, change password) -> Create project "sarps-devsecops" -> generate a token.
    pip install -r requirements-dev.txt && pytest --cov=app --cov=sarps --cov-report=xml
    sonar-scanner -Dsonar.host.url=http://localhost:9000 -Dsonar.token=<TOKEN>      # (install sonar-scanner CLI first)
Screenshot: project overview (Quality Gate, bugs, vulnerabilities, hotspots, coverage, duplications) and the issues list.
If it reports issues: note them, fix what you reasonably can, re-scan, and record before/after.

## 4. Trivy (10 min)  (install: https://trivy.dev)
    trivy fs --scanners vuln,secret,misconfig --format table --output trivy-fs.txt .
    trivy image --severity LOW,MEDIUM,HIGH,CRITICAL --format table --output trivy-image.txt <dockerhub-user>/sarps-web:latest
    trivy config terraform/
Screenshot each terminal result. Copy every finding (ID, package, severity, installed vs fixed version) into the Vulnerability Report.
If the base image has OS-package CVEs: try `python:3.12-slim` rebuilt today, or add `RUN apt-get update && apt-get upgrade -y` and rescan.

## 5. Jenkins (45 min)
Easiest: Ubuntu/WSL/VM with Jenkins LTS, plus docker, python3-venv, trivy, terraform, sonar-scanner installed.
Docker option:
    docker run -d --name jenkins -p 8080:8080 -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock --user root jenkins/jenkins:lts-jdk17
    docker exec -u root jenkins bash -c "apt-get update && apt-get install -y docker.io python3 python3-venv curl unzip"
    (then install trivy + terraform inside the container)
In Jenkins: install plugins (Pipeline, Git, SonarQube Scanner, SSH Agent, Docker Pipeline, JUnit) ->
 Manage Jenkins > System: add SonarQube server named `sonarqube` (URL + token credential) ->
 Tools: add SonarQube Scanner named `sonar-scanner` ->
 Credentials: `dockerhub-creds` (username/password), `ec2-ssh-key` (SSH private key) ->
 New Item > Pipeline > "Pipeline script from SCM" > your GitHub repo > Script Path `Jenkinsfile` -> Build Now.
In Jenkinsfile replace `YOUR_DOCKERHUB_USERNAME`. Screenshot: the Stage View (all green), console output (credentials are masked), archived Trivy reports.
If a stage fails, that is fine to show: fix it and rebuild; mention it in Challenges.

## 6. AWS + Terraform (30 min)
Create an IAM user/role with EC2 permissions, run `aws configure` (keys stay on your machine, never in Git). Create an EC2 key pair in ap-south-1.
    cd terraform
    cp terraform.tfvars.example terraform.tfvars      # edit: key_name, admin_cidr (your IP /32), docker_image
    terraform init
    terraform fmt && terraform validate
    terraform plan
    terraform apply
Output gives `website_url`. Open it. Screenshot: plan summary, apply complete, EC2 console, Security Group rules, website on the public IP.
AFTER recording everything: `terraform destroy` (avoids charges). Check Billing for a free-tier/credit overview.
If `terraform validate` reports a formatting/syntax issue, run `terraform fmt` and fix what it says (the config was written without being run).

## 7. Deploy through Jenkins
Run the pipeline with parameter EC2_HOST = the instance public IP. Screenshot the Deploy stage and `curl http://<ip>/health`.

## 8. JIRA (20 min) - import docs/jira_backlog_import.csv, create 3 sprints, move issues to Done, screenshot backlog + boards.

## 9. Video (3-4 min, voice-over) and LinkedIn
Show in order: website -> GitHub repo -> docker build/run -> Jenkins stage view -> Terraform files + apply -> AWS console -> SonarQube + Trivy results.
Hide terminal history, tokens and any credentials. Post on LinkedIn, paste link into the report (Section 10).

## Final checklist
[ ] Replace all yellow highlighted [placeholders] in the report, vulnerability report and PPT  [ ] Real scan screenshots inserted
[ ] GitHub link  [ ] LinkedIn link  [ ] Faculty/HOD names  [ ] Reflection reworded in your voice + Turnitin  [ ] Export final report to PDF/DOCX

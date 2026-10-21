# Demo video script (3-4 min). Record screen + voice. NO passwords, tokens, keys or .pem visible.
1. (0:00) Website on your AWS public IP (or localhost): "SARPS - AI-assisted student academic risk prediction, now a secure website." Show dashboard, expand a student, upload docs/demo_students.csv, show an invalid file being rejected.
2. (0:50) GitHub repo: files (app/, Dockerfile, Jenkinsfile, terraform/), commit history, merged pull request.
3. (1:15) Terminal: `docker build`, `docker run`, `docker ps` (healthy), curl /health.
4. (1:45) Jenkins: Stage View all green, open console of a build (credentials are masked), show archived Trivy reports.
5. (2:15) Terraform: show main.tf (security group, IMDSv2, encrypted disk), run/show `terraform plan` and `apply` output with the website_url.
6. (2:45) AWS console: EC2 instance running, Security Group rules (SSH only from your IP).
7. (3:05) SonarQube overview + Trivy results; mention findings, severity, fixes.
8. (3:35) Close: "Tests 19/19, 94% coverage, SDG 9: reliable, secure, reproducible." #DevSecOps #SDG9 #SAKEC

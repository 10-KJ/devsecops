// SARPS DevSecOps pipeline (Declarative). Needs on the Jenkins agent: python3, docker, trivy, terraform.
// Jenkins config required: SonarQube server named "sonarqube"; credentials "dockerhub-creds"
// (username/password) and "ec2-ssh-key" (SSH private key); SonarQube Scanner tool "sonar-scanner".
pipeline {
  agent any
  options { timestamps(); disableConcurrentBuilds(); timeout(time: 30, unit: 'MINUTES') }
  parameters {
    booleanParam(name: 'RUN_TERRAFORM_PLAN', defaultValue: true, description: 'terraform validate + plan')
    string(name: 'EC2_HOST', defaultValue: '', description: 'Public IP of the EC2 instance (from terraform output). Empty = skip deploy')
  }
  environment {
    IMAGE   = "YOUR_DOCKERHUB_USERNAME/sarps-web"
    TAG     = "${env.BUILD_NUMBER}"
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

stage('Build & Unit Test') {
    steps {
        sh '''
            python3 -m venv .venv
            .venv/bin/python -m pip install --upgrade pip
            .venv/bin/python -m pip install -r requirements-dev.txt
            .venv/bin/python -m pytest --junitxml=test-results.xml
        '''
    }
    post {
        always {
            junit allowEmptyResults: true, testResults: 'test-results.xml'
        }
    }
}

    stage('SAST: SonarQube') {
      steps {
        withSonarQubeEnv('sonarqube') {
          sh "${tool 'sonar-scanner'}/bin/sonar-scanner"
        }
      }
    }
    stage('Quality Gate') {
      steps { timeout(time: 5, unit: 'MINUTES') { waitForQualityGate abortPipeline: true } }
    }

    stage('Trivy: dependencies, secrets, IaC') {
      steps {
        sh '''
          trivy fs --scanners vuln,secret,misconfig --severity LOW,MEDIUM,HIGH,CRITICAL \
               --format table --output trivy-fs.txt .
          trivy fs --scanners vuln,secret,misconfig --severity CRITICAL --exit-code 1 .
        '''
      }
    }

    stage('Docker Build') { steps { sh 'docker build -t $IMAGE:$TAG -t $IMAGE:latest .' } }

    stage('Trivy: image scan') {
      steps {
        sh '''
          trivy image --severity LOW,MEDIUM,HIGH,CRITICAL --format table --output trivy-image.txt $IMAGE:$TAG
          trivy image --severity CRITICAL --exit-code 1 --ignore-unfixed $IMAGE:$TAG
        '''
      }
    }

    stage('Push image') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh 'echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin'
          sh 'docker push $IMAGE:$TAG && docker push $IMAGE:latest'
        }
      }
      post { always { sh 'docker logout || true' } }
    }

    stage('Terraform validate & plan') {
      when { expression { params.RUN_TERRAFORM_PLAN } }
      steps {
        dir('terraform') {
          sh 'terraform init -input=false && terraform fmt -check && terraform validate && terraform plan -input=false -out=tfplan'
        }
      }
    }

    stage('Deploy to AWS EC2') {
      when { expression { params.EC2_HOST?.trim() } }
      steps {
        sshagent(credentials: ['ec2-ssh-key']) {
          sh '''
            ssh -o StrictHostKeyChecking=accept-new ec2-user@$EC2_HOST \
              "docker pull $IMAGE:$TAG && docker rm -f sarps || true && \
               docker run -d --name sarps --restart unless-stopped -p 80:8000 $IMAGE:$TAG"
            sleep 10 && curl -fsS http://$EC2_HOST/health
          '''
        }
      }
    }
  }
  post {
    always { archiveArtifacts artifacts: 'trivy-*.txt, coverage.xml', allowEmptyArchive: true }
    success { echo 'Pipeline finished: build, test, scan, push and deploy OK.' }
    failure { echo 'Pipeline failed: see the stage that turned red (tests, quality gate, or Trivy CRITICAL).' }
  }
}

pipeline {
  agent any

  environment {
    IMAGE_NAME     = "flask-server"
    IMAGE_TAG      = "${env.BUILD_NUMBER ?: 'local'}"
    CONTAINER_NAME = "flask-server-container"
  }

  parameters {
    string(name: 'GITHUB_REPO', defaultValue: 'https://github.com/LowLevelLore/MLOPs---Iris.git', description: 'HTTPS URL of the GitHub repo to checkout')
    string(name: 'GIT_BRANCH', defaultValue: 'main', description: 'Branch to checkout')
    string(name: 'GHCR_OWNER', defaultValue: 'LowLevelLore', description: 'GHCR owner (org or username)')
  }

  stages {
    stage('Checkout Code') {
      steps {
        script {
          def gitCredsId = '' 
          if (gitCredsId?.trim()) {
            checkout([
              $class: 'GitSCM',
              branches: [[name: params.GIT_BRANCH]],
              userRemoteConfigs: [[url: params.GITHUB_REPO, credentialsId: gitCredsId]]
            ])
          } else {
            git branch: params.GIT_BRANCH, url: params.GITHUB_REPO
          }
        }
      }
    }

    stage('Load project from workspace') {
      steps {
        script {
          if (isUnix()) {
            sh 'ls -la'
          } else {
            bat 'dir'
          }
        }
      }
    }

    stage('Build & Tag Image') {
      steps {
        script {
          env.FULL_IMAGE = "ghcr.io/${params.GHCR_OWNER}/${env.IMAGE_NAME}:${env.IMAGE_TAG}"
          echo "Building Docker image: ${env.FULL_IMAGE}"
          def built = docker.build("${env.FULL_IMAGE}", ".")
          env.BUILT_IMAGE = built.id
        }
      }
    }

    stage('Run Tests inside Image') {
      steps {
        script {
          echo "Running tests inside image ${env.FULL_IMAGE}"
          docker.image("${env.FULL_IMAGE}").inside("--rm") {
            if (isUnix()) {
              sh 'pytest -q || { echo "Tests failed"; exit 1; }'
            } else {
              bat 'pytest -q'
            }
          }
        }
      }
      post {
        failure {
          echo "Tests failed — build will be marked FAILED"
        }
      }
    }

    stage('Login & Push to GHCR') {
      steps {
        script {
          def ghcrCredsId = 'ghcr-creds'
          if (!ghcrCredsId?.trim()) {
            error("GHCR credentials id not configured. Create credential 'ghcr-creds' in Jenkins.")
          }
          docker.withRegistry('https://ghcr.io', ghcrCredsId) {
            def img = docker.image("${env.FULL_IMAGE}")
            echo "Pushing image ${env.FULL_IMAGE} to GHCR..."
            img.push()
          }
        }
      }
    }
  }

  post {
    success {
      echo "Pipeline succeeded. ${env.FULL_IMAGE} pushed to ghcr.io."
    }
    failure {
      echo "Pipeline failed."
    }
    cleanup {
      echo "Optional: perform cleanup if you want to prune old images/containers"
    }
  }
}

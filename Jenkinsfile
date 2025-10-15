pipeline {
  agent any

  environment {
    IMAGE_NAME     = "flask-server"
    IMAGE_TAG      = "${env.BUILD_NUMBER ?: 'local'}"
    CONTAINER_NAME = "flask-server-container"
  }

  parameters {
    string(name: 'GITHUB_REPO', defaultValue: 'https://github.com/LowLevelLore/MLOPs---Iris.git')
    string(name: 'GIT_BRANCH', defaultValue: 'main')
    string(name: 'GHCR_OWNER', defaultValue: 'LowLevelLore')
  }

  stages {
    stage('Checkout') {
      steps {
        script {
          git branch: params.GIT_BRANCH, url: params.GITHUB_REPO
        }
      }
    }

    stage('Build Image (CLI)') {
      steps {
        script {
          env.FULL_IMAGE = "ghcr.io/${params.GHCR_OWNER}/${env.IMAGE_NAME}:${env.IMAGE_TAG}"
          if (isUnix()) {
            sh """
              echo "Building ${env.FULL_IMAGE}"
              docker build -t ${env.FULL_IMAGE} .
            """
          } else {
            bat """
              echo Building ${env.FULL_IMAGE}
              docker build -t ${env.FULL_IMAGE} .
            """
          }
        }
      }
    }

    stage('Run Tests inside Image (CLI)') {
      steps {
        script {
          if (isUnix()) {
            sh """
              set -e
              echo "Running tests inside container"
              docker run --rm ${env.FULL_IMAGE} pytest -q
            """
          } else {
            bat """
              @echo off
              echo Running tests inside container
              docker run --rm ${env.FULL_IMAGE} pytest -q
            """
          }
        }
      }
      post {
        failure {
          echo "Tests failed — failing the build"
        }
      }
    }

    stage('Login & Push to GHCR (withCredentials)') {
      steps {
        withCredentials([string(credentialsId: 'ghcr-pat', variable: 'GHCR_PAT')]) {
          script {
            if (isUnix()) {
              sh """
                echo "${GHCR_PAT}" | docker login ghcr.io --username ${params.GHCR_OWNER} --password-stdin
                docker push ${env.FULL_IMAGE}
              """
            } else {
              bat """
                @echo off
                echo ${GHCR_PAT} | docker login ghcr.io --username ${params.GHCR_OWNER} --password-stdin
                docker push ${env.FULL_IMAGE}
              """
            }
          }
        }
      }
    }
  }

  post {
    success { echo "Pipeline succeeded: ${env.FULL_IMAGE} pushed and (optionally) deployed." }
    failure { echo "Pipeline failed." }
  }
}

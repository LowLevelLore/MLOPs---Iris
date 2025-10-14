pipeline {
  agent any

  environment {
    IMAGE_NAME     = "flask-server"
    IMAGE_TAG      = "${env.BUILD_NUMBER ?: 'local'}"
    CONTAINER_NAME = "flask-server-container"
  }

  stages {

    stage('Checkout Code') {
        steps {
            git branch: 'main', url: 'file:///D:/MLOPs%20-%20Iris'
        }
    }

    stage('Load project from local folder') {
      steps {
        script {
          if (isUnix()) {
            sh '''ls -la'''
          } else {
            bat """dir"""
          }
        }
      }
    }

    stage('Build Image') {
      steps {
        script {
          if (isUnix()) {
            sh """
              echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
              docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
            """
          } else {
            bat """
              echo Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}
              docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
            """
          }
        }
      }
    }

    stage('Run Tests') {
      steps {
        script {
          if (isUnix()) {
            sh """
              set -e
              echo "Running tests inside container"
              docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} pytest -q
            """
          } else {
            bat """
              @echo off
              echo Running tests inside container
              docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} pytest -q
            """
          }
        }
      }
      post {
        failure {
          echo "Tests failed — build will be marked FAILED"
        }
      }
    }

    stage('Deploy') {
      steps {
        script {
          if (isUnix()) {
            sh """
              set -e
              echo "Deploying ${IMAGE_NAME}:${IMAGE_TAG} -> docker run -p 5000:5000"
              if docker ps -a --format '{{.Names}}' | grep -w ${CONTAINER_NAME} >/dev/null 2>&1; then
                echo "Stopping existing container ${CONTAINER_NAME}"
                docker stop ${CONTAINER_NAME} || true
                docker rm ${CONTAINER_NAME} || true
              fi
              docker run -d --name ${CONTAINER_NAME} -p 5000:5000 ${IMAGE_NAME}:${IMAGE_TAG}
            """
          } else {
            bat """
              @echo off
              echo Deploying ${IMAGE_NAME}:${IMAGE_TAG} -> docker run -p 5000:5000
              docker run -d --name ${CONTAINER_NAME} -p 5000:5000 ${IMAGE_NAME}:${IMAGE_TAG}
            """
          }
        }
      }
    }
  }

  post {
    success {
      echo "Pipeline succeeded. ${IMAGE_NAME}:${IMAGE_TAG} deployed on port 5000."
    }
    failure {
      echo "Pipeline failed."
    }
    cleanup {
      echo "Optional: perform cleanup if you want to prune old images/containers"
    }
  }
}

pipeline {
    agent any

    environment {
        AWS_REGION = "us-west-2"
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Package Lambda') {
            steps {
                sh '''
                cd src
                zip -r ../lambda.zip .
                '''
            }
        }

        stage('Upload Artifact to S3') {
            steps {
                sh '''
                aws s3 cp lambda.zip s3://bastian-lab-169-3-r-us-west-2.sec.ucsf.edu/lambda/lambda.zip
                '''
            }
        }

        stage('Terraform Init') {
            steps {
                sh '''
                cd infra
                terraform init
                '''
            }
        }

        stage('Terraform Plan') {
            steps {
                sh '''
                cd infra
                terraform plan -out=tfplan
                '''
            }
        }

        stage('Terraform Apply') {
            steps {
                sh '''
                cd infra
                terraform apply -auto-approve tfplan
                '''
            }
        }
    }

    post {
        success {
            echo "Deployment completed successfully."
        }
        failure {
            echo "Deployment failed. Check Jenkins logs."
        }
    }
}

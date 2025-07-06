# 🐳 ECS Flask App with PostgreSQL RDS Backend

This project deploys a containerized Flask app to Amazon ECS Fargate, using Amazon RDS PostgreSQL as a backend database. The app reads from a CSV bundled with the image and inserts one record into the database every 2 minutes.

---

## 🛠️ Architecture Overview

- **App**: Flask + `psycopg2` Python app packaged in Docker
- **Platform**: Amazon ECS Fargate
- **Database**: Amazon RDS for PostgreSQL
- **Verification**: Temporary EC2 instance for DB access inside VPC
- **Logging**: CloudWatch logs via ECS task definition

---

## 🧱 Task Definition (Excerpt - Obfuscated)

```json
{
  "containerDefinitions": [
    {
      "name": "zoo-app",
      "image": "<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/zoo-app:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "hostPort": 5000
        }
      ],
      "environment": [
        { "name": "DB_HOST", "value": "<RDS-ENDPOINT>" },
        { "name": "DB_PORT", "value": "5432" },
        { "name": "DB_NAME", "value": "postgres" },
        { "name": "DB_USER", "value": "postgres" },
        { "name": "DB_PASSWORD", "value": "<REDACTED>" }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/zoo-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "networkMode": "awsvpc",
  "executionRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/ecsTaskExecutionRole"
}
```

---

## 🚀 ECS Service

A basic ECS Fargate service was created using the task definition above. The service:
- Launches a single long-running task
- Pulls the latest image from ECR
- Connects to RDS using the injected environment variables

---

## 🔐 Security Group Configuration

### ✅ RDS: Allow ECS Task to Connect

- Inbound Rule:  
  - Type: `PostgreSQL`
  - Port: `5432`
  - Source: ECS Task's security group (e.g., `sg-xxxxxxxxxxxxxxxxx`)

### ✅ EC2 (for DB verification): Allow SSH + DB Access

- **EC2 SG (temporary instance)**  
  - Inbound Rule:  
    - Type: `SSH`  
    - Port: `22`  
    - Source: `0.0.0.0/0` (for temporary access)

- **RDS SG**  
  - Add a rule to allow port `5432` from the EC2 instance's security group

---

## 🧪 Verifying the Setup with EC2 Jump Box

### 1. Launch EC2

- Choose Amazon Linux 2023
- Use the same VPC and subnet as RDS
- Assign a public IP
- Open SSH (port 22) in its SG

### 2. Connect via SSH or EC2 Instance Connect

```bash
ssh -i ~/your-key.pem ec2-user@<public-ip>
```

Or use Instance Connect from the AWS Console.

### 3. Install PostgreSQL Client

```bash
sudo dnf install postgresql15 -y
```

### 4. Connect to RDS PostgreSQL

```bash
psql -h <rds-endpoint> -U postgres -d postgres
```

> You'll be prompted for the RDS password

### 5. Run SQL to Confirm Records

```sql
\dt
SELECT * FROM animals;
```

You should see rows inserted by your ECS container app.

---

## 📦 Cleanup Notes

- ✅ Terminate the temporary EC2 instance when done
- ✅ Remove the open `0.0.0.0/0` SSH rule
- ✅ Rotate RDS password if needed
- ✅ Disable unnecessary services in your ECS task if no longer needed

---

## 📈 Future Improvements

- 🔐 Use AWS Secrets Manager to inject DB credentials securely
- 🔄 Add a GitHub Actions or CodePipeline workflow to automate deployment
- 📊 Enable ECS Exec for secure in-cluster debugging
- 🛡️ Use VPC endpoints for private SSM, ECR, and CloudWatch access

---

## ✅ Outcome

You now have:
- A secure Flask microservice deployed in ECS
- A PostgreSQL RDS backend
- Secure VPC-only access for internal app and verification
- Verified DB inserts from your containerized app

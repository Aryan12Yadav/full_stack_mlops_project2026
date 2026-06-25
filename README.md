# 🚗 Vehicle Insurance Prediction – Full‑Stack MLOps Project

**Author:** Aryan Yadav

---

## 1️⃣ Project Overview
This repository demonstrates a production‑grade machine‑learning system that predicts whether a customer will purchase vehicle insurance. The solution integrates end‑to‑end data ingestion from MongoDB Atlas, rigorous data validation and transformation, model training, automated model evaluation, model storage in AWS S3, and real‑time inference via a FastAPI web service. All components are containerised and continuously deployed to an AWS EC2 instance using GitHub Actions.

---

## 2️⃣ High‑Level Architecture
```
[MongoDB Atlas] --> [Data Ingestion] --> [Validation] --> [Transformation] -->
[Model Trainer] --> [Model Evaluation] --> [Model Pusher (S3)] -->
[FastAPI Service] --> [End‑User (browser)]
```
The architecture follows a modular, component‑based design. Each stage produces an artifact that is stored under the `artifact/` directory, enabling reproducibility and easy debugging.

---

## 3️⃣ Repository Layout
```
mlopsProject/
├─ .github/
│  └─ workflows/aws.yaml            # CI/CD definition
├─ artifact/                        # Generated artefacts (raw CSV, splits, model, transformer)
├─ logs/                            # Timestamped log files
├─ notebook/                        # Exploration and data‑loading notebooks
│  ├─ mongoDB_demo.ipynb
│  └─ EDA_and_Feature_Engineering.ipynb
├─ src/
│  ├─ components/                  # Individual pipeline stages
│  │  ├─ data_ingestion.py
│  │  ├─ data_validation.py
│  │  ├─ data_transformation.py
│  │  ├─ model_trainer.py
│  │  ├─ model_evaluation.py
│  │  └─ model_pusher.py
│  ├─ configuration/               # Cloud connection helpers
│  │  ├─ mongo_db_connections.py
│  │  └─ aws_connection.py
│  ├─ data_access/                 # Low‑level DB utilities
│  │  └─ proj1_data.py
│  ├─ entity/                      # Typed data classes
│  │  ├─ config_entity.py
│  │  ├─ artifact_entity.py
│  │  └─ s3_estimator.py
│  ├─ pipeline/                    # Orchestrators
│  │  ├─ training_pipeline.py
│  │  └─ prediction_pipeline.py
│  ├─ utils/                       # Helper utilities
│  │  └─ main_utils.py
│  ├─ logger.py
│  └─ exception.py
├─ static/css/style.css
├─ templates/vehicledata.html
├─ app.py                           # FastAPI entry point
├─ demo.py                          # Convenience script to run the full pipeline locally
├─ setup.py                         # setuptools configuration for local package
├─ pyproject.toml                   # Modern build system metadata
├─ requirements.txt                 # Python dependencies
├─ Dockerfile
├─ .dockerignore
├─ .env.example                     # Example environment file (not tracked)
└─ README.md
```
---

## 4️⃣ Step‑by‑Step Development Checklist
### 4.1 Project Bootstrap
1. Execute `template.py` to generate the initial scaffold.
2. Populate `setup.py` and `pyproject.toml` so that the `src` package can be installed locally (see `crashcourse.txt` for details).
3. Create a Conda environment, activate it, and install dependencies:
   ```bash
   conda create -n vehicle python=3.10 -y
   conda activate vehicle
   pip install -r requirements.txt
   pip list | grep src   # verify local package visibility
   ```
### 4.2 MongoDB Atlas Integration
4. Sign up for MongoDB Atlas, create a new project and a free M0 cluster.
5. Add a database user and whitelist IP `0.0.0.0/0`.
6. Retrieve the connection string (Driver: Python, version ≥ 3.6) and store it as `MONGODB_URL`.
7. Create `notebook/mongoDB_demo.ipynb`, load the dataset, and push it to the Atlas collection.
8. Verify the upload via the Atlas UI – data should appear as key‑value documents.
### 4.3 Logging and Exception Handling
9. Implement a structured logger (`src/logger.py`) using `logging` with rotating file handlers.
10. Define a custom exception hierarchy (`src/exception.py`). Test both by running `demo.py`.
11. Document exploratory data analysis and feature engineering in `notebook/EDA_and_Feature_Engineering.ipynb`.
### 4.4 Data Ingestion
12. Add constants to `src/constants/__init__.py` (batch size, collection name, etc.).
13. Implement `src/configuration/mongo_db_connections.py` – a thin wrapper around `pymongo.MongoClient` that reads `MONGODB_URL`.
14. In `src/data_access/proj1_data.py` use the connection helper to paginate through the collection, convert each batch to a Pandas DataFrame, and write the raw CSV to `artifact/raw_data.csv`.
15. Split the data into `train.csv` and `test.csv` under `artifact/`.
### 4.5 Data Validation & Transformation
16. Populate `config/schema.yaml` with the complete dataset schema (column names, types, required fields, columns to drop).
17. Implement `src/components/data_validation.py` – validates the ingested DataFrame against the schema and writes a validation report.
18. Implement `src/components/data_transformation.py` – handles missing values, label‑encodes categoricals, applies SMOTEENN for class imbalance, scales numeric features, and persists a `ColumnTransformer` as `artifact/transformer.pkl`.
### 4.6 Model Training
19. Create `src/components/model_trainer.py` – trains a `RandomForestClassifier`, performs a lightweight grid search over `n_estimators` and `max_depth`, logs the best hyper‑parameters, and saves the trained model as `artifact/model.pkl`.
### 4.7 AWS Setup for Model Registry
20. Log into the AWS console, set the region to **us-east-1**.
21. Create IAM user `firstproj` with *AdministratorAccess* and generate an access‑key pair (download the CSV).
22. Export the credentials as environment variables:
    ```bash
    export AWS_ACCESS_KEY_ID="<your-access-key-id>"
    export AWS_SECRET_ACCESS_KEY="<your-secret-access-key>"
    export AWS_DEFAULT_REGION="us-east-1"
    ```
    Add the same variables to `src/constants/__init__.py` for runtime use.
23. Create an S3 bucket named `my-model-mlopsproj` (region us-east-1, uncheck *Block all public access*).
24. Add the following constants to `src/constants/__init__.py`:
    ```python
    MODEL_EVALUATION_CHANGED_THRESHOLD_SCORE: float = 0.02
    MODEL_BUCKET_NAME = "my-model-mlopsproj"
    MODEL_PUSHER_S3_KEY = "model-registry"
    ```
25. Implement `src/configuration/aws_connection.py` – returns a `boto3` S3 client using the exported credentials.
26. Add `src/aws_storage/s3_estimator.py` (or `src/entity/s3_estimator.py`) with `upload_model`, `download_model`, `upload_transformer`, and `download_transformer` utilities.
### 4.8 Model Evaluation & Pusher
27. `src/components/model_evaluation.py` downloads the current production model from S3, evaluates the newly trained model on the test split, compares accuracy/F1, and promotes the new model only if improvement exceeds `MODEL_EVALUATION_CHANGED_THRESHOLD_SCORE`.
28. `src/components/model_pusher.py` uploads the accepted model and transformer to the bucket under the key defined by `MODEL_PUSHER_S3_KEY`.
### 4.9 Prediction Pipeline & FastAPI Service
29. `src/pipeline/prediction_pipeline.py` loads the latest model and transformer from S3, applies the same preprocessing to incoming request data, and returns a binary prediction.
30. `app.py` exposes two endpoints:
    - `GET /` – renders `templates/vehicledata.html` (a responsive HTML form).
    - `POST /predict` – receives form data, invokes the prediction pipeline, and returns a clear Yes/No response.
31. Store static assets in `static/css/style.css` and reference them in the template.
---

## 5️⃣ Continuous Integration & Continuous Deployment (GitHub Actions)
### 5.1 Continuous Integration (Build & Push Docker Image)
```yaml
name: Deploy Application Docker Image to EC2 instance
on:
  push:
    branches: [main]
jobs:
  Continuous-Integration:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_DEFAULT_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build, tag, and push image to Amazon ECR
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: ${{ secrets.ECR_REPO }}
          IMAGE_TAG: latest
        run: |
          docker build -t "$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" .
          docker push "$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG"
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT
```
### 5.2 Continuous Deployment (Self‑Hosted Runner on EC2)
```yaml
  Continuous-Deployment:
    needs: Continuous-Integration
    runs-on: self-hosted
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_DEFAULT_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Clean old containers (if any)
        run: |
          OLD_CONTAINERS=$(docker ps -q -f "ancestor=${{ steps.login-ecr.outputs.registry }}/${{ secrets.ECR_REPO }}")
          if [ -n "$OLD_CONTAINERS" ]; then
            echo "Stopping old containers..."
            docker stop $OLD_CONTAINERS
            echo "Removing old containers..."
            docker rm $OLD_CONTAINERS
          else
            echo "No old containers found."
          fi

      - name: Run Docker Image to serve users
        run: |
          docker run -d \
            -e AWS_ACCESS_KEY_ID="${{ secrets.AWS_ACCESS_KEY_ID }}" \
            -e AWS_SECRET_ACCESS_KEY="${{ secrets.AWS_SECRET_ACCESS_KEY }}" \
            -e AWS_DEFAULT_REGION="${{ secrets.AWS_DEFAULT_REGION }}" \
            -e MONGODB_URL="${{ secrets.MONGODB_URL }}" \
            -p 5080:5000 \
            "${{ steps.login-ecr.outputs.registry }}/${{ secrets.ECR_REPO }}:latest"
```
> The container is exposed on host port **5080**; update the EC2 security group accordingly.
---

## 6️⃣ Self‑Hosted Runner Setup on EC2
1. Launch an Ubuntu 24.04 t2.medium instance (free‑tier eligible) and open inbound ports **22** (SSH) and **5080** (custom TCP).
2. SSH into the instance (or use EC2 Instance Connect).
3. Install Docker:
   ```bash
   sudo apt-get update -y && sudo apt-get upgrade -y
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   newgrp docker
   ```
4. Follow the GitHub UI to add a self‑hosted runner:
   - Download the runner archive, unzip, and run `./config.sh`.
   - Accept default runner name (`self-hosted`) and labels (`self-hosted`, `Linux`, `X64`).
   - Start the runner with `./run.sh`. It should appear as *idle* in the repository’s Actions > Runners page.
5. To stop/restart the runner, use `Ctrl+C` and re‑run `./run.sh`.
---

## 7️⃣ GitHub Secrets Configuration
Add the following repository secrets (Settings → Secrets & variables → Actions → New repository secret):
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION` (value: `us-east-1`)
- `ECR_REPO` (value: `vehicleproj`)
- `MONGODB_URL` (your Atlas connection string)
---

## 8️⃣ Local Development Workflow
```bash
# After cloning the repo
conda create -n vehicle python=3.10 -y
conda activate vehicle
pip install -r requirements.txt
# Verify package import
python -c "import src; print(src.__version__)"
# Run the FastAPI service locally
python app.py
# Open http://localhost:5000 in a browser
# To execute the full training pipeline locally
python demo.py
# Artefacts will be created under ./artifact/ and logs under ./logs/
```
---

## 9️⃣ Production Access
1. Ensure the EC2 security group allows inbound TCP on **5080** from `0.0.0.0/0`.
2. Open a browser and navigate to:
   `http://<EC2‑PUBLIC‑IP>:5080`
3. The prediction form will be displayed; fill in the customer details and click **Predict**.
4. Model retraining can be triggered via the `/training` route (implemented in `demo.py` or a dedicated FastAPI endpoint).
---

## 🔟 Future Enhancements
- Integrate **Evidently AI** for continuous data‑drift monitoring.
- Schedule automated monthly retraining using a GitHub scheduled workflow or an Airflow DAG.
- Experiment with advanced models (XGBoost, LightGBM, or deep‑learning architectures) for higher predictive performance.
- Replace the static CSS with a modern design framework (Tailwind or Bootstrap) and add interactive visualisations.
- Harden security by rotating IAM credentials automatically and enforcing TLS for all external connections.
---

## 📜 License
This project is released under the MIT License. See the `LICENSE` file for full terms.

---

*End of README*

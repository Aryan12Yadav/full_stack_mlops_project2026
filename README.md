# 🚗 Vehicle Insurance Prediction – Full‑Stack MLOps Project

**Author:** Aryan Yadav

---

## 1️⃣ Introduction
This repository implements a production‑grade machine‑learning solution that predicts whether a customer will purchase vehicle insurance. The system integrates data ingestion from MongoDB Atlas, model training and evaluation, model storage in AWS S3, and a FastAPI web service for real‑time inference. All components are containerised and deployed automatically via GitHub Actions to an AWS EC2 instance.

---

## 2️⃣ Business Context
- **Problem:** Insurance carriers waste resources calling every customer indiscriminately.
- **Goal:** Provide a data‑driven scoring system that ranks customers by the probability of buying vehicle insurance.
- **Impact:** Higher conversion rates, lower acquisition cost, and a repeatable, auditable pipeline for future model upgrades.

---

## 3️⃣ Technical Stack
- **Language:** Python 3.10
- **Web Framework:** FastAPI
- **ML Libraries:** scikit‑learn, pandas, numpy, imbalanced‑learn
- **Database:** MongoDB Atlas (NoSQL, cloud‑hosted)
- **Model Registry:** AWS S3
- **Containerisation:** Docker
- **CI/CD:** GitHub Actions
- **Compute:** AWS EC2 (Ubuntu) running a self‑hosted runner
- **Version Control:** Git
- **Packaging:** setuptools (`setup.py`) and `pyproject.toml`
- **Logging & Monitoring:** Custom logger, log files under `logs/`

---

## 4️⃣ Repository Layout
```
mlopsProject/
├─ .github/
│  └─ workflows/
│     └─ aws.yaml          # CI/CD pipeline definition
├─ artifact/                # Generated at runtime – data splits, models, transforms
├─ logs/                    # Runtime logs with timestamps
├─ notebook/                # Exploratory data analysis and MongoDB demo notebooks
│  ├─ mongoDB_demo.ipynb
│  └─ EDA_and_Feature_Engineering.ipynb
├─ src/                     # Core source package (importable as `src`)
│  ├─ components/          # Individual pipeline stages
│  │  ├─ data_ingestion.py
│  │  ├─ data_validation.py
│  │  ├─ data_transformation.py
│  │  ├─ model_trainer.py
│  │  ├─ model_evaluation.py
│  │  └─ model_pusher.py
│  ├─ configuration/       # Cloud connection helpers
│  │  ├─ aws_connection.py
│  │  └─ mongo_db_connections.py
│  ├─ data_access/         # Low‑level DB access utilities
│  │  └─ proj1_data.py
│  ├─ entity/              # Typed data classes for configs and artifacts
│  │  ├─ config_entity.py
│  │  ├─ artifact_entity.py
│  │  └─ s3_estimator.py
│  └─ pipeline/            # Orchestrators
│     ├─ training_pipeline.py
│     └─ prediction_pipeline.py
├─ static/                  # Web static assets
│  └─ css/style.css
├─ templates/               # Jinja2 HTML templates
│  └─ vehicledata.html
├─ app.py                   # FastAPI entry point
├─ demo.py                  # Manual pipeline runner for debugging
├─ setup.py                 # Package installer for local imports
├─ pyproject.toml           # Modern packaging config
├─ requirements.txt         # Python dependencies
├─ Dockerfile               # Docker image build script
├─ .dockerignore            # Files excluded from Docker context
├─ .env.example            # Example environment file (not tracked)
└─ README.md                # Project documentation (this file)
```

---

## 5️⃣ Data Flow Overview
1. **Ingestion** – Connect to MongoDB Atlas, paginate through the collection, convert JSON to Pandas DataFrame, store raw CSV in `artifact/`.
2. **Validation** – Load `config/schema.yaml`, verify column names, types, and missing‑value constraints.
3. **Transformation** – Impute missing values, encode categoricals, apply SMOTEENN for class imbalance, scale numeric features, persist the transformer pickle.
4. **Training** – Fit a scikit‑learn classifier, tune hyper‑parameters, serialize the trained model to `artifact/`.
5. **Evaluation** – Retrieve the current production model from AWS S3, compute accuracy & F1 on a held‑out test set, decide whether to promote the new model.
6. **Pushing** – Upload the accepted model to the S3 bucket (`my-model-mlopsproj/model-registry`).
7. **Inference** – FastAPI endpoint loads the latest model and transformer, processes incoming form data, returns a binary prediction.

---

## 6️⃣ Detailed Component Description
### 6.1 Data Ingestion (`components/data_ingestion.py`)
- Uses `src.configuration.mongo_db_connections.MongoDBClient`.
- Implements cursor pagination with a configurable `batch_size` (default 10 000).
- Retries on transient network errors (max 3 retries, exponential back‑off).
- Saves the raw dataset as `artifact/raw_data.csv` and splits into `train.csv` / `test.csv`.

### 6.2 Data Validation (`components/data_validation.py`)
- Reads the schema defined in `config/schema.yaml`.
- Checks for missing columns, unexpected data types, and duplicate rows.
- Emits a detailed validation report saved under `artifact/validation_report.txt`.

### 6.3 Data Transformation (`components/data_transformation.py`)
- Handles categorical encoding (`LabelEncoder`), numerical scaling (`StandardScaler`).
- Applies SMOTEENN to balance the target class distribution.
- Persists the `ColumnTransformer` pipeline to `artifact/transformer.pkl` for reuse in inference.

### 6.4 Model Trainer (`components/model_trainer.py`)
- Trains a `RandomForestClassifier` (configurable via `config_entity`).
- Performs a simple grid search over `n_estimators` and `max_depth`.
- Stores the trained model as `artifact/model.pkl`.

### 6.5 Model Evaluation (`components/model_evaluation.py`)
- Downloads the current production model from S3 (`aws_connection.get_s3_client`).
- Calculates `accuracy`, `precision`, `recall`, and `f1_score` on the test split.
- Applies a business‑defined threshold (`MODEL_EVALUATION_CHANGED_THRESHOLD_SCORE = 0.02`).
- Returns a boolean flag indicating promotion eligibility.

### 6.6 Model Pusher (`components/model_pusher.py`)
- Authenticates with AWS using the credentials stored in environment variables.
- Uploads `model.pkl` to the bucket path defined by `MODEL_BUCKET_NAME` and `MODEL_PUSHER_S3_KEY`.
- Updates a `model_version.txt` file in the bucket to keep track of the latest version.

---

## 7️⃣ CI/CD Pipeline (`.github/workflows/aws.yaml`)
### 7.1 Continuous Integration (CI)
- Triggered on pushes to the `main` branch.
- Checks out code, sets up Python 3.10, installs dependencies.
- Logs into AWS using encrypted secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`).
- Builds a Docker image with the command:
  ```
  docker build -t "$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" .
  ```
- Pushes the image to Amazon ECR.

### 7.2 Continuous Deployment (CD)
- Runs on a self‑hosted runner deployed on the EC2 instance.
- Pulls the latest Docker image from ECR.
- Stops any existing container, then starts a fresh container on port 5080:
  ```
  docker run -d -p 5080:5000 \
    -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
    -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
    -e AWS_DEFAULT_REGION="$AWS_DEFAULT_REGION" \
    -e MONGODB_URL="$MONGODB_URL" \
    "$ECR_REGISTRY/$ECR_REPOSITORY:latest"
  ```
- Health‑checks ensure the service is reachable before marking the workflow successful.

---

## 8️⃣ Development Workflow
1. **Clone the repo**
   ```bash
   git clone https://github.com/Aryan12Yadav/full_stack_mlops_project2026.git
   cd mlopsProject
   ```
2. **Create the Conda environment**
   ```bash
   conda create -n vehicle python=3.10 -y
   conda activate vehicle
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set environment variables** (create a `.env` file or export manually):
   ```bash
   export MONGODB_URL="mongodb+srv://<user>:<pwd>@cluster0.mongodb.net/<db>?retryWrites=true&w=majority"
   export AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY"
   export AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_KEY"
   export AWS_DEFAULT_REGION="us-east-1"
   export ECR_REPO="vehicleproj"
   ```
5. **Run the application locally**
   ```bash
   python app.py
   ```
   Open `http://localhost:5000` in a browser.
6. **Execute the full training pipeline** (optional) via `demo.py`:
   ```bash
   python demo.py
   ```
   This will generate artifacts under the `artifact/` directory.

---

## 9️⃣ Jupyter Notebook Workflow (`notebook/`)
- **mongoDB_demo.ipynb** – Demonstrates connection to MongoDB Atlas, data preview, and a quick upload of a CSV dataset.
- **EDA_and_Feature_Engineering.ipynb** – Performs exploratory data analysis, visualises distributions, handles outliers, and prototypes the transformation logic later moved into `components/data_transformation.py`.
- Notebooks are not part of the production runtime but serve as a research sandbox.

---

## 🔐 Logging & Exception Handling
- **logs/** – Each execution creates a timestamped log file (`logs/<YYYYMMDD_HHMMSS>.log`).
- **logger.py** – Centralised logger with rotating file handlers, JSON‑compatible log entries, and optional console output.
- **exception.py** – Custom exception hierarchy (`PipelineException`, `DataIngestionException`, etc.) to surface clear error messages and stack traces.

---

## 📦 Packaging (`setup.py` & `pyproject.toml`)
The project is packaged as a local module named `src` so that internal imports remain clean:
```python
# setup.py (excerpt)
from setuptools import find_packages, setup

setup(
    name="src",
    version="0.0.1",
    author="Aryan Yadav",
    packages=find_packages(),
    install_requires=[],
)
```
`pyproject.toml` declares build‑system requirements (`setuptools>=42`, `wheel`). After installation (`pip install -e .`) the package can be imported anywhere inside the repo:
```python
from src.components.data_ingestion import DataIngestion
```

---

## 📈 Monitoring & Future Enhancements
- **Data Drift Detection** – Integrate Evidently AI to monitor feature distribution changes in production.
- **Automated Retraining** – Schedule a monthly Airflow DAG or a lightweight Cron job that triggers `demo.py`.
- **Advanced Models** – Experiment with XGBoost, LightGBM, or PyTorch neural networks for higher predictive power.
- **Visualization Dashboard** – Build a Streamlit or React dashboard to display live prediction statistics, model performance over time, and data quality metrics.
- **Security Hardening** – Rotate AWS credentials via IAM roles, enforce TLS for MongoDB connections, and add OWASP‑compatible headers to the FastAPI server.

---

## 🛠️ Troubleshooting Guide
- **MongoDB connection errors** – Verify that the IP `0.0.0.0/0` is allowed in Atlas Network Access and that the username/password are correct in `MONGODB_URL`.
- **AWS AccessDenied** – Ensure IAM user has `AmazonS3FullAccess` and `AmazonEC2ContainerRegistryFullAccess`. Delete any compromised keys and generate fresh access keys.
- **Docker build failures** – Confirm Docker daemon is running, and that the `ECR_REGISTRY` environment variable is set before building.
- **Port conflicts** – The container runs on port 5000 inside Docker and maps to host port 5080. Update security‑group inbound rules accordingly.

---

## 📜 License
This repository is released under the MIT License. See the `LICENSE` file for full terms. The code, documentation, and associated assets are the intellectual property of Aryan Yadav.

---

## 🙏 Acknowledgments
- MongoDB Atlas for the free tier database.
- AWS for the free tier EC2 and S3 services.
- The open‑source community (FastAPI, scikit‑learn, pandas, etc.) for providing reliable foundations.
- All mentors and peers who reviewed the code and suggested improvements.

---


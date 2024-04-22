# 1. How to run this Read CV module
## 1.1 Create virtual environment
```
  git clone https://github.com/binhle2001/READ_CV.git
  cd READ_CV
  python -m venv .venv
  source .venv/bin/activate (Unix) or .venv/Scripts/activate (Windows)
  pip install -r requirements.txt
```
## 1.2 Create .env file
```
  [credentials]
  CLIENT_ID=
  PROJECT_ID=
  AUTH_URI=
  TOKEN_URI=
  CLIENT_SECRET=
  
  [gemini]
  API_KEY=
   
  [s3]
  AWS_ACCESS_KEY_ID=
  AWS_SECRET_ACCESS_KEY=
  AWS_REGION_NAME=
  AWS_S3_BUCKET_NAME=
```
## 1.3 Run API
```
  uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
```
# 2. Number of tokens in each CV in the dataset
| Statistic      | Value    |
|----------------|----------|
| Mean           | 1025.67  |
| Median         | 933 |
| Min            | 461  |
| Max            | 3122  |
| Mode           | 1045  |
| Std Deviation  | 377.67 |
## Note: To switch the LLM model for filtering CV information, please refer to file "ai_core/source/reading_cv.py".

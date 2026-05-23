# AI Resume Analyzer

AI Resume Analyzer is a production-ready starter project that compares a candidate resume against a job description using FastAPI, Streamlit, spaCy, and scikit-learn. Uploaded resumes can also be stored in AWS S3.

## Features

- Upload PDF or DOCX resumes
- Extract and clean text
- Accept job description input
- Perform skill extraction, keyword matching, and semantic similarity scoring
- Return a 0-100 match score, missing skills, and improvement suggestions
- Store uploaded files in AWS S3 when credentials are configured

## Project Structure

```text
resume-analyzer/
├── frontend/
│   └── app.py
├── backend/
│   ├── main.py
│   ├── routes/
│   ├── services/
│   └── models/
├── deploy/
│   ├── ec2/
│   └── nginx/
├── utils/
│   └── text_processing.py
├── cloud/
│   └── s3_upload.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Local Setup

1. Create and activate a virtual environment.
   ```bash
   cd resume-analyzer
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   This project supports Python 3.9+, but if you use Python 3.9 you should keep the dependency versions from `requirements.txt` as provided.
2. Install the dependencies.
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
3. Create a `.env` file from `.env.example` and set your AWS details if you want S3 uploads enabled.
4. Start the FastAPI backend.
   ```bash
   uvicorn backend.main:app --reload
   ```
5. In a new terminal, start the Streamlit frontend.
   ```bash
   streamlit run frontend/app.py
   ```
6. Open [http://localhost:8501](http://localhost:8501).

## API Endpoints

- `GET /` - root status
- `GET /api/v1/health` - health check
- `POST /api/v1/upload` - upload a resume to S3
- `POST /api/v1/analyze` - upload a resume and analyze it against a job description

## AWS S3 Configuration

Set these environment variables:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `AWS_S3_BUCKET_NAME`

If `AWS_S3_BUCKET_NAME` is not set, the app still runs locally and skips cloud storage.

## Docker

Build the image:

```bash
docker build -t ai-resume-analyzer .
```

Run the container:

```bash
docker run -p 8000:8000 -p 8501:8501 --env-file .env ai-resume-analyzer
```

## Deploy on AWS EC2

1. Launch an EC2 instance with Ubuntu 22.04+ or Amazon Linux 2023.
2. Attach an IAM role with S3 access if you want the safest AWS auth setup.
3. Open inbound ports:
   - `22` for SSH
   - `80` if you plan to use Nginx
   - `8501` for Streamlit direct access
   - `8000` for FastAPI direct access
4. SSH into the instance and run [deploy/ec2/bootstrap.sh](/Users/parthibanilango/PycharmProjects/File_Compression_Tool/resume-analyzer/deploy/ec2/bootstrap.sh).
   ```bash
   chmod +x deploy/ec2/bootstrap.sh
   ./deploy/ec2/bootstrap.sh
   ```
5. Copy the app to `/opt/ai-resume-analyzer` or clone your repository there.
6. Create `.env` from [deploy/ec2/.env.ec2.example](/Users/parthibanilango/PycharmProjects/File_Compression_Tool/resume-analyzer/deploy/ec2/.env.ec2.example) and update the values.
7. Start the stack.
   ```bash
   cd /opt/ai-resume-analyzer
   docker compose up --build -d
   ```
8. Check logs.
   ```bash
   docker compose logs -f
   ```
9. Open:
   - Frontend: `http://<ec2-public-ip>:8501`
   - API docs: `http://<ec2-public-ip>:8000/docs`

## Optional Nginx Reverse Proxy

If you want to serve the app through port `80`, use [deploy/nginx/resume-analyzer.conf](/Users/parthibanilango/PycharmProjects/File_Compression_Tool/resume-analyzer/deploy/nginx/resume-analyzer.conf).

Example on Ubuntu:

```bash
sudo apt-get install -y nginx
sudo cp deploy/nginx/resume-analyzer.conf /etc/nginx/sites-available/resume-analyzer
sudo ln -s /etc/nginx/sites-available/resume-analyzer /etc/nginx/sites-enabled/resume-analyzer
sudo nginx -t
sudo systemctl restart nginx
```

Then:

- `http://<ec2-public-ip>/` goes to Streamlit
- `http://<ec2-public-ip>/api/` goes to FastAPI

## Deploy on AWS Lambda

AWS Lambda is possible for the FastAPI backend, but this repository is optimized for EC2 deployment because Streamlit is better suited to a long-running server. A common production setup is:

- Deploy FastAPI to Lambda using Mangum and API Gateway
- Keep Streamlit on EC2, ECS, or App Runner
- Continue using S3 for file storage

## Production Notes

- Replace the default open CORS policy using `ALLOWED_ORIGINS`
- Add authentication before exposing the API publicly
- Expand the skill catalog based on your hiring domain
- For persistent analytics, add DynamoDB or RDS as a next step
- Prefer an EC2 IAM role for S3 instead of long-lived AWS access keys in `.env`

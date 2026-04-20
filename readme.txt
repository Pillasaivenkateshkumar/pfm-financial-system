PFM Cloud Project

Overview
This Django application is a personal financial management platform with public demo access, private user accounts, transaction tracking, receipt uploads, CI/CD automation, and optional AWS cloud integrations through the custom cloud_finance_lib package.

Dependencies
- Python 3.11
- pip
- Virtual environment tooling
- AWS credentials and AWS resources only if you want to enable the optional cloud integrations

Python packages
- Install all dependencies with:
  pip install -r requirements.txt

Environment setup
1. Copy .env.example to .env
2. Set DJANGO_SECRET_KEY
3. Keep DEBUG=True for local development
4. Fill PostgreSQL settings if using a cloud-hosted database
5. Set ENABLE_CLOUD_INTEGRATIONS=True only when AWS credentials and resources are ready
6. Fill AWS settings only for the services you want to enable

Run locally
1. Open a terminal in the pfm folder
2. Create a virtual environment:
   python -m venv venv
3. Activate it:
   Windows: venv\Scripts\activate
4. Install packages:
   pip install -r requirements.txt
5. Apply migrations:
   python manage.py migrate
6. Start the app:
   python manage.py runserver
7. Open http://127.0.0.1:8000/

Tests and checks
- python manage.py check
- python manage.py test

Cloud services currently supported in code
- Amazon EC2: deployment target in GitHub Actions CD job
- Amazon S3: transaction audit archive storage
- Amazon S3: optional receipt file storage via Django media backend
- Amazon SNS: high-expense alerts
- Amazon SQS: transaction event queue for downstream processing
- Amazon CloudWatch: custom application metrics
- AWS Systems Manager Parameter Store: runtime threshold configuration
- PostgreSQL or Amazon RDS style database settings: supported through environment variables

Deployment notes
- GitHub Actions workflow: .github/workflows/deploy.yml
- CI runs migrations and tests on pull requests and pushes to main
- CD deploys to EC2 only after CI passes on main
- To store new receipt uploads in S3, install `django-storages`, set `USE_S3_MEDIA_STORAGE=True`, and provide `AWS_S3_MEDIA_BUCKET`

Library packaging
- The reusable library package is cloud_finance_lib
- Packaging metadata is defined in pyproject.toml
- To publish it, build and upload it to your chosen package index from a machine with package publishing credentials

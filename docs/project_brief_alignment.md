# Project Brief Alignment

## What the brief requires
- A complex dynamic cloud-based application deployed on a public cloud URL
- At least five cloud services used programmatically
- A new library you created in an object-oriented language
- Clear functional and non-functional requirements
- Critical architecture analysis
- CI, delivery, and deployment evidence
- Public access to the deployed application

## Current repo status before these changes
- The project was a basic Django CRUD app
- It had local SQLite storage and a single combined deployment workflow
- It did not show five cloud services being used in code
- It did not contain a substantial reusable library package
- It had almost no automated tests
- It lacked submission-oriented documentation

## Changes made to move the project toward the brief
- Added `cloud_finance_lib`, a reusable object-oriented Python package for AWS service integrations
- Integrated programmatic support for S3, SNS, SQS, CloudWatch, and Systems Manager Parameter Store
- Switched Django settings to environment-based configuration for security and deployment flexibility
- Added optional PostgreSQL configuration so the app can target a managed cloud database
- Split CI and CD into separate GitHub Actions jobs
- Added automated tests covering the EUR-only transaction rule and cloud integration workflow
- Added `.env.example`, `readme.txt`, and packaging metadata in `pyproject.toml`
- Added this analysis document to support the report deliverable

## What still requires your real cloud setup
- Public deployment URL
- Actual AWS resources and IAM permissions
- Optional migration from SQLite to a cloud database such as Amazon RDS
- Publishing `cloud_finance_lib` to a package index and including the public URL in the report
- Final report in IEEE format, bibliography, and presentation slides

## Suggested report mapping
- Requirements section: describe transaction management, receipt storage, public demo mode, monitoring, alerts, notifications, secure config, CI/CD
- Architecture section: describe Django app plus AWS services and GitHub Actions pipeline
- Library section: explain `cloud_finance_lib` and include usage snippets from `finance/views.py`
- Cloud services section: critically analyze EC2, S3, SNS, SQS, CloudWatch, SSM, and optional RDS
- CI/CD section: explain separated CI and CD jobs and deployment gating

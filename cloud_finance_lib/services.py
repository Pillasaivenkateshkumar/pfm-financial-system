import json
import logging
import os
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import boto3


logger = logging.getLogger(__name__)


@dataclass
class CloudFeatureSettings:
    enabled: bool = False
    aws_region: str = "eu-west-1"
    audit_bucket: str = ""
    sns_topic_arn: str = ""
    ses_from_email: str = ""
    ses_to_email: str = ""
    cloudwatch_namespace: str = "PFM/Application"
    ssm_parameter_name: str = ""
    expense_alert_threshold: Decimal = Decimal("500.00")

    @classmethod
    def from_env(cls):
        threshold = os.getenv("EXPENSE_ALERT_THRESHOLD", "500.00")
        return cls(
            enabled=os.getenv("ENABLE_CLOUD_INTEGRATIONS", "False").strip().lower() in {"1", "true", "yes", "on"},
            aws_region=os.getenv("AWS_REGION", "eu-west-1"),
            audit_bucket=os.getenv("AWS_S3_AUDIT_BUCKET", ""),
            sns_topic_arn=os.getenv("AWS_SNS_TOPIC_ARN", ""),
            ses_from_email=os.getenv("AWS_SES_FROM_EMAIL", ""),
            ses_to_email=os.getenv("AWS_FINANCE_ALERT_EMAIL", ""),
            cloudwatch_namespace=os.getenv("AWS_CLOUDWATCH_NAMESPACE", "PFM/Application"),
            ssm_parameter_name=os.getenv("AWS_CONFIG_PARAMETER_NAME", ""),
            expense_alert_threshold=Decimal(str(threshold)),
        )


@dataclass
class TransactionSnapshot:
    transaction_id: int
    user_id: int
    title: str
    amount: Decimal
    currency: str
    type: str
    category: str
    transaction_date: date
    receipt_name: str = ""

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "title": self.title,
            "amount": str(self.amount),
            "currency": self.currency,
            "type": self.type,
            "category": self.category,
            "transaction_date": self.transaction_date.isoformat(),
            "receipt_name": self.receipt_name,
        }


class CloudFinancialPlatform:
    def __init__(self, settings=None, session=None):
        self.settings = settings or CloudFeatureSettings.from_env()
        self.session = session or boto3.session.Session(region_name=self.settings.aws_region)

    def _client(self, service_name):
        return self.session.client(service_name)

    def load_runtime_settings(self):
        if not self.settings.enabled:
            return self.settings
        if not self.settings.ssm_parameter_name:
            return self.settings

        try:
            response = self._client("ssm").get_parameter(
                Name=self.settings.ssm_parameter_name,
                WithDecryption=True,
            )
            payload = json.loads(response["Parameter"]["Value"])
            if "expense_alert_threshold" in payload:
                self.settings.expense_alert_threshold = Decimal(str(payload["expense_alert_threshold"]))
        except Exception as exc:
            logger.warning("SSM runtime configuration unavailable: %s", exc)
        return self.settings

    def archive_transaction(self, snapshot):
        if not self.settings.enabled:
            return False
        if not self.settings.audit_bucket:
            return False

        key = f"transactions/{snapshot.user_id}/{snapshot.transaction_id}.json"
        try:
            self._client("s3").put_object(
                Bucket=self.settings.audit_bucket,
                Key=key,
                Body=json.dumps(snapshot.to_dict()).encode("utf-8"),
                ContentType="application/json",
            )
            return True
        except Exception as exc:
            logger.warning("S3 audit archive failed: %s", exc)
            return False

    def publish_metrics(self, snapshot):
        if not self.settings.enabled:
            return False
        try:
            metric_data = [
                {
                    "MetricName": "TransactionsCreated",
                    "Unit": "Count",
                    "Value": 1,
                    "Dimensions": [
                        {"Name": "TransactionType", "Value": snapshot.type},
                        {"Name": "Currency", "Value": snapshot.currency},
                    ],
                },
                {
                    "MetricName": "TransactionAmount",
                    "Unit": "None",
                    "Value": float(snapshot.amount),
                    "Dimensions": [
                        {"Name": "TransactionType", "Value": snapshot.type},
                        {"Name": "Category", "Value": snapshot.category},
                    ],
                },
            ]
            self._client("cloudwatch").put_metric_data(
                Namespace=self.settings.cloudwatch_namespace,
                MetricData=metric_data,
            )
            return True
        except Exception as exc:
            logger.warning("CloudWatch metrics failed: %s", exc)
            return False

    def publish_expense_alert(self, snapshot):
        if not self.settings.enabled:
            return False
        if snapshot.type != "expense":
            return False
        if not self.settings.sns_topic_arn:
            return False
        if snapshot.amount < self.settings.expense_alert_threshold:
            return False

        message = (
            f"Expense alert for user {snapshot.user_id}: "
            f"{snapshot.title} cost {snapshot.amount} {snapshot.currency} "
            f"in category {snapshot.category}."
        )
        try:
            self._client("sns").publish(
                TopicArn=self.settings.sns_topic_arn,
                Subject="PFM expense alert",
                Message=message,
            )
            return True
        except Exception as exc:
            logger.warning("SNS alert failed: %s", exc)
            return False

    def send_email_notification(self, snapshot):
        if not self.settings.enabled:
            return False
        if not self.settings.ses_from_email or not self.settings.ses_to_email:
            return False

        subject = "PFM transaction notification"
        body = (
            f"Transaction saved:\n\n"
            f"Title: {snapshot.title}\n"
            f"Amount: {snapshot.amount} {snapshot.currency}\n"
            f"Type: {snapshot.type}\n"
            f"Category: {snapshot.category}\n"
            f"Date: {snapshot.transaction_date.isoformat()}\n"
        )

        try:
            self._client("ses").send_email(
                Source=self.settings.ses_from_email,
                Destination={"ToAddresses": [self.settings.ses_to_email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": body}},
                },
            )
            return True
        except Exception as exc:
            logger.warning("SES notification failed: %s", exc)
            return False

    def process_transaction(self, snapshot):
        self.load_runtime_settings()
        return {
            "ssm_loaded": self.settings.enabled and bool(self.settings.ssm_parameter_name),
            "archived_to_s3": self.archive_transaction(snapshot),
            "metrics_published": self.publish_metrics(snapshot),
            "sns_alert_sent": self.publish_expense_alert(snapshot),
            "ses_email_sent": self.send_email_notification(snapshot),
        }

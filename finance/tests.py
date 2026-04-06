from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase

from cloud_finance_lib import CloudFeatureSettings, CloudFinancialPlatform, TransactionSnapshot
from finance.forms import TransactionForm


class TransactionFormTests(TestCase):
    def test_currency_field_is_not_exposed_on_form(self):
        form = TransactionForm()
        self.assertNotIn("currency", form.fields)

    def test_transaction_form_always_saves_in_eur(self):
        form = TransactionForm(
            data={
                "title": "Salary",
                "amount": "900.00",
                "type": "income",
                "category": "Work",
                "date": "2026-04-06",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        transaction = form.save(commit=False)
        self.assertEqual(transaction.currency, "EUR")


class CloudFinancialPlatformTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="secret123")
        self.snapshot = TransactionSnapshot(
            transaction_id=1,
            user_id=self.user.id,
            title="Laptop",
            amount=Decimal("1200.00"),
            currency="EUR",
            type="expense",
            category="Equipment",
            transaction_date=date(2026, 4, 6),
            receipt_name="receipts/laptop.pdf",
        )

    @patch("cloud_finance_lib.services.boto3.session.Session")
    def test_cloud_workflow_calls_enabled_services(self, session_cls):
        session = MagicMock()
        session_cls.return_value = session

        ssm_client = MagicMock()
        ssm_client.get_parameter.return_value = {
            "Parameter": {"Value": '{"expense_alert_threshold": 1000}'}
        }
        s3_client = MagicMock()
        sns_client = MagicMock()
        sqs_client = MagicMock()
        cloudwatch_client = MagicMock()

        def client_factory(service_name):
            return {
                "ssm": ssm_client,
                "s3": s3_client,
                "sns": sns_client,
                "sqs": sqs_client,
                "cloudwatch": cloudwatch_client,
            }[service_name]

        session.client.side_effect = client_factory

        service = CloudFinancialPlatform(
            settings=CloudFeatureSettings(
                enabled=True,
                audit_bucket="audit-bucket",
                sns_topic_arn="arn:aws:sns:eu-west-1:123456789012:pfm-alerts",
                sqs_queue_url="https://sqs.eu-west-1.amazonaws.com/123456789012/pfm-events",
                ssm_parameter_name="/pfm/runtime-config",
            ),
            session=session,
        )

        result = service.process_transaction(self.snapshot)

        self.assertTrue(result["archived_to_s3"])
        self.assertTrue(result["metrics_published"])
        self.assertTrue(result["sns_alert_sent"])
        self.assertTrue(result["sqs_event_sent"])
        s3_client.put_object.assert_called_once()
        sns_client.publish.assert_called_once()
        sqs_client.send_message.assert_called_once()
        cloudwatch_client.put_metric_data.assert_called_once()

    @patch("cloud_finance_lib.services.boto3.session.Session")
    def test_cloud_workflow_gracefully_skips_optional_services(self, session_cls):
        session = MagicMock()
        session_cls.return_value = session
        session.client.return_value = MagicMock()

        service = CloudFinancialPlatform(
            settings=CloudFeatureSettings(),
            session=session,
        )

        result = service.process_transaction(self.snapshot)

        self.assertFalse(result["archived_to_s3"])
        self.assertFalse(result["metrics_published"])
        self.assertFalse(result["sns_alert_sent"])
        self.assertFalse(result["sqs_event_sent"])

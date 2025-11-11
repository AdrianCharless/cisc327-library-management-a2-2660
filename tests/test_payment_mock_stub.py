import pytest
from unittest.mock import Mock
pytest_plugins = ("pytest_mock",)

import services.library_service as library_service
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway

#  pay_late_fees tests

def test_pay_late_fees_success(mocker): 
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 2.5, "days_overdue":5, "status": "Book was returned 5 days late and will cost $2.5 as a late fee, Thank you!"},)
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 123, "title": "The Great Gatsby"},)

    payment_gateway_mock = Mock(spec=PaymentGateway)
    payment_gateway_mock.process_payment.return_value = (True, "txn_123456_1731170802", "Payment of $2.50 processed successfully")

    success, message, transaction_id = pay_late_fees("123456", 123, payment_gateway_mock)
    assert success is True
    assert transaction_id == "txn_123456_1731170802"
    assert "payment of $2.50 processed successfully" in message.lower()

    payment_gateway_mock.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=2.50,
        description="Late fees for 'The Great Gatsby'",
    )

def test_pay_late_fees_payment_declined_by_gateway(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 2.5, "days_overdue":5, "status": "Book was returned 5 days late and will cost $2.5 as a late fee, Thank you!"},)
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 123, "title": "The Great Gatsby"},)

    payment_gateway_mock = Mock(spec=PaymentGateway)
    payment_gateway_mock.process_payment.return_value = (False, "", "Payment declined: amount exceeds limit")

    success, message, transaction_id = pay_late_fees("123456", 123, payment_gateway_mock)
    assert success is False
    assert transaction_id is None
    assert "payment failed: payment declined: amount exceeds limit" in message.lower()

    payment_gateway_mock.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=2.50,
        description="Late fees for 'The Great Gatsby'",
    )

def test_pay_late_fees_invalid_patron_id():
    payment_gateway_mock = Mock(spec=PaymentGateway)

    success, message, transaction_id = pay_late_fees("789", 123, payment_gateway_mock)
    assert success is False
    assert transaction_id is None
    assert "invalid patron id. must be exactly 6 digits." in message.lower()

    payment_gateway_mock.process_payment.assert_not_called()

def test_pay_late_fees_zero_late_fee(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 0.0, "days_overdue": 0, "status": "Book was returned on time and will have no late fee, Thank you!"},)
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 123, "title": "The Great Gatsby"},)

    payment_gateway_mock = Mock(spec=PaymentGateway)

    success, message, transaction_id = pay_late_fees("123456", 123, payment_gateway_mock)
    assert success is False
    assert transaction_id is None
    assert "no late fees to pay for this book." in message.lower()

    payment_gateway_mock.process_payment.assert_not_called()


def test_pay_late_fees_network_error(mocker):
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 2.5, "days_overdue":5, "status": "Book was returned 5 days late and will cost $2.5 as a late fee, Thank you!"},)
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 123, "title": "The Great Gatsby"},)

    payment_gateway_mock = Mock(spec=PaymentGateway)
    payment_gateway_mock.process_payment.side_effect = RuntimeError("gateway down")

    success, message, transaction_id = pay_late_fees("123456", 123, payment_gateway_mock)
    assert success is False
    assert transaction_id is None
    assert "payment processing error: gateway down" in message.lower()

    payment_gateway_mock.process_payment.assert_called_once()

#additional tests for 80% coverage

def test_process_payment_amount_zero_triggers_guard():
    payment_gateway = PaymentGateway()
    success, transaction_id, message = payment_gateway.process_payment(patron_id="123456", amount=0.0, description="0 late fee amount")
    assert success is False
    assert transaction_id == ""
    assert "invalid amount: must be greater than 0" in message.lower()

def test_process_payment_amount_negative_triggers_guard():
    payment_gateway = PaymentGateway()
    success, transaction_id, message = payment_gateway.process_payment(patron_id="123456", amount=-1.0, description="negative late fee amount")
    assert success is False
    assert transaction_id == ""
    assert "invalid amount: must be greater than 0" in message.lower()

# refund_late_fee_payment tests

def test_refund_late_fee_payment_success(mocker):
    payment_gateway_mock = Mock(spec=PaymentGateway)
    payment_gateway_mock.refund_payment.return_value = (True, "Refund of $2.50 processed successfully. Refund ID: refund_txn_123456_1731170802")

    success, message = refund_late_fee_payment("txn_123456_1731170802", 2.50, payment_gateway_mock)
    assert success is True
    assert "refund of $2.50 processed successfully. refund id: refund_txn_123456_1731170802" in message.lower()
    payment_gateway_mock.refund_payment.assert_called_once_with("txn_123456_1731170802", 2.50)

def test_refund_late_fee_payment_invalid_transaction_id(mocker):
    payment_gateway_mock = Mock(spec=PaymentGateway)
    payment_gateway_mock.refund_payment.return_value = (False, "Invalid transaction ID")

    success, message = refund_late_fee_payment("txn_123_1731170802", 2.50, payment_gateway_mock)
    assert success is False
    assert "refund failed: invalid transaction id" in message.lower()
    payment_gateway_mock.refund_payment.assert_called_once_with("txn_123_1731170802", 2.50)

def test_refund_late_fee_payment_negative_refund_amount(mocker):
    payment_gateway_mock = Mock(spec=PaymentGateway)
    payment_gateway_mock.refund_payment.return_value = (False, "Invalid refund amount")

    success, message = refund_late_fee_payment("txn_123456_1731170802", -2.50, payment_gateway_mock)
    assert success is False
    assert "refund amount must be greater than 0." in message.lower()
    payment_gateway_mock.refund_payment.assert_not_called()

def test_refund_late_fee_payment_zero_refund_amount(mocker):
    payment_gateway_mock = Mock(spec=PaymentGateway)
    payment_gateway_mock.refund_payment.return_value = (False, "Invalid refund amount")

    success, message = refund_late_fee_payment("txn_123456_1731170802", 0, payment_gateway_mock)
    assert success is False
    assert "refund amount must be greater than 0." in message.lower()
    payment_gateway_mock.refund_payment.assert_not_called()

def test_refund_late_fee_payment_greater_than_15(mocker):
    payment_gateway_mock = Mock(spec=PaymentGateway)
    payment_gateway_mock.refund_payment.return_value = (True, "Refund of $16.00 processed successfully. Refund ID: refund_txn_123456_1731170802")

    success, message = refund_late_fee_payment("txn_123456_1731170802", 16, payment_gateway_mock)
    assert success is False
    assert "refund amount exceeds maximum late fee." in message.lower()
    payment_gateway_mock.refund_payment.assert_not_called()

def test_refund_late_fees_network_error(mocker):
    payment_gateway_mock = Mock(spec=PaymentGateway)
    payment_gateway_mock.refund_payment.side_effect = RuntimeError("gateway down")

    success, message = refund_late_fee_payment("txn_123456_1731170802", 2.5, payment_gateway_mock)
    assert success is False
    assert "refund processing error: gateway down" in message.lower()

    payment_gateway_mock.process_payment.assert_not_called()

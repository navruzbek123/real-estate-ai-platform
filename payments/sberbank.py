import uuid
import hashlib
from datetime import datetime
from django.conf import settings


class SberbankClient:
    def __init__(self):
        self.merchant_login = getattr(settings, 'SBERBANK_MERCHANT_LOGIN', 'test_merchant')
        self.merchant_password = getattr(settings, 'SBERBANK_MERCHANT_PASSWORD', 'test_password')
        self.is_test = getattr(settings, 'SBERBANK_IS_TEST', True)
        self.return_url = getattr(settings, 'SBERBANK_RETURN_URL', 'http://localhost:8000/payments/success/')

    def _generate_order_id(self):
        return f"ORDER_{uuid.uuid4().hex[:12].upper()}"

    def _generate_signature(self, params):
        values = [
            self.merchant_login,
            params.get('amount', ''),
            params.get('orderId', ''),
            self.merchant_password
        ]
        signature_string = ':'.join(str(v) for v in values)
        return hashlib.md5(signature_string.encode()).hexdigest()

    def create_order(self, amount, description, order_id=None):
        if self.is_test:
            return self._create_mock_order(amount, description, order_id)

        try:
            order_id = order_id or self._generate_order_id()

            params = {
                'userName': self.merchant_login,
                'password': self.merchant_password,
                'orderId': order_id,
                'amount': int(amount * 100),
                'description': description[:100],
                'returnUrl': self.return_url
            }

            params['token'] = self._generate_signature(params)

            payment_url = f"{self.return_url}?orderId={order_id}&status=success"

            return {
                'success': True,
                'order_id': order_id,
                'payment_url': payment_url
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _create_mock_order(self, amount, description, order_id=None):
        order_id = order_id or self._generate_order_id()

        payment_url = f"{self.return_url}?orderId={order_id}&status=success"

        return {
            'success': True,
            'order_id': order_id,
            'payment_url': payment_url,
            'is_mock': True,
            'message': 'Тестовый режим Сбербанка (без реальной оплаты)'
        }

    def get_order_status(self, order_id):
        if self.is_test:
            return {
                'success': True,
                'order_id': order_id,
                'status': 'success',
                'is_mock': True
            }

        return {
            'success': False,
            'error': 'Режим тестирования отключен'
        }

    def refund_order(self, order_id, amount=None):
        if self.is_test:
            return {
                'success': True,
                'order_id': order_id,
                'refund_id': f"REFUND_{uuid.uuid4().hex[:12].upper()}",
                'is_mock': True
            }

        return {
            'success': False,
            'error': 'Режим тестирования отключен'
        }

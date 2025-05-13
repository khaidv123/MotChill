from django.test import TestCase
from django.contrib.auth.models import User
from .models import Benefit, Subscription, UserSubscription

class ModelsTest(TestCase):

    def setUp(self):
        # Create a user instance
        self.user = User.objects.create_user(username='testuser', password='12345')
        # Create a benefit instance
        self.benefit = Benefit.objects.create(name='Free Shipping')
        # Create a subscription instance
        self.subscription = Subscription.objects.create(name='Premium', price=99.99)
        self.subscription.benefits.add(self.benefit)
        # Create a user subscription instance
        self.user_subscription = UserSubscription.objects.create(
            user=self.user,
            subscription=self.subscription,
            start_date='2023-01-01',
            end_date='2023-12-31'
        )

    def test_benefit_creation(self):
        self.assertEqual(self.benefit.name, 'Free Shipping')

    def test_subscription_creation(self):
        self.assertEqual(self.subscription.name, 'Premium')
        self.assertEqual(self.subscription.price, 99.99)
        self.assertIn(self.benefit, self.subscription.benefits.all())
        self.assertEqual(self.subscription.duration_in_days, 30)
        self.assertTrue(self.subscription.is_active)

    def test_user_subscription_creation(self):
        self.assertEqual(self.user_subscription.user, self.user)
        self.assertEqual(self.user_subscription.subscription, self.subscription)
        self.assertEqual(self.user_subscription.start_date, '2023-01-01')
        self.assertEqual(self.user_subscription.end_date, '2023-12-31')

    def test_benefit_str(self):
        self.assertEqual(str(self.benefit), 'Free Shipping')

    def test_subscription_str(self):
        self.assertEqual(str(self.subscription), 'Premium - $99.99')

    def test_user_subscription_str(self):
        self.assertEqual(str(self.user_subscription), 'testuser - Premium')

    def test_subscription_default_values(self):
        subscription = Subscription.objects.create(name='Basic', price=49.99)
        self.assertEqual(subscription.duration_in_days, 30)
        self.assertTrue(subscription.is_active)

    def test_user_subscription_deletion_on_user_delete(self):
        self.user.delete()
        self.assertFalse(UserSubscription.objects.filter(id=self.user_subscription.id).exists())

    def test_user_subscription_deletion_on_subscription_delete(self):
        self.subscription.delete()
        self.assertFalse(UserSubscription.objects.filter(id=self.user_subscription.id).exists())
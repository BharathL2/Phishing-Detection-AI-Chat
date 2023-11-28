import unittest
from src.spam_module.spam_service import SpamService


spam_message = (
    'Congratulations! You’ve won a $500 Amazon gift card. Claim it here.',
    'ACTION REQUIRED. Please verify your Bank of America account information to avoid a hold on your account. Click here to confirm.',
    'Thank you for paying last month’s bill. We’re rewarding our very best customers with a gift for their loyalty. Click here!',
    'Congratulations! Your credit score entitles you to a no-interest Visa credit card. Click here to claim.',
    'We’ve received your resume and would love to set up an online interview. Click here or call us at 987654123 at your earliest convenience.',
    'There’s an issue with your payment information from your recent order 456987. Take action now.',
    'We have detected suspicious activity on your Wells Fargo account. Log in at to update your account preferences and protect your information.',
    'Hi Grandpa, it’s me – I’ve been in a car accident, and my parents aren’t around. Can you please send me money so I can get home? You can wire funds to me here.',
    'Your 2FA settings are not up to date. To avoid account suspension, please click the following link to update your settings.',
    '''Hey, it's Boss Name. I'm in a meeting now and need your help with something urgent. Can you transfer $5,000 to this account ASAP? I'll explain everything later. Please keep this confidential.''',
    'We’re happy to inform you that you’re entitled to a refund for overpayment on your AMEX account. Click on this link  below to claim your refund.',
    '''Congratulations! You have all been selected to receive a free gift card worth $1000. Click on this link to claim your reward now. Limited time offer, so act fast! Don't miss out on this amazing opportunity.''',
)
spam_prediction_expected = [True, True, True, True, False, True, True, False, True, False, True, True]

ham_message = (
    'Hello, how are you? What are you doing today?',
    'Shuffle arrays or sparse matrices in a consistent way.',
    'Split arrays or matrices into random train and test subsets.',
    "I hope you're pleased with yourselves. We could all have been killed — or worse, expelled. Now if you don't mind, I'm going to bed.",
    'It takes a great deal of bravery to stand up to our enemies, but just as much to stand up to our friends.',
    'Different parts of the world have different climates. Some parts of the world are hot and rainy nearly every day.',
)
ham_prediction_expected = [False, False, False, False, False, False]


class Testing(unittest.TestCase):
    def setUp(self):
        self.spam_service_instance = SpamService()

    def test_spam(self):
        prediction = [ self.spam_service_instance.is_spam(message) for message in spam_message]
        self.assertListEqual(spam_prediction_expected, prediction)

    def test_ham(self):
        prediction = [ self.spam_service_instance.is_spam(message) for message in ham_message]
        self.assertListEqual(ham_prediction_expected, prediction)


if __name__ == '__main__':
    unittest.main()



import re
import string
from joblib import load


class SpamService:
    empty_message = 'Empty message!'
    model_path = './src/spam_module/sms-spam-bayes.joblib'

    def __init__(self):
        self.model = load(self.model_path)

    def clean_text(self, text):
        text = str(text).lower()
        text = re.sub('\[.*?\]', '', text)
        text = re.sub('https?://\S+|www\.\S+', '', text)
        text = re.sub('<.*?>+', '', text)
        text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
        text = re.sub('\n', '', text)
        text = re.sub('\w*\d\w*', '', text)
        return text

    def is_spam(self, message):
        if not message:
            raise ValueError(self.empty_message)

        message = self.clean_text(message)
        prediction = self.model.predict([message])

        return True if prediction[0] == 1 else False

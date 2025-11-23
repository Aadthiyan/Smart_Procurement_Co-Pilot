import os
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, SentimentOptions
from dotenv import load_dotenv

load_dotenv('src/config/cloud.env')

class AIService:
    def __init__(self):
        self.nlu_client = None
        
        if os.getenv('NLU_APIKEY') and os.getenv('NLU_URL'):
            try:
                authenticator = IAMAuthenticator(os.getenv('NLU_APIKEY'))
                self.nlu_client = NaturalLanguageUnderstandingV1(
                    version='2022-04-07',
                    authenticator=authenticator
                )
                self.nlu_client.set_service_url(os.getenv('NLU_URL'))
                print("Connected to IBM NLU.")
            except Exception as e:
                print(f"Failed to connect to NLU: {e}")

    def analyze_text(self, text):
        """
        Analyzes text for entities and sentiment using IBM NLU.
        Falls back to simple mock analysis if NLU is not configured.
        """
        if self.nlu_client:
            try:
                response = self.nlu_client.analyze(
                    text=text,
                    features=Features(
                        entities=EntitiesOptions(emotion=True, sentiment=True, limit=2),
                        sentiment=SentimentOptions()
                    )).get_result()
                return response
            except Exception as e:
                print(f"NLU Analysis failed: {e}")
                return self._mock_analysis(text)
        else:
            return self._mock_analysis(text)

    def _mock_analysis(self, text):
        # Simple mock logic
        sentiment = "positive" if "good" in text.lower() or "great" in text.lower() else "neutral"
        if "bad" in text.lower() or "delay" in text.lower():
            sentiment = "negative"
            
        return {
            "sentiment": {"document": {"label": sentiment}},
            "entities": [],
            "mock": True
        }

ai_service = AIService()

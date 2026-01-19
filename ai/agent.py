import json
from django.conf import settings
from django.core import serializers
from google import genai
from google.genai import types
from dotenv import load_dotenv
from ai import prompts, models
from products.models import Product
from outflows.models import Outflow


class SGEAgent:

    def __init__(self): 
        self.__client = genai.Client( 
            api_key=settings.GEMINI_API_KEY, 
        )

    def __get_data(self):
        products = Product.objects.all()
        outflows = Outflow.objects.all()
        return json.dumps({
            'products': serializers.serialize('json', products),
            'outflows': serializers.serialize('json', outflows),
        })

    def invoke(self):
        stream = self.__client.models.generate_content_stream(
            model=settings.GEMINI_MODEL,
            contents=prompts.USER_PROMPT.replace('{{data}}', self.__get_data()),
            config=types.GenerateContentConfig(
                system_instruction=prompts.SYSTEM_PROMPT,
                temperature=0.1,
                top_p=0.8,
            )
        )

        result = []
        for chunk in stream:
            if chunk.text:
                result.append(chunk.text)

        models.AiResult.objects.create(result="".join(result))

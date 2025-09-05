import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Configurar a chave
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Modelos
model = genai.GenerativeModel("gemini-2.5-flash")
# model = genai.GenerativeModel("gemini-2.5-pro")


# Prompt a ser enviado
response = model.generate_content("Me explique crédito consignado em 3 pontos.")
print(response.text)

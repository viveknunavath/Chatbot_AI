from flask import Flask, render_template, request, redirect, url_for, session, make_response
import psycopg2
import datetime
import pandas as pd
import numpy as np
from flask import jsonify
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsRegressor
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
import subprocess
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import time
import traceback

app = Flask(__name__)

app.secret_key = 'welcome'


# Globals to store negotiation state
original_price = 0.0
predicted_price = 0.0
product_name = ''
uname = None

# Friendly template-based responses
friendly_responses = {
    "greeting": lambda: "Hey there!  I'm Nego, your shopping buddy. What can I help you with today?",
    "price": lambda price: f"Absolutely! That item is currently priced at just ${original_price:.2f}. Let me know if you'd like a discount! ",
    "discount": lambda price: f"Let me check... okay, here's a better deal: ${price:.2f}! ",
    "thanks": lambda: "You're very welcome!  Anything else I can do for you?",
    "fallback": lambda: "Hmm, I’m not sure about that yet. But I’m learning every day!"
}

sid = SentimentIntensityAnalyzer()
recognizer = sr.Recognizer()

def get_db_connection():
    return psycopg2.connect(
        host='dpg-d0q4vueuk2gs73a8gdt0-a.oregon-postgres.render.com',
        port=5432,
        database='chatbot_ai_wngz',
        user='chatbot_ai_wngz_user',
        password='IVEU9LsHCVXVwuL154xxv75L3VnueQ85'
    )

@app.route('/ViewReview', methods=['GET'])
def ViewReview():
    table_rows = ""
    try:
        con = get_db_connection()
        with con:
            cur = con.cursor()
            cur.execute("SELECT id, username, review, sentiment FROM reviews")
            rows = cur.fetchall()
            for row in rows:
                table_rows += f"""
                <tr>
                    <td class='px-6 py-4 whitespace-nowrap text-sm text-gray-800'>{row[1]}</td> <!-- username -->
                    <td class='px-6 py-4 whitespace-nowrap text-sm text-gray-600'>{row[2]}</td> <!-- review -->
                    <td class='px-6 py-4 whitespace-nowrap text-sm font-semibold text-indigo-600'>{row[3]}</td> <!-- sentiment -->
                </tr>
                """
    except Exception as e:
        table_rows = f"<tr><td colspan='3' class='text-red-600 p-4'>Error: {str(e)}</td></tr>"

    return render_template('ViewReview.html', msg=table_rows)


@app.route('/ViewOrders', methods=['GET'])
def ViewOrders():
    global uname
    table_rows = ""
    try:
        con = get_db_connection()
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM purchaseorder WHERE username = %s", (uname,))
            rows = cur.fetchall()
            for row in rows:
                table_rows += f"""
                <tr>
                    <td class='px-6 py-4 whitespace-nowrap text-sm text-gray-800'>{row[1]}</td> <!-- username -->
                    <td class='px-6 py-4 whitespace-nowrap text-sm text-gray-800'>{row[2]}</td> <!-- product_id -->
                    <td class='px-6 py-4 whitespace-nowrap text-sm text-gray-800'>{row[3]}</td> <!-- product_name -->
                    <td class='px-6 py-4 whitespace-nowrap text-sm text-green-700 font-semibold'>${row[4]:.2f}</td> <!-- amount -->
                    <td class='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>{row[5]}</td> <!-- transaction_date -->
                </tr>
                """
    except Exception as e:
        table_rows = f"<tr><td colspan='5' class='text-red-600 p-4'>Error: {str(e)}</td></tr>"

    return render_template('ViewOrders.html', msg=table_rows)


@app.route('/CompleteOrder', methods=['POST'])
def CompleteOrder():
    try:
        global uname, product_name, predicted_price

        product_id = request.form.get('t1', '')
        chat_log = request.form.get('chatlog', '')
        if not product_id:
            return render_template('UserScreen.html', msg='Product ID missing.')

        if predicted_price > 0:
            con = get_db_connection()
            cur = con.cursor()
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cur.execute("INSERT INTO purchaseorder(username,product_id,product_name,amount,transaction_date) VALUES(%s,%s,%s,%s,%s)",
                        (session['username'], product_id, product_name, predicted_price, now))
            con.commit()
            return render_template('UserScreen.html', msg='Your order completed')

        return render_template('UserScreen.html', msg='Negotiate first')
    except Exception as e:
        return f"<h3>Error in CompleteOrder: {str(e)}</h3>", 500

        

@app.route('/PostReview', methods=['GET'])
def PostReview():
    return render_template('PostReview.html', msg='')


@app.route('/PostReviewAction', methods=['POST'])
def PostReviewAction():
    global uname
    uname = session.get('username')
    review = request.form.get('t1', '').strip()

    if not review:
        return render_template('PostReview.html', msg="Please enter a review.")

    # Sentiment analysis
    sentiment_dict = sid.polarity_scores(review)
    compound = sentiment_dict['compound']
    
    if compound >= 0.05:
        result = 'Positive'
    elif compound <= -0.05:
        result = 'Negative'
    else:
        result = 'Neutral'

    try:
        con = get_db_connection()
        with con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO reviews (username, review, sentiment) VALUES (%s, %s, %s)",
                (uname, review, result)
            )
            con.commit()  # ✅ This line ensures the insert is saved
            return render_template('PostReview.html', msg=f"Your review was accepted & sentiment predicted: {result}")
    except Exception as e:
        return render_template('PostReview.html', msg=f"Error saving review: {str(e)}")




@app.route('/UserScreen', methods=['GET', 'POST'])
def UserScreen():
    global uname
    if 'username' in session:
        uname = session['username']
        return render_template('UserScreen.html', msg=uname)
    else:
        return redirect(url_for('Auth'))




@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', msg='')


# ✅ Serve the unified login/signup page
@app.route('/Auth', methods=['GET'])
def Auth():
    return render_template('Auth.html')

# ✅ Redirect legacy login/signup URLs to /Auth
@app.route('/Login')
def redirect_login():
    return redirect(url_for('Auth'))

@app.route('/Signup')
def redirect_signup():
    return redirect(url_for('Auth'))



@app.route('/ChatData')
def ChatData():
    global predicted_price
    query = request.args.get('mytext', '').lower()

    if any(greet in query for greet in ["hi", "hello", "hey"]):
        return friendly_responses["greeting"]()

    if "price" in query:
        return friendly_responses["price"](predicted_price)

    if "discount" in query or "final" in query:
        predicted_price *= 0.95  # apply discount
        return friendly_responses["discount"](predicted_price)

    if "thank" in query:
        return friendly_responses["thanks"]()

    return friendly_responses["fallback"]()


import tempfile
import threading
import time

@app.route('/record', methods=['POST'])
def record():
    global predicted_price

    if predicted_price == 0.0:
        return make_response("Please select a product first from Browse Products.", 400)

    try:
        ffmpeg_path = 'ffmpeg'

        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_webm, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:

            temp_webm.write(request.files['data'].read())
            temp_webm.flush()

            subprocess.check_output([ffmpeg_path, "-y", "-i", temp_webm.name, temp_wav.name], stderr=subprocess.STDOUT)

            with sr.AudioFile(temp_wav.name) as source:
                audio = recognizer.record(source)
            try:
               query = recognizer.recognize_google(audio, language="en-IN").strip().lower()
            except sr.UnknownValueError:
               output = "Sorry, I couldn't understand what you said. Could you please repeat that? "
               query = ""


        # Friendly response logic
        if any(word in query for word in ["hi", "hello", "hey"]):
            output = friendly_responses["greeting"]()
        elif "price" in query:
            output = friendly_responses["price"](predicted_price)
        elif any(k in query for k in ['final', 'discount', 'deal']):
            discount = min(predicted_price * 0.05, predicted_price * 0.15)
            predicted_price -= discount
            output = friendly_responses["discount"](predicted_price)
        elif "thank" in query:
            output = friendly_responses["thanks"]()
        else:
            output = friendly_responses["fallback"]()

        # Generate response audio
        audio_dir = os.path.join('static', 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        response_filename = f"response_{int(time.time())}.mp3"
        response_path = os.path.join(audio_dir, response_filename)
        gTTS(output, lang='en').save(response_path)

        os.remove(temp_webm.name)
        os.remove(temp_wav.name)

        def delete_later(path):
            time.sleep(10)
            try:
                os.remove(path)
                print(f"[INFO] Deleted: {path}")
            except Exception as e:
                print(f"[WARN] Failed to delete {path}: {e}")

        threading.Thread(target=delete_later, args=(response_path,)).start()

        return jsonify({
            "query": query,
            "response": output,
            "audio_file": f"/static/audio/{response_filename}"
        })

    except Exception as e:
        traceback.print_exc()
        return make_response(f"Server error: {str(e)}", 500)






@app.route('/Chatbot')
def Chatbot():
    global original_price, predicted_price, product_name
    product_id = request.args.get('t1')
    types = request.args.get('t2')
    
    try:
        df = pd.read_csv(os.path.join('Dataset', 'model_cleaned.csv'))
        df.fillna('', inplace=True)
        row = df.loc[df['index'] == int(product_id)].iloc[0]
    except Exception as e:
        return f"<h3>Error in Chatbot: {str(e)}</h3>", 500

    original_price = float(row['Price'])
    predicted_price = float(row['Negotiate'])
    product_name = row['Name']
    
    output = f"Hi! this is Nego.<br/>Your selected Product : {product_name}.<br/>Its Current Price : ${original_price:.2f}<br/>"
    template = 'Chatbot.html' if types == 'text' else 'VoiceBot.html'
    return render_template(template, msg=output)






@app.route('/BrowseProducts', methods=['GET'])
def BrowseProducts():
    # Path to your CSV file
    csv_path = os.path.join(os.getcwd(), 'Dataset', 'ecommerce.csv')

    if not os.path.exists(csv_path):
        return f"<h3>[ERROR] File not found at path: {csv_path}</h3>", 500

    try:
        df = pd.read_csv(csv_path)
        df.fillna('', inplace=True)  # Replace NaNs with empty strings
    except Exception as e:
        return f"<h3>Failed to load CSV file: {str(e)}</h3>", 500

    # Prepare the products list for the template
    products = []
    for _, row in df.iterrows():
        products.append({
            "id": str(row["index"]),
            "type": row["type"],
            "name": row["name"],
            "description": row["description"],
            "price": row["price"]
        })

    return render_template("BrowseProducts.html", products=products)


    


@app.route('/LoginAction', methods=['POST'])
def LoginAction():
    user = request.form['username'].strip()
    password = request.form['password'].strip()

    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (user, password))
    data = cursor.fetchone()

    if data:
        session['username'] = data[0]
        return redirect(url_for('UserScreen'))
    else:
        return render_template('Auth.html', msg="Invalid login details")

   


@app.route('/SignupAction', methods=['POST'])
def SignupAction():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    
    con = get_db_connection()
    cursor = con.cursor()
    
    try:
        cursor.execute("INSERT INTO users (username, password, emailid) VALUES (%s, %s, %s)", (name, password, email))
        con.commit()
        # Show success message
        return render_template('Auth.html', msg="✅ Account created successfully. Please login.")
    except:
        con.rollback()
        return render_template('Auth.html', msg="❌ Signup failed. User may already exist.")
 
        

@app.route('/AboutUs')
def AboutUs():
    return render_template('AboutUs.html')
       


@app.route('/Logout')
def Logout():
    # Remove user session
    uname = session.pop('username', None)

    # Define the audio folder
    audio_dir = os.path.join('static', 'audio')

    # Delete audio files (.webm, .wav, .mp3)
    if os.path.exists(audio_dir):
        for file in os.listdir(audio_dir):
            if file.endswith(('.webm', '.wav', '.mp3')):
                try:
                    os.remove(os.path.join(audio_dir, file))
                except Exception as e:
                    print(f"Error deleting {file}: {e}")

    # Delete post reviews and orders of the logged-in user
    if uname:
        try:
            con = get_db_connection()
            with con:
                cur = con.cursor()

                # Delete user reviews
                cur.execute("DELETE FROM reviews WHERE username = %s", (uname,))

                # Delete user orders
                cur.execute("DELETE FROM purchaseorder WHERE username = %s", (uname,))

                con.commit()
                print(f"Deleted reviews and orders for user: {uname}")
        except Exception as e:
            print(f"Error deleting user data for {uname}: {e}")

    return render_template('index.html', msg='Logged out successfully!')




@app.route('/')
def home():
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)












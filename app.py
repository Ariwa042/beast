from flask import Flask, request, session, jsonify, render_template, url_for
import requests
import time
import os
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Telegram Bot API token
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '460363720:AAE_1X_Cwm3sJ9RMJFNha04mbzgJ-m8JBys')  # Replace with your actual bot token

# Your private channel ID (with -100 prefix)
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', '6736572379')  # Replace with your actual channel ID

# Ensure the templates folder is correctly set
app.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app.static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

# Log environment variables for debugging
logging.debug(f'TELEGRAM_BOT_TOKEN: {BOT_TOKEN}')
logging.debug(f'TELEGRAM_CHANNEL_ID: {CHANNEL_ID}')

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the participant privacy notice
@app.route('/mrbeast-privacy')
def participant_privacy_notice():
    return render_template('participant-privacy-notice.html')

# Route for the cookie policy
@app.route('/cookie-policy')
def cookie_policy():
    return render_template('cookie-policy.html')

# Route for the privacy policy
@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

# Route for the data protection policy
@app.route('/data-protection-policy')
def data_protection_policy():
    return render_template('data-protection-policy.html')

# Route for form submission
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        first_name = request.form.get('firstName').strip()
        last_name = request.form.get('lastName').strip()
        email = request.form.get('email').strip()
        country = request.form.get('country').strip()
        state = request.form.get('state').strip()
        user_ip = request.remote_addr
        current_time = time.time()

        if not all([first_name, last_name, email, country, state]):
            logging.warning('Form submission failed: All fields are required.')
            return jsonify({"error": "All fields are required."}), 400

        if 'last_submission_time' in session and current_time - session['last_submission_time'] < 3600:
            logging.warning('Form submission failed: Submission limit reached.')
            return jsonify({"error": "You can only submit once per hour."}), 429

        try:
            message = f"First Name: {first_name}\nLast Name: {last_name}\nCountry: {country}\nState: {state}\nEmail: {email}"
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': CHANNEL_ID,
                'text': message
            }
            logging.debug(f'Sending request to Telegram API: {url} with data: {data}')
            response = requests.post(url, data=data)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            response_data = response.json()

            # Log the response for debugging
            with open('telegram_response.log', 'a') as log_file:
                log_file.write(response.text + '\n')

            logging.debug(f'Telegram API response: {response.text}')

            if not response_data.get('ok'):
                raise Exception(f"Failed to send message: {response_data.get('description', 'Unknown error')}")

            session['last_submission_time'] = current_time
            logging.info('Form submission successful.')
            return jsonify({"success": "Application sent successfully!"}), 200
        except requests.exceptions.RequestException as e:
            logging.error(f'Request to Telegram API failed: {e}')
            return jsonify({"error": f'Request to Telegram API failed: {e}'}), 500
        except Exception as e:
            logging.error(f'Error sending message to Telegram: {e}')
            return jsonify({"error": str(e)}), 500
    else:
        logging.warning('Invalid request method.')
        return jsonify({"error": "Invalid request method."}), 405

if __name__ == '__main__':
    app.run(debug=True)

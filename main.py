from flask import Flask, request, jsonify
import requests
import os
import time

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to post comments on Facebook
def post_comment(post_id, comment, access_token):
    url = f"https://graph.facebook.com/{post_id}/comments"
    payload = {"message": comment, "access_token": access_token}
    
    try:
        response = requests.post(url, data=payload)
        response_data = response.json()
        
        if response.status_code == 200:
            return {"status": "success", "response": response_data}
        else:
            return {"status": "error", "response": response_data}

    except requests.exceptions.RequestException as e:
        return {"status": "error", "response": str(e)}

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Comments Tool V2</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Roboto', sans-serif; }
            body {
                background: url('https://i.ibb.co/d4d3rN8j/f153a235c73ce3a8ec00deaa07322986.jpg') no-repeat center center fixed;
                background-size: cover; display: flex; justify-content: center; align-items: center;
                height: 100vh; font-size: 14px; color: #fff; overflow: hidden;
            }
            .container {
                background: rgba(0, 0, 0, 0.7); padding: 30px; border-radius: 15px;
                width: 100%; max-width: 800px; box-shadow: 0 0 20px rgba(0, 0, 0, 0.8);
                backdrop-filter: blur(8px); text-align: center;
            }
            h2 { font-size: 32px; color: #ff7b5f; font-weight: bold; text-transform: uppercase; }
            form { display: flex; flex-direction: column; gap: 15px; }
            label { font-size: 16px; color: #ffd700; font-weight: bold; }
            input, button {
                padding: 12px; font-size: 16px; border-radius: 12px; border: 2px solid #ffd700;
                color: #fff; background-color: #333; transition: all 0.3s ease;
            }
            button {
                background: linear-gradient(90deg, #ff7b5f, #ff6347); font-weight: bold; cursor: pointer;
            }
            button:hover { background: linear-gradient(90deg, #ff6347, #ff7b5f); transform: scale(1.05); }
            .footer p { color: #ff7b5f; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Comments Tool V2</h2>
            <form action="/submit" method="POST" enctype="multipart/form-data">
                <label for="wall_post_id">Wall Post ID:</label>
                <input type="text" id="wall_post_id" name="wall_post_id" required>

                <label for="hater_name">Hater Name:</label>
                <input type="text" id="hater_name" name="hater_name" placeholder="Enter Hater Name (Optional)">

                <label for="access_token">Access Token:</label>
                <input type="text" id="access_token" name="access_token" required>

                <label for="comments_file">Comments File (TXT format):</label>
                <input type="file" id="comments_file" name="comments_file" accept=".txt" required>

                <label for="speed">Speed (Seconds between comments):</label>
                <input type="text" id="speed" name="speed" required>

                <button type="submit">Start Commenting</button>
            </form>
            <div class="footer">
                <p>Tool by ArYan.x3</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/submit', methods=['POST'])
def submit():
    wall_post_id = request.form.get('wall_post_id')
    hater_name = request.form.get('hater_name', '')  # Default to empty string if not provided
    access_token = request.form.get('access_token')
    speed = request.form.get('speed')

    try:
        speed = int(speed)
        if speed < 1:
            return jsonify({"error": "Speed must be at least 1 second."}), 400
    except ValueError:
        return jsonify({"error": "Invalid speed value."}), 400

    comments_file = request.files.get('comments_file')

    if not comments_file or not comments_file.filename.endswith('.txt'):
        return jsonify({"error": "Invalid file type. Only .txt files are allowed."}), 400

    # Save and read comments
    comments_path = os.path.join(app.config['UPLOAD_FOLDER'], comments_file.filename)
    comments_file.save(comments_path)

    with open(comments_path, 'r', encoding='utf-8') as f:
        comments = [line.strip() for line in f.readlines() if line.strip()]

    if not comments:
        return jsonify({"error": "No valid comments found in file."}), 400

    results = []
    for comment in comments:
        if hater_name:
            comment = comment.replace("{hater}", hater_name)  # Replace placeholder if found
        response = post_comment(wall_post_id, comment, access_token)
        results.append(response)
        time.sleep(speed)

    return jsonify({"message": "Comments posted successfully!", "results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  

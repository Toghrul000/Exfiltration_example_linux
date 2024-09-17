from flask import Flask, request, jsonify
import os
import tempfile

app = Flask(__name__)

# We save the collected data to a Temporary folder since this is a demo, 
# of course real attacker would store it somewhere persistent
# Get the Windows and Linux temporary directory using tempfile module
tmp_dir = tempfile.gettempdir()
tmp_file_path = os.path.join(tmp_dir, 'received_data.txt')


# Function to check if the content is the same as the last saved content
def is_duplicate_content(new_content):
    if os.path.exists(tmp_file_path):
        with open(tmp_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if lines:
                last_content = lines[-1].strip()  # Get the last line in the file
                return new_content == last_content
    return False

# Endpoint to receive data from the client
@app.route('/upload', methods=['POST'])
def upload():
    content = request.form.get('content')

    if content:
        # Check for duplicate content
        if is_duplicate_content(content):
            return jsonify({'status': 'error', 'message': 'Duplicate content, not saved'}), 200

        # Print or process the received data
        print("Received data:")
        print(content)

        # Save the data to /tmp folder file if it's not a duplicate
        with open(tmp_file_path, 'a', encoding='utf-8') as file:
            file.write(content + '\n')

        return jsonify({'status': 'success', 'message': 'Data received and saved'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'No data received'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


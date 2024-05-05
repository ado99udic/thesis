from flask import Flask, request, render_template
import subprocess
import os

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Run the web.py script and save the output to a file
        output = subprocess.run(['python', 'web.py'], capture_output=True, text=True).stdout
        output_file = 'output.txt'
        with open(output_file, 'w') as f:
            f.write(output)

        # Read the output file and send it as a response
        formatted_output = ""
        with open(output_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                formatted_output += f"<p>{line}</p>"
        os.remove(output_file)
        return formatted_output

    return render_template('index1.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
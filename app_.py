from flask import Flask, request, render_template
import subprocess
import os

app = Flask(__name__)
app.config["DEBUG"] = True

def format_output_as_table(output):
    lines = output.split('\n')
    data = []
    current_vehicle = {}
    summary = {}
    for line in lines:
        if line.startswith('Route for vehicle'):
            if current_vehicle:
                data.append(current_vehicle)
            current_vehicle = {'Route for vehicle': line.split(' ')[-1]}
        elif line.startswith('0 ->'):
            if 'Route for vehicle' in current_vehicle:
                current_vehicle['Route for vehicle'] += ', ' + line.strip()
            else:
                current_vehicle['Route for vehicle'] = line.strip()
        elif line.startswith('Distance of the route'):
            current_vehicle['Distance of the route'] = line.split(': ')[1]
        elif line.startswith('Maximum of the route distances'):
            summary['Maximum of the route distances'] = line.split(': ')[1]
        elif line.startswith('Distance of all roads'):
            summary['Distance of all roads'] = line.split(': ')[1]
        elif line.startswith('Time taken'):
            summary['Time taken'] = line.split(': ')[1]
    if current_vehicle:
        data.append(current_vehicle)
    
    # Convert the data into an HTML table
    html = '<table>'
    html += '<tr><th>Vehicle</th><th>Route for vehicle</th><th>Distance of the route</th></tr>'
    for vehicle in data:
        html += f'<tr><td>Vehicle {vehicle["Route for vehicle"].split(":")[0]}</td><td>{vehicle["Route for vehicle"].split(":")[1]}</td><td>{vehicle["Distance of the route"]}</td></tr>'
    html += '</table>'
    
    # Add the summary data
    html += f"<p>Maximum of the route distances: {summary.get('Maximum of the route distances', 'N/A')}</p>"
    html += f"<p>Distance of all roads: {summary.get('Distance of all roads', 'N/A')}</p>"
    html += f"<p>Time taken: {summary.get('Time taken', 'N/A')}</p>"
    
    return html

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Run the web.py script and save the output to a file
        output = subprocess.run(['python', 'web.py'], capture_output=True, text=True).stdout
        output_file = 'output.txt'
        with open(output_file, 'w') as f:
            f.write(output)

        # Read the output file and send it as a response
        with open(output_file, 'r') as f:
            output = f.read()
            formatted_output = format_output_as_table(output)
        os.remove(output_file)
        return formatted_output

    return render_template('index1.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
from flask import Flask, render_template, Response
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/plot')
def generate_plot():
    # Generate the Matplotlib graph
    x = [1, 2, 3, 4, 5]
    y = [10, 15, 13, 17, 8]

    plt.bar(x, y)
    plt.xlabel('X-Axis')
    plt.ylabel('Y-Axis')
    plt.title('Dynamically Generated Bar Chart')

    # Save the Matplotlib plot to a BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Encode the plot as base64 for embedding in HTML
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')
    
    return render_template('plot.html', plot_data=plot_data, result = 0)

if __name__ == '__main__':
    app.run(debug=True)
import os
import sys
print("Running on Python version:", sys.version)
import webbrowser
from threading import Timer
from flask import Flask, render_template, request
from model_solver import solve_lp

# Create output directory if not exists (for PyInstaller compatibility)
output_path = os.path.join(os.getcwd(), 'output')
if not os.path.exists(output_path):
    os.makedirs(output_path)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/input', methods=['POST'])
def input_data():
    num_vars = int(request.form['num_vars'])
    num_constraints = int(request.form['num_constraints'])
    return render_template('input.html', num_vars=num_vars, num_constraints=num_constraints)

@app.route('/solve', methods=['POST'])
def solve():
    num_vars = int(request.form['num_vars'])
    num_constraints = int(request.form['num_constraints'])

    c = [float(request.form[f'c{i}']) for i in range(num_vars)]
    A = [[float(request.form[f'a{i}_{j}']) for j in range(num_vars)] for i in range(num_constraints)]
    b = [float(request.form[f'b{i}']) for i in range(num_constraints)]

    result = solve_lp(c, A, b)

    # Construct problem statement
    obj_str = "Maximize Z = " + " + ".join(f"{c[i]}x{i+1}" for i in range(num_vars))
    constraints_str = "\n".join(
        " + ".join(f"{A[i][j]}x{j+1}" for j in range(num_vars)) + f" ≤ {b[i]}"
        for i in range(num_constraints)
    )
    result['problem_statement'] = f"{obj_str}\n\n{constraints_str}"

    return render_template('result.html', result=result)

# Auto-open browser when run as .exe or locally
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=False)






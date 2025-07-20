@app.route('/input', methods=['POST'])
def input_data():
    num_vars = int(request.form['num_vars'])
    num_constraints = int(request.form['num_constraints'])
    return render_template('input.html', num_vars=num_vars, num_constraints=num_constraints)
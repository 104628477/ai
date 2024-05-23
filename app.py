from flask import Flask, request, render_template
import sys
from itertools import product
from inference_engine import parse_input, tt_entails, forward_chaining, backward_chaining

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        content = request.form['content']
        method = request.form['method']
        
        # Save content to a temporary file to parse
        with open('input.txt', 'w') as f:
            f.write(content)
        
        kb, query = parse_input('input.txt')
        
        if method == 'TT':
            res, count = tt_entails(kb, query)
            if res:
                result = f"YES: {count}"
            else:
                result = "NO"
        elif method == 'FC':
            res, known = forward_chaining(kb, query)
            if res:
                result = f"YES: {', '.join(known)}"
            else:
                result = "NO"
        elif method == 'BC':
            res, inferred = backward_chaining(kb, query)
            if res:
                result = f"YES: {', '.join([k for k, v in inferred.items() if v])}"
            else:
                result = "NO"
        else:
            result = f"Unknown method: {method}"
    
    return render_template('engine.html', result=result)

if __name__ == "__main__":
    app.run(debug=True)

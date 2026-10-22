import os
from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable is required.")


BASE_NAMES = {
    2: "Binary",
    8: "Octal",
    10: "Decimal",
    16: "Hexadecimal"
}


def convert_number(number, from_base, to_base):
    decimal_number = int(number, from_base)

    if to_base == 10:
        return str(decimal_number)

    sign = "-" if decimal_number < 0 else ""
    positive_number = abs(decimal_number)

    if to_base == 2:
        result = bin(positive_number)[2:]

    elif to_base == 8:
        result = oct(positive_number)[2:]

    elif to_base == 16:
        result = hex(positive_number)[2:].upper()

    else:
        raise ValueError("Unsupported number system.")

    return sign + result


@app.route('/')
def home():
    return render_template(
        'index.html',
        result=None,
        error=None,
        number="",
        from_base=10,
        to_base=2,
        history=session.get('history', [])
    )


@app.route('/convert', methods=['POST'])
def convert():
    number = request.form.get('number', '').strip()
    result = None
    error = None

    try:
        from_base = int(request.form.get('from_base', 10))
        to_base = int(request.form.get('to_base', 2))

        if from_base not in BASE_NAMES or to_base not in BASE_NAMES:
            raise ValueError("Unsupported number system.")

        if not number:
            raise ValueError("Please enter a number.")

        result = convert_number(number, from_base, to_base)

        history = session.get('history', [])

        history.insert(0, {
            'number': number,
            'from_name': BASE_NAMES[from_base],
            'to_name': BASE_NAMES[to_base],
            'result': result,
            'time': datetime.now().strftime('%I:%M %p')
        })

        session['history'] = history[:10]

    except ValueError:
        error = "Invalid number for the selected number system."

    return render_template(
        'index.html',
        result=result,
        error=error,
        number=number,
        from_base=from_base if from_base in BASE_NAMES else 10,
        to_base=to_base if to_base in BASE_NAMES else 2,
        history=session.get('history', [])
    )


@app.route('/clear-history', methods=['POST'])
def clear_history():
    session.pop('history', None)
    return render_template(
        'index.html',
        result=None,
        error=None,
        number="",
        from_base=10,
        to_base=2,
        history=[]
    )


if __name__ == '__main__':
    app.run(debug=True)

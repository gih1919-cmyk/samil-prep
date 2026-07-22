from flask import Flask, request

app = Flask(__name__)

# 신뢰수준별 신뢰계수 (감사 실무 표준표)
RELIABILITY_FACTORS = {
    "70": 1.2,
    "80": 1.6,
    "90": 2.3,
    "95": 3.0,
    "97.5": 3.7,
    "99": 4.6,
}

@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        population = float(request.form["population"])
        tolerable = float(request.form["tolerable"])
        expected = float(request.form["expected"])
        confidence = request.form["confidence"]

        if tolerable <= expected:
            result = "오류: 허용오류는 예상오류보다 커야 합니다."
        else:
            factor = RELIABILITY_FACTORS[confidence]
            sample_size = (population * factor) / (tolerable - expected)
            result = f"{round(sample_size)}개"

    page = f"""
    <html>
    <head>
        <title>감사 표본크기 계산기</title>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; background-color: #f4f6f8; padding: 40px; max-width: 500px; margin: auto; }}
            h1 {{ color: #2c3e50; }}
            label {{ display: block; margin-top: 15px; font-weight: bold; }}
            input, select {{ width: 100%; padding: 8px; margin-top: 5px; box-sizing: border-box; }}
            button {{ margin-top: 20px; padding: 10px 20px; background-color: #2c3e50; color: white; border: none; cursor: pointer; }}
            .result {{ margin-top: 30px; padding: 20px; background-color: #eafaf1; border-radius: 5px; font-size: 18px; }}
        </style>
    </head>
    <body>
        <h1>📋 감사 표본크기 계산기</h1>
        <form method="post">
            <label>모집단 장부금액 (원)</label>
            <input type="number" name="population" required>

            <label>허용오류(중요성 금액, 원)</label>
            <input type="number" name="tolerable" required>

            <label>예상오류 (원, 없으면 0)</label>
            <input type="number" name="expected" value="0" required>

            <label>신뢰수준 (%)</label>
            <select name="confidence">
                <option value="70">70%</option>
                <option value="80">80%</option>
                <option value="90">90%</option>
                <option value="95" selected>95%</option>
                <option value="97.5">97.5%</option>
                <option value="99">99%</option>
            </select>

            <button type="submit">계산하기</button>
        </form>

       {'<div class="result">' + str(result) + '</div>' if result else ''}
    </body>
    </html>
    """
    return page

if __name__ == "__main__":
    app.run(debug=True, port=5001)
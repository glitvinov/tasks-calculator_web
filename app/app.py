from flask import Flask, render_template, request, make_response, session, redirect, url_for
from flask_session import Session
import random
import redis

app = Flask(__name__)
redis_client = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=True)

# Настройка сессии
app.config['SESSION_TYPE'] = 'filesystem'  # Используем файловую систему для хранения сессий
app.config['SESSION_PERMANENT'] = False  # Сессия не сохраняется между запросами
Session(app)

SECRET_TEXT = "123123123"
complexity = 3

# Генерация случайного математического примера
def generate_math_problem_old():
    num1 = random.randint(1, 100)
    num2 = random.randint(1, 100)
    operator = random.choice(['+', '-'])
    if operator == '+':
        result = num1 + num2
    elif operator == '-':
        result = num1 - num2
    elif operator == '*':
        result = num1 * num2
    else:
        result = round(num1 / num2, 2)
    return f"{num1} {operator} {num2} =", result

def generate_math_problem():
    operators = ['+', '-', '*']
    operands = [random.randint(1, 100) for _ in range(complexity)]

    random_operators = [random.choice(operators) for _ in range((complexity-1))]
    problem_parts = []
    for i in range((complexity-1)):
        problem_parts.extend([operands[i], random_operators[i]])
    problem_parts.append(operands[(complexity-1)])
    
    result = eval(' '.join(map(str, problem_parts)))
    math_problem = ' '.join(map(str, problem_parts))
    return math_problem, result

# Главная страница
@app.route('/', methods=['GET', 'POST'])
def index():
    math_problem, answer = generate_math_problem()
    score = session.get('score', 0)
    visited = session.get('visited', 0)
    session['visited'] = 1


    if request.method == 'POST':
        user_answer = request.form.get('answer')
        if user_answer is not None:
            try:
                user_answer = int(user_answer)
                correct_answer = redis_client.get('correct_answer')
                if user_answer == int(correct_answer):
                    score += 1
                else:
                    score -= 10
            except ValueError:
                score -= 10
            session['score'] = score

    redis_client.set('correct_answer', answer)
    if score > 10000:
        math_problem += "  " + SECRET_TEXT
    resp = make_response(render_template('index.html', math_problem=math_problem, score=score, visited=visited))
    return resp


@app.route('/reset', methods=['POST'])
def reset_score():
    session['score'] = 0
    session['visited'] = 0
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
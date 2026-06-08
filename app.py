from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import random
import string
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'efm_secret_key_fima_1456'

# ===== ХРАНИЛИЩА =====
orders_db = {}
closed_orders = {}
reviews_db = []

PRICES = {'1 час': 1000, '2 часа': 2000}

def generate_order_number():
    return ''.join(random.choices(string.digits, k=8))

# ===== ГЛАВНАЯ =====
HTML_MAIN = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EFMConsult | Компьютерные консультации</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,600;14..32,700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.5; }
        .container { max-width: 1280px; margin: 0 auto; padding: 0 24px; }
        .header { background: white; border-bottom: 1px solid #e2e8f0; padding: 20px 0; position: sticky; top: 0; z-index: 10; background: rgba(255,255,255,0.95); backdrop-filter: blur(8px); }
        .header-inner { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; }
        .logo h1 { font-size: 1.8rem; font-weight: 700; background: linear-gradient(135deg, #1e4a42, #0b2b26); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .logo p { font-size: 0.8rem; color: #5b6e8c; }
        .nav a { margin-left: 28px; text-decoration: none; color: #334155; font-weight: 500; transition: 0.2s; }
        .nav a:hover { color: #1e4a42; }
        
        .hero { background: linear-gradient(135deg, #e6f7f3 0%, #d1ede6 100%); border-radius: 48px; margin: 48px 0; padding: 64px 56px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 40px; }
        .hero-content h2 { font-size: 3rem; font-weight: 700; line-height: 1.2; margin-bottom: 20px; color: #0b2b26; }
        .hero-content p { font-size: 1.2rem; color: #2d4a45; margin-bottom: 32px; max-width: 550px; }
        .hero-stats { display: flex; gap: 32px; margin-top: 24px; }
        .stat h3 { font-size: 1.8rem; font-weight: 700; color: #1e4a42; }
        .stat p { font-size: 0.9rem; color: #5b6e8c; }
        .hero-image { background: rgba(30,74,66,0.1); border-radius: 32px; padding: 20px 32px; font-size: 5rem; text-align: center; }
        
        .pricing { margin: 80px 0; text-align: center; }
        .section-title { font-size: 2rem; font-weight: 700; margin-bottom: 16px; }
        .section-sub { color: #5b6e8c; margin-bottom: 48px; }
        .price-grid { display: flex; justify-content: center; gap: 32px; flex-wrap: wrap; }
        .price-card { background: white; border-radius: 32px; padding: 32px; width: 300px; box-shadow: 0 20px 35px -10px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; transition: 0.2s; }
        .price-card:hover { transform: translateY(-5px); border-color: #b8e1d8; }
        .price-card h3 { font-size: 1.8rem; margin-bottom: 12px; }
        .price-card .price { font-size: 2.8rem; font-weight: 700; color: #1e4a42; margin: 16px 0; }
        .price-card ul { text-align: left; list-style: none; margin: 20px 0; }
        .price-card li { padding: 8px 0; display: flex; align-items: center; gap: 8px; }
        .price-card li::before { content: "✓"; color: #2e7d64; font-weight: bold; }
        
        .order-form-section { background: white; border-radius: 48px; padding: 48px; margin: 80px 0; box-shadow: 0 20px 40px -12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
        .form-grid { display: flex; flex-wrap: wrap; gap: 32px; margin-top: 32px; }
        .form-col { flex: 1; min-width: 260px; }
        .form-group { margin-bottom: 24px; }
        label { display: block; font-weight: 500; margin-bottom: 8px; color: #1e293b; }
        select, input { width: 100%; padding: 14px 18px; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 28px; font-size: 1rem; transition: 0.2s; }
        select:focus, input:focus { outline: none; border-color: #1e4a42; box-shadow: 0 0 0 3px rgba(30,74,66,0.1); }
        .price-badge { background: #e6f7f3; border-radius: 28px; padding: 16px; text-align: center; font-weight: 700; font-size: 1.4rem; color: #1e4a42; margin: 20px 0; }
        .btn { background: #1e4a42; color: white; border: none; width: 100%; padding: 16px; border-radius: 40px; font-weight: 600; font-size: 1rem; cursor: pointer; transition: 0.2s; }
        .btn:hover { background: #0b2b26; transform: translateY(-2px); }
        
        .reviews-section { background: white; border-radius: 48px; padding: 48px; margin: 60px 0; border: 1px solid #e2e8f0; }
        .reviews-grid { display: flex; flex-direction: column; gap: 20px; margin-top: 32px; }
        .review-card { background: #f8fafc; border-radius: 28px; padding: 20px 28px; border-left: 4px solid #1e4a42; }
        .review-name { font-weight: 700; color: #1e4a42; margin-bottom: 8px; }
        .review-stars { color: #f5b042; margin-bottom: 8px; font-size: 1.1rem; }
        .review-text { color: #334155; margin-bottom: 8px; }
        .review-date { font-size: 0.7rem; color: #94a3b8; }
        
        .contact-block { background: #f1f5f9; border-radius: 32px; padding: 32px; text-align: center; margin: 40px 0; }
        .contact-links { display: flex; justify-content: center; gap: 24px; flex-wrap: wrap; margin: 20px 0; }
        .contact-card { background: white; padding: 12px 24px; border-radius: 60px; font-weight: 500; }
        footer { text-align: center; padding: 32px 0; border-top: 1px solid #e2e8f0; color: #6c7a91; margin-top: 40px; }
        @media (max-width: 700px) { .hero { padding: 32px; } .hero-content h2 { font-size: 2rem; } }
    </style>
    <script>
        function updatePrice() {
            const service = document.getElementById('service').value;
            let price = service === '1 час' ? 1000 : 2000;
            document.getElementById('displayPrice').innerText = price + ' ₽';
            document.getElementById('totalPriceHidden').value = price;
        }
        window.onload = updatePrice;
    </script>
</head>
<body>
<div class="header">
    <div class="container header-inner">
        <div class="logo"><h1>EFMConsult</h1><p>компьютерная помощь • удалённо</p></div>
        <div class="nav"><a href="#prices">Услуги</a><a href="#order">Заказать</a><a href="#reviews">Отзывы</a><a href="#contacts">Контакты</a></div>
    </div>
</div>

<div class="container">
    <div class="hero">
        <div class="hero-content">
            <h2>Компьютерная помощь<br>без стресса и очередей</h2>
            <p>Консультация онлайн, удалённое подключение, решение проблем любой сложности. Чётко, быстро, без лишних слов.</p>
            <div class="hero-stats"><div class="stat"><h3>500+</h3><p>клиентов</p></div><div class="stat"><h3>98%</h3><p>положительных</p></div><div class="stat"><h3>15 мин</h3><p>средний отклик</p></div></div>
        </div>
        <div class="hero-image">💻🖱️</div>
    </div>

    <div id="prices" class="pricing">
        <div class="section-title">Честные цены</div>
        <div class="section-sub">Никаких скрытых комиссий — только фиксированный тариф</div>
        <div class="price-grid">
            <div class="price-card"><h3>1 час</h3><div class="price">1 000 ₽</div><ul><li>Консультация по любой проблеме</li><li>Диагностика текстом</li><li>Советы по устранению</li></ul></div>
            <div class="price-card"><h3>2 часа</h3><div class="price">2 000 ₽</div><ul><li>Всё из первого тарифа</li><li>Удалённое подключение</li><li>Полное решение задачи</li></ul></div>
        </div>
    </div>

    <div id="reviews" class="reviews-section">
        <div class="section-title">⭐ Отзывы наших клиентов</div>
        <div class="section-sub">Что говорят те, кому мы уже помогли</div>
        <div class="reviews-grid">
            {% if reviews %}
                {% for r in reviews %}
                <div class="review-card">
                    <div class="review-name">{{ r.name }}</div>
                    <div class="review-stars">{% for _ in range(r.rating) %}⭐{% endfor %}</div>
                    <div class="review-text">"{{ r.review }}"</div>
                    <div class="review-date">{{ r.date }}</div>
                </div>
                {% endfor %}
            {% else %}
                <p style="text-align:center; color:#6c7a91;">Пока нет отзывов. Будьте первым!</p>
            {% endif %}
        </div>
    </div>

    <div id="order" class="order-form-section">
        <div class="section-title">📋 Оформить заказ</div>
        <div class="section-sub">Заполните форму — мы свяжемся с вами в течение 15 минут</div>
        <form method="POST" action="/create_order">
            <div class="form-grid">
                <div class="form-col">
                    <div class="form-group"><label>🕒 Тариф</label><select name="service" id="service" onchange="updatePrice()"><option value="1 час">1 час (1000 ₽)</option><option value="2 часа">2 часа (2000 ₽)</option></select></div>
                    <div class="form-group"><label>👤 Ваше имя</label><input type="text" name="name" placeholder="Как к вам обращаться?" required></div>
                </div>
                <div class="form-col">
                    <div class="price-badge">💰 К оплате: <span id="displayPrice">1000</span> ₽</div>
                    <input type="hidden" name="price" id="totalPriceHidden" value="1000">
                    <button type="submit" class="btn">✅ СОЗДАТЬ ЗАКАЗ</button>
                </div>
            </div>
        </form>
    </div>

    <div id="contacts" class="contact-block">
        <h3 style="margin-bottom: 16px;">📬 Свяжитесь с нами</h3>
        <div class="contact-links">
            <div class="contact-card">📱 Telegram: <strong>@kotik999myau</strong></div>
            <div class="contact-card">📱 MAX: <strong>+7 985 512 77 06</strong></div>
            <div class="contact-card">✉️ Почта: <strong>efmstudio@inbox.ru</strong></div>
        </div>
        <p style="font-size: 0.8rem; margin-top: 12px;">❗ По телефону — только MAX. Обычные звонки не принимаем.</p>
    </div>
    <footer>© EFMConsult — Профессиональная компьютерная помощь | Работаем по всей России</footer>
</div>
</body>
</html>
'''

HTML_ORDER_CONFIRM = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Заказ создан | EFMConsult</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;font-family:'Inter',sans-serif;}
        body{background:#f8fafc;padding:40px;min-height:100vh;display:flex;align-items:center;justify-content:center;}
        .card{max-width:550px;margin:auto;background:white;border-radius:48px;padding:40px;border:1px solid #e2e8f0;text-align:center;box-shadow:0 20px 35px -10px rgba(0,0,0,0.05);}
        h2{color:#1e4a42;margin-bottom:20px;}
        .order-num{font-size:32px;background:#e6f7f3;padding:15px;border-radius:48px;margin:15px 0;font-weight:bold;letter-spacing:4px;color:#1e4a42;}
        .info p{margin:12px 0;color:#334155;}
        .info strong{color:#0b2b26;}
        .btn{display:inline-block;background:#1e4a42;padding:12px 28px;border-radius:40px;color:white;font-weight:600;text-decoration:none;margin-top:24px;margin-right:12px;border:none;cursor:pointer;}
        .btn:hover{background:#0b2b26;}
        .contact-note{margin-top:24px;padding-top:20px;border-top:1px solid #e2e8f0;font-size:0.85rem;color:#5b6e8c;}
    </style>
</head>
<body>
<div class="card">
    <h2>✅ Заказ создан</h2>
    <div class="order-num">№ {{ order_number }}</div>
    <div class="info">
        <p><strong>Услуга:</strong> {{ service }}</p>
        <p><strong>Сумма:</strong> {{ price }} ₽</p>
        <p><strong>Имя:</strong> {{ name }}</p>
    </div>
    <div class="contact-note">
        📬 Свяжитесь с нами и <strong>обязательно укажите номер заказа</strong><br>
        Telegram: @kotik999myau | MAX: +7 985 512 77 06
    </div>
    <a href="/" class="btn">◀ На главную</a>
</div>
</body>
</html>
'''

HTML_ADMIN = '''
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Вход в админку</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>*{margin:0;padding:0;box-sizing:border-box;}body{background:#f8fafc;padding:40px;font-family:'Inter',sans-serif;}.container{max-width:460px;margin:80px auto;background:white;border-radius:48px;padding:40px;border:1px solid #e2e8f0;}h2{color:#1e4a42;text-align:center;margin-bottom:24px;}input,button{width:100%;padding:14px;margin:12px 0;border-radius:60px;border:none;}input{background:#f8fafc;border:1px solid #cbd5e1;font-size:1rem;}button{background:#1e4a42;color:white;font-weight:600;cursor:pointer;}button:hover{background:#0b2b26;}.error{color:#e53e3e;text-align:center;margin-top:12px;}</style>
</head>
<body>
<div class="container"><h2>🔐 Вход в админ-панель</h2>
<form method="POST"><input type="password" name="password" placeholder="Введите пароль" required><button type="submit">Войти</button></form>
{% if error %}<p class="error">{{ error }}</p>{% endif %}</div></body></html>
'''

HTML_ADMIN_PANEL = '''
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Панель заказов</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}body{background:#f8fafc;padding:40px;font-family:'Inter',sans-serif;}.container{max-width:900px;margin:0 auto;background:white;border-radius:48px;padding:40px;border:1px solid #e2e8f0;}
h2{color:#1e4a42;text-align:center;margin-bottom:24px;}input,button{width:100%;padding:14px;margin:8px 0;border-radius:60px;border:none;}
input{background:#f8fafc;border:1px solid #cbd5e1;font-size:1rem;}button{background:#1e4a42;color:white;font-weight:600;cursor:pointer;transition:0.2s;}button:hover{background:#0b2b26;}
.screenshot-card{background:#fefefe;border-radius:28px;padding:28px;margin-top:28px;border:2px solid #e2e8f0;box-shadow:0 10px 25px -5px rgba(0,0,0,0.05);}
.screenshot-header{text-align:center;border-bottom:2px dashed #cbd5e1;padding-bottom:16px;margin-bottom:20px;}.screenshot-header h3{font-size:1.8rem;color:#1e4a42;}
.order-row{display:flex;padding:12px 0;border-bottom:1px solid #e2e8f0;}.order-label{width:140px;font-weight:600;color:#1e4a42;}.order-value{flex:1;color:#0f172a;font-weight:500;}
.screenshot-note{text-align:center;font-size:0.7rem;color:#94a3b8;margin-top:16px;}
.service-btn{background:#2e7d64;margin-top:10px;}
.back{display:inline-block;margin-top:24px;color:#1e4a42;text-decoration:none;font-weight:500;}
hr{margin:24px 0;}
.not-found{color:#e53e3e;text-align:center;margin-top:20px;}
.reviews-list{margin-top:40px;}.review-item{background:#f8fafc;padding:16px;border-radius:24px;margin-bottom:12px;border-left:3px solid #1e4a42;}
</style>
</head>
<body>
<div class="container">
    <h2>📦 Поиск заказа</h2>
    <form method="POST">
        <input type="text" name="order_number" placeholder="Введите номер заказа (8 цифр)" required>
        <button type="submit">Найти заказ</button>
    </form>
    
    {% if order %}
        <div class="screenshot-card">
            <div class="screenshot-header"><h3>✅ Заказ №{{ order.number }}</h3><p>сформирован {{ order.date }}</p></div>
            <div class="order-row"><div class="order-label">👤 Клиент</div><div class="order-value">{{ order.name }}</div></div>
            <div class="order-row"><div class="order-label">⚙️ Услуга</div><div class="order-value">{{ order.service }}</div></div>
            <div class="order-row"><div class="order-label">💰 Сумма</div><div class="order-value">{{ order.price }} ₽</div></div>
            <div class="screenshot-note">🖥️ EFMConsult — компьютерная помощь</div>
        </div>
        
        <form method="POST" action="/close_order">
            <input type="hidden" name="order_number" value="{{ order.number }}">
            <button type="submit" class="service-btn">✅ Я обслужил клиента</button>
        </form>
    {% elif searched and not order %}
        <p class="not-found">❌ Заказ не найден</p>
    {% endif %}
    
    <hr>
    <h3 style="margin:20px 0 10px">⭐ Отзывы клиентов</h3>
    <div class="reviews-list">
        {% for r in reviews %}
        <div class="review-item">
            <strong>{{ r.name }}</strong> (оценка: {{ r.rating }}★) <span style="color:#6c7a91; font-size:0.7rem;">{{ r.date }}</span>
            <p style="margin-top:5px;">"{{ r.review }}"</p>
        </div>
        {% else %}
        <p style="color:#6c7a91;">Нет отзывов</p>
        {% endfor %}
    </div>
    
    <hr>
    <a href="/" class="back">← Вернуться на главную</a>
</div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_MAIN, reviews=reviews_db)

@app.route('/create_order', methods=['POST'])
def create_order():
    name = request.form.get('name', '').strip()
    service = request.form.get('service')
    price = PRICES.get(service, 1000)
    if not name or not service:
        return "Ошибка: не заполнены данные", 400
    order_number = generate_order_number()
    orders_db[order_number] = {
        'name': name,
        'service': service,
        'price': price,
        'date': datetime.now().strftime("%d.%m.%Y %H:%M")
    }
    return render_template_string(HTML_ORDER_CONFIRM,
                                 order_number=order_number,
                                 service=service,
                                 price=price,
                                 name=name)

@app.route('/close_order', methods=['POST'])
def close_order():
    order_number = request.form.get('order_number')
    if order_number in orders_db:
        closed_orders[order_number] = orders_db[order_number]
        del orders_db[order_number]
    return redirect(url_for('admin_search'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'fima1456Game!':
            session['admin_logged'] = True
            return redirect(url_for('admin_search'))
        else:
            return render_template_string(HTML_ADMIN, error='Неверный пароль')
    return render_template_string(HTML_ADMIN)

@app.route('/admin/search', methods=['GET', 'POST'])
def admin_search():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_panel'))
    order = None
    searched = False
    if request.method == 'POST':
        order_num = request.form.get('order_number', '').strip()
        if order_num in orders_db:
            order = {
                'number': order_num,
                'name': orders_db[order_num]['name'],
                'service': orders_db[order_num]['service'],
                'price': orders_db[order_num]['price'],
                'date': orders_db[order_num]['date']
            }
        searched = True
    return render_template_string(HTML_ADMIN_PANEL, order=order, searched=searched, reviews=reviews_db)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    data = request.get_json()
    order_number = data.get('order_number')
    name = data.get('name')
    rating = data.get('rating', 5)
    review = data.get('review')
    
    if order_number not in closed_orders:
        return {'success': False, 'error': 'Заказ не найден или ещё не закрыт'}
    if not review or len(review) < 2:
        return {'success': False, 'error': 'Отзыв слишком короткий'}
    
    reviews_db.append({
        'name': name,
        'order_number': order_number,
        'rating': rating,
        'review': review,
        'date': datetime.now().strftime("%d.%m.%Y %H:%M")
    })
    return {'success': True}

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════╗
║         EFMConsult                   ║
║   Компьютерная помощь удалённо       ║
╠══════════════════════════════════════╣
║  🌐 http://localhost:5000            ║
║  🔐 Админка: /admin                  ║
║  🔑 Пароль: fima1456Game!            ║
╚══════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)

import json
import sqlite3
import time
import hashlib
import http.client
import urllib.parse
from sqlite3 import Error
import telebot
import requests

bot = telebot.TeleBot("6373577877:AAEntNmZ3XNJkcrOotju9g0K6K2GRg4oDLE")
database = "users_data.db"


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(database, check_same_thread=False)
        print(f"Соединение с базой данных успешно установлено. Версия SQLite: {sqlite3.version}")
        return conn
    except Error as e:
        print(e)

    return conn


def create_users_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance REAL, purchases REAL, discount REAL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS purchases (user_id INTEGER, amount REAL)")
        conn.commit()
        print("Таблица 'users' успешно создана")
    except Error as e:
        print(e)


def add_user(conn, user_id):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (user_id, balance, purchases) VALUES (?, ?, ?)",
                       (user_id, 0, 0))
        cursor.execute("INSERT INTO purchases (user_id, amount) VALUES (?, ?)",
                       (user_id, 0))
        conn.commit()
        print(f"Пользователь {user_id} успешно добавлен в базу данных")
    except Error as e:
        print(e)


# Функция для получения данных пользователя по его telegram_id
def get_user_data(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row is not None:
        return {
            "user_id": row[0],
            "balance": row[1],
            "purchases": row[2]
        }
    else:
        return None


# Функция для обновления баланса пользователя
def update_balance(conn, user_id, amount):
    cursor = conn.cursor()

    # Получение текущего баланса пользователя
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result is None:
        print(f"Пользователь с идентификатором {user_id} не найден")
        return

    old_balance = result[0]
    new_balance = old_balance + float(amount)

    # Обновление баланса пользователя
    cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (new_balance, user_id))
    conn.commit()
    print(f"Баланс пользователя {user_id} обновлен: {old_balance} + {amount} = {new_balance}")


# Функция для обновления суммы покупок пользователя
def update_purchases(conn, user_id, new_purchases):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET purchases=? WHERE user_id=?", (new_purchases, user_id))
    conn.commit()
    print(f"Сумма покупок пользователя {user_id} обновлена")


# Функция для обновления доменов пользователя
def update_domains(conn, user_id, new_domains):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET domains=? WHERE user_id=?", (new_domains, user_id))
    conn.commit()
    print(f"Домены пользователя {user_id} обновлены")


def update_profile_info(conn, user_id):
    cursor = conn.cursor()

    # Получение текущего баланса пользователя
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    balance = cursor.fetchone()[0]

    # Получение суммы покупок пользователя
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM purchases WHERE user_id=?", (user_id,))
    purchases = cursor.fetchone()[0]

    discount = calculate_discount(purchases)

    # Обновление информации о профиле пользователя
    cursor.execute("UPDATE users SET balance=?, purchases=?, discount=? WHERE user_id=?",
                   (balance, purchases, discount, user_id))
    conn.commit()


def add_purchase(connection, user_id, amount):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO purchases (user_id, amount) VALUES (?, ?)", (user_id, amount))
    connection.commit()


# Инициализация соединения
connection = create_connection()
cursor = connection.cursor()

if connection is not None:
    create_users_table(connection)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    user_data = get_user_data(connection, user_id)
    if user_data is None:
        add_user(connection, user_id)

    rules = "Правила и соглашение:\n..."
    bot.send_message(user_id, rules)

    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)

    replenish_balance_button = telebot.types.KeyboardButton('Пополнить баланс')
    profile_button = telebot.types.KeyboardButton('Профиль')
    buy_domains_button = telebot.types.KeyboardButton('Купить домены')
    buy_host_button = telebot.types.KeyboardButton('Купить хост')
    my_services_button = telebot.types.KeyboardButton('Мои услуги')

    keyboard.add(replenish_balance_button, profile_button, buy_domains_button, buy_host_button, my_services_button)
    bot.send_message(user_id, "Выберите действие:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Пополнить баланс')
def replenish_balance(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Выберите метод оплаты:", reply_markup=payment_method_keyboard())
    bot.register_next_step_handler(message, process_payment_method)


# Функция для создания клавиатуры с методами оплаты
def payment_method_keyboard():
    payment_methods = ['USDT TRC20', 'BTC', 'ETH']
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    buttons = [telebot.types.KeyboardButton(method) for method in payment_methods]
    keyboard.add(*buttons)
    return keyboard


# Функция для обработки следующего шага после выбора метода оплаты
def process_payment_method(message):
    user_id = message.chat.id
    method = message.text
    bot.send_message(user_id, "Введите сумму пополнения в $:")
    bot.register_next_step_handler(message, lambda msg: process_replenish_balance(msg, method))


# Функция для обработки следующего шага после ввода суммы пополнения
def process_replenish_balance(message, method):
    user_id = message.chat.id
    amount = message.text

    if method == "USDT TRC20":
        method = "USDTCRYPTOBOT"
    elif method == "BTC":
        method = "BITCOIN"
    elif method == "ETH":
        method = "ETHEREUM"

    # Подключение к Crystal Pay API и отправка запроса на оплату
    url = "https://api.crystalpay.io/v2/invoice/create/"
    data = {
        "auth_login": "domainsSecond2Bot",
        "auth_secret": "77f06e463422308db2549add690388d2c4fcadc0",
        "amount": amount,
        "required_method": method,
        "amount_currency": "USD",
        "type": "purchase",
        "lifetime": 60
    }
    response = requests.post(url, json=data)
    data = json.loads(response.text)
    url = data["url"]

    update_balance(connection, user_id, amount)
    update_profile_info(connection, user_id)

    # Обновление информации о профиле пользователя
    update_profile_info(connection, user_id)

    bot.send_message(user_id, "Ваш баланс успешно пополнен.")


# Обработчик команды "Профиль"
@bot.message_handler(func=lambda message: message.text == 'Профиль')
def profile(message):
    user_id = message.chat.id
    cursor = connection.cursor()
    # Обновление информации о профиле пользователя
    update_profile_info(connection, user_id)

    # Получение информации о профиле пользователя
    cursor.execute("SELECT balance, purchases, discount FROM users WHERE user_id=?", (user_id,))
    profile_info = cursor.fetchone()

    balance = profile_info[0]
    purchases = profile_info[1]
    discount = profile_info[2]

    profile_info = f"Текущий баланс: ${balance}\nСумма покупок: ${purchases}\nТекущая скидка: {discount}%"
    bot.send_message(user_id, profile_info)


def calculate_discount(amount):
    if amount >= 10000:
        return 10
    elif amount >= 5000:
        return 5
    elif amount >= 1000:
        return 3
    else:
        return 0


# Обработчик команды "Купить домены"
@bot.message_handler(func=lambda message: message.text == 'Купить домены')
def buy_domains(message):
    user_id = message.chat.id

    # Получение информации о доступных доменных зонах и их ценах
    domains_info = get_domains_info()
    bot.send_message(user_id, domains_info)

    # Запрос выбора доменной зоны
    bot.send_message(user_id, "Выберите доменную зону:")
    bot.register_next_step_handler(message, process_domain_zone_selection)


def get_domains_info():
    domains_info = ".com - 23$\n.net - 25$\n.org - 23$"
    return domains_info


def process_domain_zone_selection(message):
    user_id = message.chat.id
    domain_zone = message.text

    # Получение введенного доменного имени от пользователя
    bot.send_message(user_id, "Введите доменное имя без доменной зоны:")
    bot.register_next_step_handler(message, process_domain_purchase, domain_zone)


def process_domain_purchase(message, domain_zone):
    user_id = message.chat.id
    domain_name = message.text

    # Проверка доступности доменной зоны и предложение купить домен
    if is_domain_available(domain_name, domain_zone):
        confirmation_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
        buy_button = telebot.types.KeyboardButton('Купить')
        cancel_button = telebot.types.KeyboardButton('Отмена')
        confirmation_keyboard.add(buy_button, cancel_button)
        bot.send_message(user_id, "Домен доступен. Вы хотите его купить?", reply_markup=confirmation_keyboard)
        bot.register_next_step_handler(message, process_domain_purchase_confirmation, domain_name)
    else:
        bot.send_message(user_id, "Это доменное имя недоступно. Пожалуйста, выберите другое доменное имя.")


def is_domain_available(query, suffix):
    url = "http://panda.www.net.cn/cgi-bin/check_muitl.cgi?domain="
    url += query + suffix

    result = my_file_get_contents(url)  # You need to implement my_file_get_contents() method

    if query + suffix + "|210" in result:
        return True
    elif query + suffix + "|211" in result:
        return False
    else:
        return False


def my_file_get_contents(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except requests.exceptions.RequestException:
        return None

    return None



def post_data(params, userid, email, password):
    sVTime = time.strftime("%Y%m%d%H%M", time.localtime())
    params.append(("userid", userid))
    params.append(("vtime", sVTime))

    userstr = userid + password + email + sVTime
    params.append(("userstr", hashlib.md5(userstr.encode()).hexdigest()))

    encoded_params = urllib.parse.urlencode(params)
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Connection": "close"
    }

    conn = http.client.HTTPConnection("api.nicenic.cxm")
    conn.request("POST", "/", encoded_params, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()

    return data.decode()


"""
def is_domain_available(domain_zone, domain_name):
    url = "http://api.nicenic.com/"
    data = {
        "category": "domain",
        "action": "check",
        "query": domain_name,
        "suffix": domain_zone
    }
    try:
        response = requests.get(url, data=data)
        print(response.text)
        response.raise_for_status()  # проверка на ошибки при отправке запроса
    except requests.exceptions.RequestException as err:
        print(f"Возникла ошибка при выполнении запроса: {err}")"""


def process_domain_purchase_confirmation(message, domain_name):
    user_id = message.chat.id
    confirmation = message.text

    if confirmation == 'Купить':
        # Покупка домена
        purchase_domain(domain_name)
        bot.send_message(user_id, "Домен успешно приобретен!")
    else:
        bot.send_message(user_id, "Покупка домена отменена.")


def purchase_domain(domain_name):
    # API www.nicenic.net для покупки домена и привязки NS
    pass


bot.polling()

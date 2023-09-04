import json
import sqlite3
from sqlite3 import Error
import telebot
from telebot import types
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
            "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance REAL, purchases REAL, "
            "discount REAL)")
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
    back_button = telebot.types.KeyboardButton('Назад')
    keyboard.add(back_button)
    return keyboard


# Функция для обработки следующего шага после выбора метода оплаты
def process_payment_method(message):
    user_id = message.chat.id
    method = message.text
    if method == 'Назад':
        start(message)
    else:
        # Добавляем кнопку "Отмена" для отмены ввода
        cancel_button = telebot.types.KeyboardButton('Отмена')
        cancel_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        cancel_keyboard.add(cancel_button)
        bot.send_message(user_id, "Введите сумму пополнения в $:", reply_markup=cancel_keyboard)
        bot.register_next_step_handler(message, lambda msg: process_replenish_balance(msg, method))


# Функция для обработки следующего шага после ввода суммы пополнения
def process_replenish_balance(message, method):
    user_id = message.chat.id
    amount = message.text

    if amount == 'Отмена':
        start(message)  # Вернуться к основному меню при выборе "Отмена"
    else:
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
        print(url)

        update_balance(connection, user_id, amount)
        update_profile_info(connection, user_id)

        # Обновление информации о профиле пользователя
        update_profile_info(connection, user_id)

        bot.send_message(user_id, "Ваш баланс успешно пополнен.")
        start(message)


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


domain_zones = {
    ".com": 23,
    ".net": 25,
    ".org": 23,
    ".info": 20,  # Пример другой доменной зоны
    ".biz": 18  # Пример другой доменной зоны
}


# Обработчик команды "Купить домены"
@bot.message_handler(func=lambda message: message.text == 'Купить домены')
def buy_domains(message):
    user_id = message.chat.id

    # Отправляем пользователю список доступных доменных зон и цен
    domains_info = "Доступные доменные зоны и цены:\n"
    for zone, price in domain_zones.items():
        domains_info += f"{zone} - {price}$\n"

    # Создаем клавиатуру с кнопкой "Назад"
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for zone in domain_zones.keys():
        markup.add(zone)
    markup.add("Другая доменная зона", "Назад")  # Добавляем кнопку "Назад"

    bot.send_message(user_id, domains_info)
    bot.send_message(user_id, "Выберите доменную зону из списка или введите свою:", reply_markup=markup)
    bot.register_next_step_handler(message, process_domain_zone_selection)


def process_domain_zone_selection(message):
    user_id = message.chat.id
    selected_zone = message.text

    if selected_zone == "Назад":
        start(message)
    elif selected_zone in domain_zones:
        # Если выбрана доменная зона из списка
        bot.send_message(user_id, f"Вы выбрали доменную зону {selected_zone}.")
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add("Назад")
        bot.send_message(user_id, "Введите доменное имя без доменной зоны:", reply_markup=markup)
        bot.register_next_step_handler(message, process_domain_purchase, selected_zone)
    elif selected_zone == "Другая доменная зона":
        # Если выбрана опция "Другая доменная зона"
        bot.send_message(user_id, "Введите свою доменную зону (например, '.example'):")
        bot.register_next_step_handler(message, process_custom_domain_zone)
    else:
        # Если введенная зона не найдена в списке
        bot.send_message(user_id, "Доменная зона не найдена. Пожалуйста, выберите из списка или введите свою.")


def process_custom_domain_zone(message):
    user_id = message.chat.id
    custom_zone = message.text.strip()

    if custom_zone == "Назад":
        buy_domains(message)
    # Проверка на корректность формата зоны (должна начинаться с точки)
    elif custom_zone.startswith("."):
        bot.send_message(user_id, f"Вы выбрали доменную зону {custom_zone}.")
        bot.send_message(user_id, "Введите доменное имя без доменной зоны:")
        bot.register_next_step_handler(message, process_domain_purchase, custom_zone)
    else:
        bot.send_message(user_id,
                         "Некорректный формат доменной зоны. Пожалуйста, введите зону, начиная с точки (например, '.example').")


def process_domain_purchase(message, selected_zone):
    user_id = message.chat.id
    domain_name = message.text
    if domain_name == "Назад":
        buy_domains(message)

    # Проверка доступности доменной зоны и предложение купить домен
    elif is_domain_available(selected_zone, domain_name):
        confirmation_markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buy_button = telebot.types.KeyboardButton('Купить')
        cancel_button = telebot.types.KeyboardButton('Отмена')
        back_button = telebot.types.KeyboardButton('Назад')
        confirmation_markup.add(buy_button, cancel_button, back_button)
        bot.send_message(user_id, "Домен доступен. Вы хотите его купить?", reply_markup=confirmation_markup)
        bot.register_next_step_handler(message, process_domain_purchase_confirmation, domain_name, selected_zone)
    else:
        bot.send_message(user_id, "Это доменное имя недоступно. Пожалуйста, выберите другое доменное имя.")


def is_domain_available(domain_zone, domain_name):
    url = "https://api.ote-godaddy.com/v1/domains/available"
    headers = {
        "Authorization": "sso-key 3mM44UdBCbEmRF_Uac91bSRzG2f196iUCUVac:HN7VLrUFQ9YP1zvAFPjN7R"
    }
    params = {
        "domain": domain_name + domain_zone
    }

    try:
        response = requests.get(url, headers=headers)
        response_data = response.json()

        if "available" in response_data and response_data["available"]:
            price = response_data.get("price", {}).get("purchase")
            if price:
                return True, price
            else:
                return True, "Цена не указана"
        else:
            return False, "Домен недоступен"
    except requests.exceptions.RequestException as err:
        print(f"Возникла ошибка при выполнении запроса: {err}")
        return False, "Произошла ошибка при проверке доступности домена"


def process_domain_purchase_confirmation(message, domain_name, selected_zone):
    user_id = message.chat.id
    confirmation = message.text

    if confirmation == 'Купить':
        price = domain_zones[selected_zone]
        purchase_domain(domain_name, selected_zone)
        bot.send_message(user_id, f"Домен {domain_name}{selected_zone} успешно приобретен за {price}$!")
    elif confirmation == 'Отмена':
        bot.send_message(user_id, "Покупка домена отменена.")
    elif confirmation == 'Назад':
        bot.send_message(user_id, "Выберите доменную зону:")
        bot.register_next_step_handler(message, process_domain_zone_selection)
    else:
        bot.send_message(user_id, "Некорректный выбор. Используйте кнопки на клавиатуре.")


def purchase_domain(domain_name, domain_zone):
    purchase_data = {
        "consent": {
            "agreedAt": "2023-09-04T12:00:00Z",
            "agreedBy": "Your Name",
            "agreementKeys": ["DNRA"]
        },
        "contactAdmin": {
            "addressMailing": {
                "address1": "123 Main St",
                "city": "Your City",
                "country": "US",
                "postalCode": "12345",
                "state": "CA"  # Код штата для Калифорнии
            },
            "email": "admin@example.com",
            "fax": "+1.1234567890",
            "jobTitle": "1",
            "nameFirst": "Admin",
            "nameLast": "LastName",
            "nameMiddle": "1",
            "organization": "Your Organization",
            "phone": "+1.1234567890"
        },
        "contactBilling": {
            "addressMailing": {
                "address1": "123 Main St",
                "city": "Your City",
                "country": "US",
                "postalCode": "12345",
                "state": "CA"  # Код штата для Калифорнии
            },
            "email": "billing@example.com",
            "fax": "+1.1234567890",
            "jobTitle": "1",
            "nameFirst": "Billing",
            "nameLast": "LastName",
            "nameMiddle": "",
            "organization": "Your Organization",
            "phone": "+1.1234567890"
        },
        "contactRegistrant": {
            "addressMailing": {
                "address1": "123 Main St",
                "city": "Your City",
                "country": "US",
                "postalCode": "12345",
                "state": "CA"  # Код штата для Калифорнии
            },
            "email": "registrant@example.com",
            "fax": "+1.1234567890",
            "jobTitle": "1",
            "nameFirst": "Registrant",
            "nameLast": "LastName",
            "nameMiddle": "1",
            "organization": "Your Organization",
            "phone": "+1.1234567890"
        },
        "contactTech": {
            "addressMailing": {
                "address1": "123 Main St",
                "city": "Your City",
                "country": "US",
                "postalCode": "12345",
                "state": "CA"  # Код штата для Калифорнии
            },
            "email": "tech@example.com",
            "fax": "+1.1234567890",
            "jobTitle": "1",
            "nameFirst": "Tech",
            "nameLast": "LastName",
            "nameMiddle": "",
            "organization": "Your Organization",
            "phone": "+1.1234567890"
        },
        "domain": domain_name + domain_zone,
        "nameServers": ["ns1.example.com", "ns2.example.com"],
        "period": 1,
        "privacy": False,
        "renewAuto": True
    }

    # Отправка POST-запроса
    url = "https://api.ote-godaddy.com/v1/domains/purchase"
    headers = {
        "Authorization": "sso-key 3mM44UdBCbEmRF_Uac91bSRzG2f196iUCUVac:HN7VLrUFQ9YP1zvAFPjN7R",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=purchase_data)
        print(response.text)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(f"Произошла ошибка при покупке домена: {err}")


@bot.message_handler(func=lambda message: message.text == 'Купить хост')
def buy_host(message):
    user_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardMarkup()

    pq_hosting_button = telebot.types.KeyboardButton('pq hosting')
    ddos_guard_button = telebot.types.KeyboardButton('DDOS Guard')
    privacy_protection_button = telebot.types.KeyboardButton('Приват защита от любых атак')

    keyboard.add(pq_hosting_button, ddos_guard_button, privacy_protection_button)
    bot.send_message(user_id, "Выберите хост:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'pq hosting')
def host_configuration(message):
    # 1 пункт если нажимает - дает на выбор 4 разных конфигурации хоста, позже покажем
    pass


@bot.message_handler(func=lambda message: message.text == 'DDOS Guard')
def host_configuration(message):
    user_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardMarkup()

    generic_button = telebot.types.KeyboardButton('Общий сервер ddos guard - 12$')
    for_one_domain_button = telebot.types.KeyboardButton('Сервер ddos guard для одного домена - 80$')
    personal_button = telebot.types.KeyboardButton('Личный сервер для 50-ти доменов - 350$')

    keyboard.add(generic_button, for_one_domain_button, personal_button)
    bot.send_message(user_id, "Выберите сервер:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Приват защита от любых атак')
def host_configuration(message):
    user_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardMarkup()

    buy_button = telebot.types.KeyboardButton('Купить')
    cancel_button = telebot.types.KeyboardButton('Отменить')

    keyboard.add(buy_button, cancel_button)
    bot.send_message(user_id, "1 домен - 95$", reply_markup=keyboard)

    bot.register_next_step_handler(message, process_purchase_confirmation)


def process_purchase_confirmation(message):
    user_id = message.chat.id
    confirmation = message.text

    if confirmation == 'Купить':
        purchase_func()
        bot.send_message(user_id, "Покупка cовершена успешно!")
    else:
        bot.send_message(user_id, "Покупка отменена.")


def purchase_func():
    pass


@bot.message_handler(func=lambda message: message.text == 'Мои услуги ')
def my_services(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    item1 = types.KeyboardButton('Мои сайты')
    item2 = types.KeyboardButton('Мои хостинги')
    markup.add(item1, item2)
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Мои сайты' or message.text == 'Мои хостинги')
def handle_buttons(message):
    # По нажатию первой - выходит список доменов и хостов - на каждый можно нажать и редактировать
    # Домены - сменить IP привязки
    # Хостинги - (пишет IP хоста) - показывает текущие домены на хосте + кнопка добавить домен
    if message.text == 'Мои сайты':
        pass
    elif message.text == 'Мои хостинги':
        pass


@bot.callback_query_handler(func=lambda call: call.data == 'add_domain')
def handle_add_domain(call):
    pass


bot.polling()

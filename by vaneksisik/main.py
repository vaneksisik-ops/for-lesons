import os
import json
import hashlib
import os
import tempfile
import pyzipper

def convert_keys_to_int(items_list):
    return [{int(k): v for k, v in item.items()} for item in items_list]


if os.path.exists("menu.json") and os.path.getsize("menu.json") > 0:
    with open("menu.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        adult_menu = convert_keys_to_int(data.get("adult_menu", []))
        kids_menu = convert_keys_to_int(data.get("kids_menu", []))
        drinks_menu = convert_keys_to_int(data.get("drinks_menu", []))
        adult_prices = convert_keys_to_int(data.get("adult_prices", []))
        kids_prices = convert_keys_to_int(data.get("kids_prices", []))
        drinks_prices = convert_keys_to_int(data.get("drinks_prices", []))




adult_prices = [{0: 650}, {1: 450}, {2: 490}, {3: 2400}, {4: 1900}, {5: 950}, {6: 850}, {7: 550}, {8: 480}, {9: 690},
                {10: 580}, {11: 380}, {12: 420}]
kids_prices = [{0: 250}, {1: 280}, {2: 310}, {3: 290}, {4: 380}, {5: 320}, {6: 340}, {7: 280}, {8: 240}, {9: 190},
               {10: 220}, {11: 260}, {12: 210}]
drinks_prices = [{0: 280}, {1: 350}, {2: 230}, {3: 270}, {4: 120}, {5: 250}, {6: 290}]


def get_price(menu_prices, item_id):
    for d in menu_prices:
        if item_id in d:
            return d[item_id]
    return 0


if os.path.exists("users.json") and os.path.getsize("users.json") > 0:
    with open("users.json", "r", encoding="utf-8") as file:
        users = json.load(file)
else:
    users = []

current_user = None
num_adults = 0
num_children = 0
total_price = 0
total_items_count = 0


def view_orders():
    print()
    if os.path.exists("orders.json") and os.path.getsize("orders.json") > 0:
        with open("orders.json", "r", encoding="utf-8") as file:
            orders = json.load(file)
    else:
        orders = []

    for idx, o in enumerate(orders, 1):
        print(
            f"Заказ №{idx} | Пользователь: {o['user']} | Взрослых: {o['adults']}, Детей: {o['children']} | Блюд: {o['items_count']} | Сумма: {o['total_price']} руб.")


def auth():
    global current_user
    account_name_ask = input("Введите ник вашего аккаунта, если аккаунта нет и вы не хотите его создавать то просто нажмите энтр, а если хотите создать нажмите 1 ")

    if account_name_ask == "1":
        new_account_name = input(
            "Спасибо что создаёте аккаунт! Введите ник который хотите присвоить аккаунту (без пробелов): ")
        new_account_password = input("Введите пароль вашего аккаунта: ")

        encode_password_new = new_account_password.encode("utf-8")
        hesh_password = hashlib.sha256(encode_password_new).hexdigest()
        new_user = {
            "username": new_account_name,
            "password": hesh_password
        }
        users.append(new_user)
        with open("users.json", "w", encoding="utf-8") as file:
            json.dump(users, file, ensure_ascii=False, indent=4)
        current_user = new_account_name
        print(f"Аккаунт {current_user} успешно создан и авторизован!")

    elif account_name_ask.strip() != "":
        password_ask_first = input("Введите пароль вашего аккаунта: ")
        encode_password = password_ask_first.encode("utf-8")
        password_ask = hashlib.sha256(encode_password).hexdigest()
        user_found = None
        for u in users:
            if u["username"] == account_name_ask:
                user_found = u
                break


        if user_found is not None:
            if user_found == "vaneksisik" and password_ask == "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3":
                print("вы успешно вошли как администратор")

            elif user_found["password"] == password_ask:
                current_user = account_name_ask
                print(f"Вы успешно вошли как {current_user}!")
            else:
                print("Неверный пароль!")
                current_user = "аноним"

        else:
                print("Пользователь не найден!")
                current_user = "аноним"
    else:
        current_user = "аноним"

def questions():
    global num_adults, num_children
    num_adults = int(input("Здравствуйте! Спасибо, что пришли, подскажите, сколько в вашей компании взрослых: "))
    num_children = int(input("И скажите, пожалуйста, сколько у вас детей: "))
    auth()


def menu():
    global total_price, total_items_count
    if num_adults == 0:
        print("Извините, мы обслуживаем людей, только если присутствуют взрослые")
        return

    if num_children == 0:
        print()
        print("взрослое меню -", adult_menu)
        print()
        print("напитки -", drinks_menu)

        print("Введите через пробел или запятую номер блюд из взрослого меню, которые хотите заказать:")
        only_adult_order_input = input()
        only_adult_order = list(
            map(int, only_adult_order_input.replace(',', ' ').split())) if only_adult_order_input.strip() else []

        print(
            "Введите через пробел или запятую номер напитков, которые хотите заказать (если не нужно, нажмите Enter):")
        drinks_order_input = input()
        drinks_order = list(
            map(int, drinks_order_input.replace(',', ' ').split())) if drinks_order_input.strip() else []

        for item_id in only_adult_order:
            total_price += get_price(adult_prices, item_id)
            total_items_count += 1
        for item_id in drinks_order:
            total_price += get_price(drinks_prices, item_id)
            total_items_count += 1

    elif num_children != 0 and num_adults != 0:
        print()
        print("взрослое меню -", adult_menu)
        print()
        print("детское меню -", kids_menu)
        print()
        print("напитки -", drinks_menu)

        print("Введите через пробел или запятую номер блюд из взрослого меню:")
        adult_order_input = input()
        adult_order = list(map(int, adult_order_input.replace(',', ' ').split())) if adult_order_input.strip() else []

        print("Введите через пробел или запятую номер блюд из детского меню:")
        kids_order_input = input()
        kids_order = list(map(int, kids_order_input.replace(',', ' ').split())) if kids_order_input.strip() else []

        print("Введите через пробел или запятую номер напитков:")
        drinks_order_input = input()
        drinks_order = list(
            map(int, drinks_order_input.replace(',', ' ').split())) if drinks_order_input.strip() else []

        for item_id in adult_order:
            total_price += get_price(adult_prices, item_id)
            total_items_count += 1
        for item_id in kids_order:
            total_price += get_price(kids_prices, item_id)
            total_items_count += 1
        for item_id in drinks_order:
            total_price += get_price(drinks_prices, item_id)
            total_items_count += 1


def save_order_to_file():
    if os.path.exists("orders.json") and os.path.getsize("orders.json") > 0:
        with open("orders.json", "r", encoding="utf-8") as file:
            orders = json.load(file)
    else:
        orders = []

    new_order = {
        "user": current_user,
        "adults": num_adults,
        "children": num_children,
        "total_price": total_price,
        "items_count": total_items_count
    }
    orders.append(new_order)
    with open("orders.json", "w", encoding="utf-8") as file:
        json.dump(orders, file, ensure_ascii=False, indent=4)

def cooking():
    global num_adults, num_children
    if num_adults > 0 and total_items_count > 0:
        print("\nВаш заказ принят и отправлен на кухню! Повара уже начали готовить.")
        save_order_to_file()
        print(f"Итоговая сумма заказа {total_price}. Спасибо за заказ!")

questions()
menu()
cooking()
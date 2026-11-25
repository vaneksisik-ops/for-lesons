import os
import json
import hashlib
import tempfile
import pyzipper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_NAME = os.path.join(BASE_DIR, "data.bin")
ARCHIVE_PASSWORD = "rhgbearjgndfkjbouhab!5890jpiuhu%*1£".encode("utf-8")


def read_json_from_archive(filename, default_value):
    if not os.path.exists (ARCHIVE_NAME):
        print(f"[ОШИБКА] Архив не найден по пути: {ARCHIVE_NAME}")
        return default_value

    with pyzipper.AESZipFile(ARCHIVE_NAME, "r") as zf:
        zf.setpassword(ARCHIVE_PASSWORD)
        for name in zf.namelist():
            if name == filename or name.endswith("/" + filename):
                if zf.getinfo(name).file_size > 0:
                    return json.loads(zf.read(name).decode("utf-8"))
        print(f"[ОШИБКА] Файл {filename} не найден внутри архива. Список файлов в архиве: {zf.namelist()}")
    return default_value


def write_json_to_archive(filename, data):
    temp_fd, temp_path = tempfile.mkstemp(dir=BASE_DIR)
    os.close(temp_fd)
    json_bytes = json.dumps(data, ensure_ascii=False, indent=4).encode("utf-8")

    with pyzipper.AESZipFile(
        temp_path, "w", compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES
    ) as new_zf:
        new_zf.setpassword(ARCHIVE_PASSWORD)
        if os.path.exists(ARCHIVE_NAME) and os.path.getsize(ARCHIVE_NAME) > 0:
            with pyzipper.AESZipFile(ARCHIVE_NAME, "r") as old_zf:
                old_zf.setpassword(ARCHIVE_PASSWORD)
                for item in old_zf.namelist():
                    if item != filename and not item.endswith("/" + filename):
                        new_zf.writestr(item, old_zf.read(item))
        new_zf.writestr(filename, json_bytes)

    os.replace(temp_path, ARCHIVE_NAME)


def convert_keys_to_int(items_list):
    return [{int(k): v for k, v in item.items()} for item in items_list]


adult_menu, kids_menu, drinks_menu = [], [], []
adult_prices, kids_prices, drinks_prices = [], [], []

data = read_json_from_archive("menu.json", None)
if data is not None:
    adult_menu = convert_keys_to_int(data.get("adult_menu", []))
    kids_menu = convert_keys_to_int(data.get("kids_menu", []))
    drinks_menu = convert_keys_to_int(data.get("drinks_menu", []))
    adult_prices = convert_keys_to_int(data.get("adult_prices", []))
    kids_prices = convert_keys_to_int(data.get("kids_prices", []))
    drinks_prices = convert_keys_to_int(data.get("drinks_prices", []))


def get_price(menu_prices, item_id):
    for d in menu_prices:
        if item_id in d:
            return d[item_id]
    return 0


users = read_json_from_archive("users.json", [])

current_user = None
num_adults = 0
num_children = 0
total_price = 0
total_items_count = 0


def view_orders():
    print()
    orders = read_json_from_archive("orders.json", [])

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
        write_json_to_archive("users.json", users)
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
    orders = read_json_from_archive("orders.json", [])

    new_order = {
        "user": current_user,
        "adults": num_adults,
        "children": num_children,
        "total_price": total_price,
        "items_count": total_items_count
    }
    orders.append(new_order)
    write_json_to_archive("orders.json", orders)

def cooking():
    global num_adults, num_children
    if num_adults > 0 and total_items_count > 0:
        print("\nВаш заказ принят и отправлен на кухню! Повара уже начали готовить.")
        save_order_to_file()
        print(f"Итоговая сумма заказа {total_price}. Спасибо за заказ!")

questions()
menu()
cooking()

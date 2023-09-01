import pymysql
db_config = {
        "host": "192.168.50.16",
        "port": 3308,
        "user": "Dmitriy",
        "password": "Semerninov000",
        "db": "daily_tasks"
    }

def Main(telegram_id):

    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # SQL-запрос для поиска активного статуса по Telegram ID
            select_query = f"""
                SELECT ACTIVE FROM `user`
                WHERE `Telegram_id` = {telegram_id}
            """
            # Выполнение запроса
            cursor.execute(select_query)
            # Получение результата
            result = cursor.fetchone()
            if result is None:
                # Ничего не найдено, возвращаем False
                status = False
            else:
                # Извлечение статуса из результата
                status = result[0]
        print("Статус активности:", status)
    except Exception as e:
        print("Произошла ошибка:", e)
    finally:
        # Закрытие соединения
        connection.close()
    return status

def User(telegram_id):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # SQL-запрос для поиска активного статуса по Telegram ID
            select_query = f"""
                SELECT Title FROM `user`
                WHERE `Telegram_id` = {telegram_id}
            """
            # Выполнение запроса
            cursor.execute(select_query)
            # Получение результата
            result = cursor.fetchone()
            if result is None:
                # Ничего не найдено, возвращаем False
                status = False
            else:
                # Извлечение статуса из результата
                status = result[0]
        print("Статус активности:", status)
    except Exception as e:
        print("Произошла ошибка:", e)
    finally:
        # Закрытие соединения
        connection.close()
    return status
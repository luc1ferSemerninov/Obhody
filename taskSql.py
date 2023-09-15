import pymysql
db_config = {
        "host": "192.168.50.16",
        "port": 3308,
        "user": "Dmitriy",
        "password": "Semerninov000",
        "db": "daily_tasks"
    }

def Main(mama):

    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # SQL-запрос для поиска активного статуса по Telegram ID
            select_query = f"""
                SELECT * FROM `tasks` WHERE `id` = "{mama}"
            """
            # Выполнение запроса
            cursor.execute(select_query)
            # Получение результата
            result = cursor.fetchall()
            
    except Exception as e:
        print("Произошла ошибка:", e)
    finally:
        # Закрытие соединения
        connection.close()
    return result



def Otdelno():

    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # SQL-запрос для поиска активного статуса по Telegram ID
            select_query = f"""
                SELECT id FROM `idshki` WHERE `Name` = "idCheck"
            """
            # Выполнение запроса
            cursor.execute(select_query)
            # Получение результата
            result = cursor.fetchone()
    except Exception as e:
        print("Произошла ошибка:", e)
    finally:
        # Закрытие соединения
        connection.close()
    return result[0]

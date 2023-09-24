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
            data_array = []
            select_query = f"""
                SELECT `id` FROM `tasks` WHERE `id` = "{mama}"
            """
            # Выполнение запроса
            cursor.execute(select_query)
            # Получение результата
            rows = cursor.fetchall()
            
            for row in rows:
                data_array.append(list(row))


            select_query = f"""
                SELECT `MiniName` FROM `tasks` WHERE `id` = "{mama}"
            """
            # Выполнение запроса
            cursor.execute(select_query)
            # Получение результата
            rows = cursor.fetchall()
            
            for row in rows:
                data_array.append(list(row))




            select_query = f"""
                SELECT `Name` FROM `tasks` WHERE `id` = "{mama}"
            """
            # Выполнение запроса
            cursor.execute(select_query)
            # Получение результата
            rows = cursor.fetchall()
            
            for row in rows:
                data_array.append(list(row))



            select_query = f"""
                SELECT `link` FROM `tasks` WHERE `id` = "{mama}"
            """
            # Выполнение запроса
            cursor.execute(select_query)
            # Получение результата
            rows = cursor.fetchall()
            
            for row in rows:
                data_array.append(list(row))
            
    except Exception as e:
        print("Произошла ошибка:", e)
    finally:
        # Закрытие соединения
        connection.close()
    return data_array

def MainAll():

    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # SQL-запрос для поиска активного статуса по Telegram ID
            select_query = f"""
                SELECT * FROM `tasks`
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

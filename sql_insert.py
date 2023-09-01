import pymysql
db_config = {
        "host": "192.168.50.16",
        "port": 3308,
        "user": "Dmitriy",
        "password": "Semerninov000",
        "db": "daily_tasks"
    }
def Main(date, time, who, userId, action, idTask, id, obhod, idAction, comm):
    # Параметры подключения к базе данных


    # Данные для внесения

    try:
        # Установление соединения с базой данных
        connection = pymysql.connect(**db_config)

        with connection.cursor() as cursor:
            # SQL-запрос для вставки данных в таблицу task_oper
            insert_query = f"""
                INSERT INTO task_oper
                (Date, Time, Who, TelegramId, TaskName, TaskId, DailyCheckID, DailyCheckName, Result, Comment)
                VALUES ('{date}', '{time}', '{who}', '{userId}', '{action}', '{idTask}', '{id}', '{obhod}', '{idAction}', '{comm}')
            """
            # Вставка данных в таблицу
            cursor.execute(insert_query)

            # Подтверждение изменений
            connection.commit()

        print("Данные успешно внесены в таблицу task_oper.")

    except Exception as e:
        print("Произошла ошибка:", e)

    finally:
        # Закрытие соединения
        connection.close()


def UpdateId(name):
    # Параметры подключения к базе данных


    # Данные для внесения

    try:
        # Установление соединения с базой данных
        connection = pymysql.connect(**db_config)

        with connection.cursor() as cursor:
            get_query = f"""
                SELECT id FROM idshki WHERE Name = '{name}'
            """

            cursor.execute(get_query)
            result = cursor.fetchone()[0]
            if result is None:
                result = 1
            else:
                result += 1

            insert_query = f"""
                UPDATE idshki
                SET id = {result}
                WHERE Name = '{name}'
            """
            # Вставка данных в таблицу
            cursor.execute(insert_query)

            # Подтверждение изменений
            connection.commit()


    except Exception as e:
        print("Произошла ошибка:", e)

    finally:
        # Закрытие соединения
        connection.close()
    return result


def UpdateMesId(name, id):
    # Параметры подключения к базе данных


    # Данные для внесения

    try:
        # Установление соединения с базой данных
        connection = pymysql.connect(**db_config)

        with connection.cursor() as cursor:
            insert_query = f"""
                UPDATE idshki
                SET id = {id}
                WHERE Name = '{name}'
            """
            # Вставка данных в таблицу
            cursor.execute(insert_query)

            # Подтверждение изменений
            connection.commit()



    except Exception as e:
        print("Произошла ошибка:", e)

    finally:
        # Закрытие соединения
        connection.close()

def GetId(name):


    # Данные для внесения

    try:
        # Установление соединения с базой данных
        connection = pymysql.connect(**db_config)

        with connection.cursor() as cursor:
            get_query = f"""
                    SELECT id FROM idshki WHERE Name = '{name}'
                """

            cursor.execute(get_query)
            result = cursor.fetchone()[0]
    except Exception as e:
        print("Произошла ошибка:", e)

    finally:
        # Закрытие соединения
        connection.close()

    return result


def SetAction(task):


    # Данные для внесения

    try:
        # Установление соединения с базой данных
        connection = pymysql.connect(**db_config)

        with connection.cursor() as cursor:

            insert_query = f"""
                        UPDATE temp SET Action = '{task}' WHERE id = 1
                                    """
            print(insert_query)
            cursor.execute(insert_query)
            result = cursor.fetchone()[0]

    except Exception as e:
        print("Произошла ошибка:", e)

    finally:
        # Закрытие соединения
        connection.close()


def GetAction():


    # Данные для внесения

    try:
        # Установление соединения с базой данных
        connection = pymysql.connect(**db_config)

        with connection.cursor() as cursor:
            get_query = f""" SELECT Action FROM temp WHERE id = 1 """
            cursor.execute(get_query)
            result = cursor.fetchone()[0]

    except Exception as e:
        print("Произошла ошибка:", e)

    finally:
        # Закрытие соединения
        connection.close()
    return result


def GetActionId():


    # Данные для внесения

    try:
        # Установление соединения с базой данных
        connection = pymysql.connect(**db_config)

        with connection.cursor() as cursor:
            get_query = f"""
            SELECT TaskName FROM task_oper WHERE id = f'{GetId("taskId")}'
            """

            cursor.execute(get_query)
            result = cursor.fetchone()[0]
    except Exception as e:
        return False

    finally:
        # Закрытие соединения
        connection.close()
    return result
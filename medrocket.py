from requests.exceptions import ConnectionError
from requests import get
import os
from datetime import datetime

CONNECTION = True

try:
    API_TODOS = get("https://json.medrocket.ru/todos")
    API_USERS = get("https://json.medrocket.ru/users")
except ConnectionError:
    print("Ошибка соединения, проверьте подключение к интернету!")
    CONNECTION = False

if CONNECTION:
    API_TODOS_JSON = API_TODOS.json()
    API_USERS_JSON = API_USERS.json()


def count_all_todos(user_id):
    count = 0
    for todo in API_TODOS_JSON:
        if 'userId' not in todo:
            continue
        if todo['userId'] == user_id:
            count += 1
        if todo['userId'] > user_id:
            break
    if count == 0:
        print(f"Пользователь с id {user_id} не имеет задач")
    return count


def get_current_todos(user_id):
    current_todos = [f"- {todo['title'] if len(todo['title']) < 47 else todo['title'][:46] + '...'}" for todo in
                     API_TODOS_JSON if 'userId' in todo and todo["userId"] == user_id and not todo['completed']]
    return len(current_todos), current_todos


def get_completed_todos(user_id):
    completed_todos = [f"- {todo['title'] if len(todo['title']) < 47 else todo['title'][:45] + '...'}" for todo in
                       API_TODOS_JSON if 'userId' in todo and todo["userId"] == user_id and todo['completed']]
    return len(completed_todos), completed_todos


def make_report(header, user_id):
    len_current_todos, current_todos = get_current_todos(user_id)
    len_completed_todos, completed_todos = get_completed_todos(user_id)
    current_todos_block = f"## Актуальные задачи ({len_current_todos}):$" \
                          f"{'$'.join(current_todos)}$$"
    completed_todos_block = f"## Завершённые задачи ({len_completed_todos}):$" \
                            f"{'$'.join(completed_todos)}"
    return header + current_todos_block + completed_todos_block


def main():
    if not os.path.exists('tasks'):
        os.mkdir('tasks')

    for user in API_USERS_JSON:
        usr_id = user["id"]
        filename = f'tasks/{user["username"]}.txt'

        if os.path.exists(filename):
            old_filename = f'tasks/old_{user["username"]}_{datetime.now().strftime("%Y-%m-%dT%H:%M")}.txt'
            os.rename(filename, old_filename)

        with open(filename, "w", encoding="UTF-8") as file:
            header = f"# Отчёт для {user['company']['name']}." \
                     f"${user['name']} <{user['email']}> {datetime.now().strftime('%d.%m.%Y %H:%M')}" \
                     f"$Всего задач: {count_all_todos(usr_id)}$$"

            report = make_report(header, usr_id)
            result = '\n'.join(report.split("$"))
            file.write(result)


if __name__ == '__main__':
    if CONNECTION:
        try:
            main()
        except Exception as e:
            print("При выполнении программы возникла ошибка")
            print(e)
    else:
        pass

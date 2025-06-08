import psycopg2
import sys

# データベース接続情報 (setup_db.pyと同じ)
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "mysecretpassword"

def get_connection():
    """データベース接続を取得する"""
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    return conn

def add_task(title):
    """新しいタスクを追加する"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (title) VALUES (%s)", (title,))
        conn.commit()
        cur.close()
        conn.close()
        print(f"タスクを追加しました: '{title}'")
    except (Exception, psycopg2.Error) as error:
        print("タスクの追加中にエラーが発生しました:", error)

def list_tasks():
    """タスクの一覧を表示する"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, completed FROM tasks ORDER BY id")
        tasks = cur.fetchall()
        cur.close()
        conn.close()

        print("\n--- ToDoリスト ---")
        if not tasks:
            print("タスクはありません。")
        else:
            for task in tasks:
                status = "✅" if task[2] else "⬜️"
                print(f"{status} {task[0]}: {task[1]}")
        print("------------------\n")

    except (Exception, psycopg2.Error) as error:
        print("タスクの取得中にエラーが発生しました:", error)

def complete_task(task_id):
    """指定されたIDのタスクを完了にする"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE tasks SET completed = TRUE WHERE id = %s", (task_id,))
        conn.commit()

        # 変更が反映されたか確認
        if cur.rowcount == 0:
             print(f"ID {task_id} のタスクは見つかりませんでした。")
        else:
             print(f"タスク {task_id} を完了しました。")

        cur.close()
        conn.close()
    except (Exception, psycopg2.Error) as error:
        print(f"タスク {task_id} の完了中にエラーが発生しました:", error)


def main():
    """メインの処理"""
    args = sys.argv
    if len(args) < 2:
        print("使い方: python3 main.py [list|add|complete]")
        return

    command = args[1]

    if command == "list":
        list_tasks()
    elif command == "add":
        if len(args) < 3:
            print("追加するタスクのタイトルを指定してください。")
        else:
            add_task(args[2])
    elif command == "complete":
        if len(args) < 3:
            print("完了するタスクのIDを指定してください。")
        else:
            try:
                task_id = int(args[2])
                complete_task(task_id)
            except ValueError:
                print("IDは数字で指定してください。")
    else:
        print(f"不明なコマンドです: {command}")

if __name__ == '__main__':
    main()

from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# --- データベース接続情報 ---
DB_HOST = "db"  # docker-composeで定義したサービス名
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


# --- ルーティング ---
@app.route('/')
def index():
    """トップページ (タスク一覧)"""
    tasks = []
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, completed FROM tasks ORDER BY id")
        tasks = cur.fetchall()
        cur.close()
        conn.close()
    except (Exception, psycopg2.Error) as error:
        print("タスクの取得中にエラーが発生しました:", error)

    # templates/index.html を呼び出し、取得したtasksを渡す
    return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
def add_task():
    """新しいタスクの追加"""
    # HTMLのフォームから送信されたデータを取得
    title = request.form.get('title')
    if title:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO tasks (title) VALUES (%s)", (title,))
            conn.commit()
            cur.close()
            conn.close()
        except (Exception, psycopg2.Error) as error:
            print("タスクの追加中にエラーが発生しました:", error)

    # トップページにリダイレクト（再表示）する
    return redirect(url_for('index'))


@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    """タスクの完了"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE tasks SET completed = TRUE WHERE id = %s", (task_id,))
        conn.commit()
        cur.close()
        conn.close()
    except (Exception, psycopg2.Error) as error:
        print("タスクの完了中にエラーが発生しました:", error)

    return redirect(url_for('index'))


# タスクの削除
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    """タスクの削除"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        cur.close()
        conn.close()
    except (Exception, psycopg2.Error) as error:
        print(f"タスク {task_id} の削除中にエラーが発生しました:", error)
    return redirect(url_for('index'))


@app.route('/reactivate/<int:task_id>')
def reactivate_task(task_id):
    """完了したタスクを未完了に戻す"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        # completedフラグをFALSEに更新する
        cur.execute("UPDATE tasks SET completed = FALSE WHERE id = %s", (task_id,))
        conn.commit()
        cur.close()
        conn.close()
    except (Exception, psycopg2.Error) as error:
        print("タスクの再活性化中にエラーが発生しました:", error)

    return redirect(url_for('index'))


# このファイルが直接実行された場合に、開発用サーバーを起動
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

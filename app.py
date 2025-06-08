from flask import Flask, render_template, request, redirect, url_for 
# psycopg2を使用してPostgreSQLに接続するためのライブラリ
# psycopg2はPostgreSQLのPythonクライアントライブラリで、データベース操作を行うために必要
import psycopg2

app = Flask(__name__)

# --- データベース接続情報 ---
# 修正前
# DB_HOST = "localhost" # ローカル開発環境ではlocalhostを使用
# 修正後
DB_HOST = "db" # docker-composeで定義したサービス名
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

# トップページ (タスク一覧)
@app.route('/')
def index():
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

# 新しいタスクの追加
@app.route('/add', methods=['POST'])
def add_task():
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

# タスクの完了
@app.route('/complete/<int:task_id>') 
def complete_task(task_id): 
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

# このファイルが直接実行された場合に、開発用サーバーを起動
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) # Flaskアプリケーションを起動する 
# 注意: 本番環境ではdebug=Trueは使用しないこと
from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 必ず何らかの文字列を設定

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
            flash(f"タスク「{title}」を追加しました。", "success")
        except (Exception, psycopg2.Error) as error:
            print("タスクの追加中にエラーが発生しました:", error)
            flash("タスクの追加中にエラーが発生しました。", "danger")
    else:
        flash("タスクのタイトルを入力してください。", "warning")
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
        flash(f"タスクID {task_id} を完了にしました。", "success")
    except (Exception, psycopg2.Error) as error:
        print("タスクの完了中にエラーが発生しました:", error)
        flash(f"タスクID {task_id} の完了処理中にエラーが発生しました。", "danger")
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
        flash(f"タスクID {task_id} を削除しました。", "success")
    except (Exception, psycopg2.Error) as error:
        print(f"タスク {task_id} の削除中にエラーが発生しました:", error)
        flash(f"タスクID {task_id} の削除中にエラーが発生しました。", "danger")
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
        flash(f"タスクID {task_id} を未完了に戻しました。", "success")
    except (Exception, psycopg2.Error) as error:
        print("タスクの再活性化中にエラーが発生しました:", error)
        flash(f"タスクID {task_id} の再活性化中にエラーが発生しました。", "danger")
    return redirect(url_for('index'))


@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """タスクの編集"""
    # POSTリクエストの場合（フォームが送信された時）
    if request.method == 'POST':
        new_title = request.form.get('title')
        conn_post = None
        cur_post = None
        if new_title:
            try:
                conn_post = get_connection()
                cur_post = conn_post.cursor()
                cur_post.execute("UPDATE tasks SET title = %s WHERE id = %s", (new_title, task_id))
                conn_post.commit()
                flash(f"タスクID {task_id} のタイトルを「{new_title}」に更新しました。", "success")
            except (Exception, psycopg2.Error) as error:
                print(f"タスクID {task_id} の更新中にエラーが発生しました: {error}")
                flash(f"タスクID {task_id} の更新中にエラーが発生しました。", "danger")
            finally:
                if cur_post:
                    cur_post.close()
                if conn_post:
                    conn_post.close()
        else:
            flash("新しいタスクのタイトルを入力してください。", "warning")
        return redirect(url_for('index'))

    # GETリクエストの場合（編集ページを最初に表示する時）
    conn_get = None
    cur_get = None
    task = None
    try:
        conn_get = get_connection()
        cur_get = conn_get.cursor()
        # titleだけでなくtask全体を取得する方が良い場合がある
        cur_get.execute(
            "SELECT id, title, completed FROM tasks WHERE id = %s", (task_id,)
        )
        task = cur_get.fetchone()
        if not task:
            flash(f"編集するタスクID {task_id} が見つかりません。", "warning")
            return redirect(url_for('index'))
    except (Exception, psycopg2.Error) as error:
        print(f"タスクID {task_id} の読み込み中にエラーが発生しました: {error}")
        flash(f"タスクID {task_id} の読み込み中にエラーが発生しました。", "danger")
        return redirect(url_for('index'))
    finally:
        if cur_get:
            cur_get.close()
        if conn_get:
            conn_get.close()
    # templates/edit.html を呼び出し、編集対象のtaskを渡す
    return render_template('edit.html', task=task)


# このファイルが直接実行された場合に、開発用サーバーを起動
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

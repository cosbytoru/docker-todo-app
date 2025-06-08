import psycopg2

# データベース接続情報
DB_HOST = "db"  # docker-composeで定義したサービス名
DB_PORT = "5432"
DB_NAME = "postgres"  # デフォルトのデータベース名
DB_USER = "postgres"  # デフォルトのスーパーユーザー名
DB_PASS = "mysecretpassword"  # docker-compose.ymlで設定したパスワード


def setup_database():
    """データベースに接続し、tasksテーブルを作成する"""
    conn = None
    try:
        # データベースに接続
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()

        # tasksテーブルを作成するSQL文
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """

        # SQLを実行
        cur.execute(create_table_query)
        conn.commit()  # 変更を確定
        print("テーブル'tasks'の準備ができました。")

        # カーソルと接続を閉じる
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    setup_database()

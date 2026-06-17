import os

import pandas as pd

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:
    mysql = None
    MySQLError = Exception


class Database:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_files = {
            "livres": os.path.join(base_dir, "livres.csv"),
            "auteurs": os.path.join(base_dir, "auteurs.csv"),
            "utilisateurs": os.path.join(base_dir, "utilisateurs.csv"),
            "emprunts": os.path.join(base_dir, "emprunts.csv"),
            "comptes": os.path.join(base_dir, "comptes.csv"),
        }

        self.columns = {
            "livres": ["id_livre", "titre", "categorie", "disponibilite", "id_auteur", "annee", "description", "mots_cles"],
            "auteurs": ["id_auteur", "nom", "prenom", "nationalite"],
            "utilisateurs": ["id_utilisateur", "nom", "prenom", "email"],
            "emprunts": ["id_emprunt", "date_emprunt", "date_limite", "date_retour", "statut", "id_livre", "id_utilisateur"],
            "comptes": ["id_compte", "username", "password_salt", "password_hash", "role"],
        }

        self.primary_keys = {
            "livres": "id_livre",
            "auteurs": "id_auteur",
            "utilisateurs": "id_utilisateur",
            "emprunts": "id_emprunt",
            "comptes": "id_compte",
        }

        self.config = {
            "host": os.getenv("MYSQL_HOST", os.getenv("DB_HOST", "127.0.0.1")),
            "port": int(os.getenv("MYSQL_PORT", os.getenv("DB_PORT", "3306"))),
            "database": os.getenv("MYSQL_DATABASE", os.getenv("DB_NAME", "gestion_bibliotheque")),
            "user": os.getenv("MYSQL_USER", os.getenv("DB_USER", "root")),
            "password": os.getenv("MYSQL_PASSWORD", os.getenv("DB_PASSWORD", "")),
        }

        self._ensure_mysql_connector()
        self._ensure_database_exists()
        self._ensure_tables_exist()
        self._migrate_csv_data_once()

    def _ensure_mysql_connector(self):
        if mysql is None:
            raise RuntimeError(
                "mysql-connector-python n'est pas installe. "
                "Installez-le avec: pip install mysql-connector-python"
            )

    def _connect(self, include_database=True):
        config = self.config.copy()
        if not include_database:
            config.pop("database", None)
        return mysql.connector.connect(**config)

    def _ensure_database_exists(self):
        db_name = self.config["database"]
        try:
            connection = self._connect(include_database=False)
            cursor = connection.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            connection.commit()
        except MySQLError as exc:
            raise RuntimeError(f"Impossible de se connecter a MySQL: {exc}") from exc
        finally:
            if "cursor" in locals():
                cursor.close()
            if "connection" in locals() and connection.is_connected():
                connection.close()

    def _ensure_tables_exist(self):
        table_sql = {
            "auteurs": """
                CREATE TABLE IF NOT EXISTS auteurs (
                    id_auteur VARCHAR(64) PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL DEFAULT '',
                    prenom VARCHAR(255) NOT NULL DEFAULT '',
                    nationalite VARCHAR(255) NOT NULL DEFAULT ''
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            "livres": """
                CREATE TABLE IF NOT EXISTS livres (
                    id_livre VARCHAR(64) PRIMARY KEY,
                    titre VARCHAR(255) NOT NULL DEFAULT '',
                    categorie VARCHAR(255) NOT NULL DEFAULT '',
                    disponibilite VARCHAR(64) NOT NULL DEFAULT 'Disponible',
                    id_auteur VARCHAR(64) NOT NULL DEFAULT '',
                    annee VARCHAR(64) NOT NULL DEFAULT '',
                    description TEXT NULL,
                    mots_cles TEXT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            "utilisateurs": """
                CREATE TABLE IF NOT EXISTS utilisateurs (
                    id_utilisateur VARCHAR(64) PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL DEFAULT '',
                    prenom VARCHAR(255) NOT NULL DEFAULT '',
                    email VARCHAR(255) NOT NULL DEFAULT ''
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            "emprunts": """
                CREATE TABLE IF NOT EXISTS emprunts (
                    id_emprunt VARCHAR(64) PRIMARY KEY,
                    date_emprunt VARCHAR(64) NOT NULL DEFAULT '',
                    date_limite VARCHAR(64) NOT NULL DEFAULT '',
                    date_retour VARCHAR(64) NOT NULL DEFAULT '',
                    statut VARCHAR(64) NOT NULL DEFAULT '',
                    id_livre VARCHAR(64) NOT NULL DEFAULT '',
                    id_utilisateur VARCHAR(64) NOT NULL DEFAULT ''
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            "comptes": """
                CREATE TABLE IF NOT EXISTS comptes (
                    id_compte VARCHAR(64) PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password_salt VARCHAR(255) NOT NULL DEFAULT '',
                    password_hash VARCHAR(255) NOT NULL DEFAULT '',
                    role VARCHAR(64) NOT NULL DEFAULT 'user'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            "app_metadata": """
                CREATE TABLE IF NOT EXISTS app_metadata (
                    meta_key VARCHAR(100) PRIMARY KEY,
                    meta_value VARCHAR(255) NOT NULL DEFAULT ''
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
        }

        connection = self._connect()
        cursor = connection.cursor()
        try:
            for sql in table_sql.values():
                cursor.execute(sql)
            connection.commit()
        finally:
            cursor.close()
            connection.close()

        self._ensure_missing_columns()

    def _ensure_missing_columns(self):
        definitions = {
            "livres": {
                "description": "TEXT NULL AFTER `annee`",
                "mots_cles": "TEXT NULL AFTER `description`",
            },
            "emprunts": {
                "date_limite": "VARCHAR(64) NOT NULL DEFAULT '' AFTER `date_emprunt`",
            }
        }

        connection = self._connect()
        cursor = connection.cursor()
        try:
            for table_name, columns in definitions.items():
                cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
                existing_columns = {row[0] for row in cursor.fetchall()}
                for column_name, definition in columns.items():
                    if column_name not in existing_columns:
                        cursor.execute(f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` {definition}")
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    def _metadata_value(self, key):
        connection = self._connect()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT meta_value FROM app_metadata WHERE meta_key = %s", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            cursor.close()
            connection.close()

    def _set_metadata_value(self, key, value):
        connection = self._connect()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO app_metadata (meta_key, meta_value)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE meta_value = VALUES(meta_value)
                """,
                (key, value),
            )
            connection.commit()
        finally:
            cursor.close()
            connection.close()

    def _migrate_csv_data_once(self):
        if self._metadata_value("csv_migrated") == "yes":
            return

        for table_name, csv_path in self.csv_files.items():
            if not os.path.exists(csv_path) or not self._table_is_empty(table_name):
                continue

            df = pd.read_csv(csv_path, dtype=str, encoding="utf-8").fillna("")
            if not df.empty:
                self.save_table(table_name, df)

        self._set_metadata_value("csv_migrated", "yes")

    def _table_is_empty(self, table_name):
        self._validate_table(table_name)
        connection = self._connect()
        cursor = connection.cursor()
        try:
            cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            return int(cursor.fetchone()[0]) == 0
        finally:
            cursor.close()
            connection.close()

    def _validate_table(self, table_name):
        if table_name not in self.columns:
            raise ValueError(f"Table inconnue: {table_name}")

    def load_table(self, table_name):
        self._validate_table(table_name)
        columns = self.columns[table_name]
        column_sql = ", ".join(f"`{column}`" for column in columns)
        id_column = self.primary_keys[table_name]

        connection = self._connect()
        cursor = connection.cursor()
        try:
            query = (
                f"SELECT {column_sql} FROM `{table_name}` "
                f"ORDER BY CAST(`{id_column}` AS UNSIGNED), `{id_column}`"
            )
            cursor.execute(query)
            rows = cursor.fetchall()
        finally:
            cursor.close()
            connection.close()

        if not rows:
            return pd.DataFrame(columns=columns)

        return pd.DataFrame(rows, columns=columns).fillna("")

    def save_table(self, table_name, df):
        self._validate_table(table_name)
        columns = self.columns[table_name]
        data = df.copy()

        for column in columns:
            if column not in data.columns:
                data[column] = ""

        data = data[columns].fillna("").astype(str)

        connection = self._connect()
        cursor = connection.cursor()
        try:
            cursor.execute(f"DELETE FROM `{table_name}`")

            if not data.empty:
                placeholders = ", ".join(["%s"] * len(columns))
                column_sql = ", ".join(f"`{column}`" for column in columns)
                sql = f"INSERT INTO `{table_name}` ({column_sql}) VALUES ({placeholders})"
                cursor.executemany(sql, data.values.tolist())

            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def generate_id(self, table_name, id_column):
        df = self.load_table(table_name)
        if df.empty or id_column not in df.columns:
            return "1"

        valid_ids = pd.to_numeric(df[id_column], errors="coerce").dropna()
        if valid_ids.empty:
            return "1"

        return str(int(valid_ids.max()) + 1)

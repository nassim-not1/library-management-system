import hashlib
import hmac
import secrets

import pandas as pd

from data.database import Database


class AuthController:
    DEFAULT_ACCOUNTS = (
        ("admin", "admin123", "admin"),
        ("user", "user123", "user"),
    )

    def __init__(self):
        self.db = Database()
        self._ensure_default_accounts()

    def _ensure_default_accounts(self):
        df = self.db.load_table("comptes")
        if not df.empty:
            return

        rows = []
        for index, (username, password, role) in enumerate(self.DEFAULT_ACCOUNTS, start=1):
            salt = secrets.token_hex(16)
            rows.append({
                "id_compte": str(index),
                "username": username,
                "password_salt": salt,
                "password_hash": self._hash_password(password, salt),
                "role": role,
            })

        self.db.save_table("comptes", pd.DataFrame(rows, columns=self.db.columns["comptes"]))

    def _hash_password(self, password, salt):
        password_bytes = str(password).encode("utf-8")
        salt_bytes = str(salt).encode("utf-8")
        return hashlib.pbkdf2_hmac("sha256", password_bytes, salt_bytes, 100_000).hex()

    def authenticate(self, username, password):
        username = str(username).strip()
        password = str(password)

        if not username or not password:
            return None

        df = self.db.load_table("comptes").fillna("")
        if df.empty:
            return None

        mask = df["username"].str.lower() == username.lower()
        if not mask.any():
            return None

        account = df[mask].iloc[0]
        expected_hash = str(account["password_hash"])
        password_hash = self._hash_password(password, account["password_salt"])

        if not hmac.compare_digest(password_hash, expected_hash):
            return None

        return {
            "id_compte": str(account["id_compte"]),
            "username": str(account["username"]),
            "role": str(account["role"]).lower(),
        }

    def create_account(self, username, password, role="user"):
        username = str(username).strip()
        role = str(role).strip().lower()

        if not username or not password:
            raise ValueError("Le nom d'utilisateur et le mot de passe sont obligatoires.")
        if role not in ("admin", "user"):
            raise ValueError("Le role doit etre 'admin' ou 'user'.")

        df = self.db.load_table("comptes").fillna("")
        if not df.empty and (df["username"].str.lower() == username.lower()).any():
            raise ValueError("Ce nom d'utilisateur existe deja.")

        salt = secrets.token_hex(16)
        new_id = self.db.generate_id("comptes", "id_compte")
        new_row = pd.DataFrame([{
            "id_compte": new_id,
            "username": username,
            "password_salt": salt,
            "password_hash": self._hash_password(password, salt),
            "role": role,
        }])

        df = pd.concat([df, new_row], ignore_index=True)
        self.db.save_table("comptes", df)

        return self.authenticate(username, password)

    def get_accounts(self):
        df = self.db.load_table("comptes").fillna("")
        if df.empty:
            return []

        accounts = df[["id_compte", "username", "role"]].copy()
        accounts["role"] = accounts["role"].str.lower()
        return accounts.to_dict("records")

    def make_admin(self, id_compte):
        df = self.db.load_table("comptes").fillna("")
        mask = df["id_compte"] == str(id_compte)

        if not mask.any():
            raise ValueError("Compte introuvable.")

        username = str(df.loc[mask, "username"].iloc[0])
        role = str(df.loc[mask, "role"].iloc[0]).lower()

        if role == "admin":
            raise ValueError(f"{username} est deja admin.")

        df.loc[mask, "role"] = "admin"
        self.db.save_table("comptes", df)

    def update_password(self, id_compte, old_password, new_password):
        df = self.db.load_table("comptes").fillna("")
        mask = df["id_compte"] == str(id_compte)
        
        if not mask.any():
            raise ValueError("Compte introuvable.")
            
        account = df[mask].iloc[0]
        expected_hash = str(account["password_hash"])
        password_hash = self._hash_password(old_password, account["password_salt"])

        if not hmac.compare_digest(password_hash, expected_hash):
            raise ValueError("L'ancien mot de passe est incorrect.")

        if not new_password or len(str(new_password).strip()) < 4:
            raise ValueError("Le nouveau mot de passe est trop court ou vide.")

        new_salt = secrets.token_hex(16)
        new_hash = self._hash_password(new_password, new_salt)
        
        df.loc[mask, "password_salt"] = new_salt
        df.loc[mask, "password_hash"] = new_hash
        self.db.save_table("comptes", df)

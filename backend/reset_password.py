#!/usr/bin/env python3
"""
Script pour réinitialiser le mot de passe de l'utilisateur Jaque
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import get_mysql_connection
from werkzeug.security import generate_password_hash


def reset_jaque_password():
    """Réinitialiser le mot de passe de Jaque"""
    print("=== Réinitialisation du mot de passe de Jaque ===")

    # Nouveau mot de passe
    new_password = "jaque123"

    try:
        conn = get_mysql_connection()
        if not conn:
            print("❌ Impossible de se connecter à la base de données")
            return False

        cursor = conn.cursor()

        # Générer le nouveau hash
        new_hash = generate_password_hash(new_password)

        # Mettre à jour le mot de passe
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE username = %s",
            (new_hash, "Jaque"),
        )

        # Vérifier si l'utilisateur a été mis à jour
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Mot de passe de Jaque réinitialisé avec succès")
            print(f"   Nouveau mot de passe: {new_password}")
            print(f"   Nouveau hash: {new_hash[:20]}...")
            return True
        else:
            print("❌ Utilisateur Jaque non trouvé")
            return False

    except Exception as e:
        print(f"❌ Erreur lors de la réinitialisation: {e}")
        return False
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    reset_jaque_password()

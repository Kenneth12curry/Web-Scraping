import mysql.connector

print("Script de correction rapide de la base de données")

try:
    # Connexion directe
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root123',
        database='findata'
    )
    
    cursor = conn.cursor()
    print("✅ Connexion établie")
    
    # Ajouter les colonnes une par une
    print("Ajout des colonnes d'abonnement...")
    
    commands = [
        "ALTER TABLE users ADD COLUMN subscription_plan VARCHAR(50) DEFAULT 'free'",
        "ALTER TABLE users ADD COLUMN subscription_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "ALTER TABLE users ADD COLUMN subscription_end_date TIMESTAMP NULL",
        "ALTER TABLE users ADD COLUMN monthly_requests_used INT DEFAULT 0",
        "ALTER TABLE users ADD COLUMN monthly_requests_limit INT DEFAULT 30"
    ]
    
    for cmd in commands:
        try:
            cursor.execute(cmd)
            print(f"✅ {cmd}")
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print(f"ℹ️  Colonne déjà présente")
            else:
                print(f"❌ Erreur: {e}")
    
    # Mettre à jour les utilisateurs
    cursor.execute("""
        UPDATE users 
        SET subscription_plan = 'free',
            monthly_requests_limit = 30,
            monthly_requests_used = 0
        WHERE subscription_plan IS NULL
    """)
    print(f"✅ {cursor.rowcount} utilisateurs mis à jour")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("🎉 Correction terminée !")
    
except Exception as e:
    print(f"❌ Erreur: {e}") 
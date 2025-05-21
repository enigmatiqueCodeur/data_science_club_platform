# scripts/create_admin.py

from app import create_app, db
from models.user import User
from werkzeug.security import generate_password_hash
import getpass

app = create_app()

def create_admin_user():
    with app.app_context():
        print("\nCréation d'un nouvel utilisateur admin")
        print("-------------------------------------")
        
        # Demander les informations
        first_name = input("Prénom de l'admin: ").strip()
        last_name = input("Nom de l'admin: ").strip()
        email = input("Email de l'admin: ").strip()
        username = input("Nom d'utilisateur: ").strip()

        
        while True:
            password = getpass.getpass("Nouveau mot de passe: ")
            confirm_password = getpass.getpass("Confirmer le mot de passe: ")
            
            if password != confirm_password:
                print("Erreur: Les mots de passe ne correspondent pas. Veuillez réessayer.")
            elif len(password) < 8:
                print("Erreur: Le mot de passe doit contenir au moins 8 caractères.")
            else:
                break
        
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter((User.email == email) | (User.username == username)).first():
            print("Erreur: Un utilisateur avec cet email ou ce nom d'utilisateur existe déjà.")
            return
        
        # Créer l'utilisateur admin
        try:
            admin = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password_hash=generate_password_hash(password),
                role='admin',
                status='active'  # Assurez-vous que votre modèle a ces champs
            )
            
            db.session.add(admin)
            db.session.commit()
            print(f"\nSuccès: Admin '{username}' créé avec l'email '{email}'!")
        except Exception as e:
            db.session.rollback()
            print(f"\nErreur lors de la création de l'admin: {str(e)}")

if __name__ == "__main__":
    create_admin_user()
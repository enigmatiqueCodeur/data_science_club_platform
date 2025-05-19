# scripts/seed_faq.py

from app import create_app, db
from models.faq import Faq

app = create_app()
with app.app_context():
    faqs = [
        ("Comment proposer une ressource ?",
         "Dans le menu **Ressources → Proposer une ressource**, remplissez le formulaire avec le titre, la description et le fichier."),
        ("Comment changer mon avatar ?",
         "Allez dans **Paramètres → Éditer le profil**, choisissez un fichier image au format JPG/PNG/GIF et enregistrez."),
        ("Quels formats de fichier sont acceptés pour les ressources ?",
         "Nous acceptons les formats PDF, PPTX, DOCX, ZIP, py, ipynb, dta, sav, les images (JPG, PNG), ..."),
        ("Comment puis-je devenir admin ?",
         "Le rôle d’admin est attribué par l’équipe ENSEA Data Science Club. Contactez un admin via le forum ou Slack."),
        ("Comment fonctionne le système de points XP ?",
         "Vous gagnez **+50 XP** pour chaque ressource validée, **+10 XP**pour chaque ressource proposée, **+5 XP** pour chaque fil créé et **+2 XP** pour chaque réponse validée."),
        ("Où trouver les ressources validées ?",
         "Dans **Ressources → Liste des ressources**, seulemet les ressource “Validées” y apparaissent."),
        ("Puis-je éditer ou supprimer une ressource que j’ai proposée ?",
         "Non."),
        ("Comment signaler un contenu inapproprié ?",
         "On vous assure qu'il y en aura pas cependant au cas où ça fini par arrivé contactez un admin."),
        ("Comment accéder à l’API du forum ?",
         "Notre API n’est pas encore publique, mais vous pouvez proposer une intégration via la roadmap GitHub."),
        ("Comment modifier mon mot de passe ?",
         "Dans **Paramètres → Sécurité**, entrez votre mot actuel puis le nouveau mot de passe deux fois."),
        ("Pourquoi ne vois-je pas certaines ressources ?",
         "Les ressources non validées sont masquées. Si vous êtes admin, allez dans **Admin → Valider ressources**."),
        ("Comment trier les ressources par catégories ?",
         "Dans la page **Liste des ressources**, utilisez le menu déroulant “Catégorie” pour filtrer."),
        ("Comment rechercher un thread précis ?",
         "Dans **Forum**, utilisez la barre de recherche en haut pour filtrer par titre."),
        ("Comment citer un autre membre dans un post ?",
         "Tapez **@** suivi du pseudo, p.ex. `@alice`. Vous pouvez également mentionner **@all** pour notifier tout le monde."),
        ("Puis-je télécharger plusieurs fichiers à la fois ?",
         "Non, chaque ressource est un seul fichier. Vous pouvez ZIPper plusieurs fichiers avant l’upload."),
        ("Comment voir l’historique de mes sessions ?",
         "Dans **Dashboard**, vous verrez un recap de vos activités."),
        ("Comment supprimer mon compte ?",
         "Envoyez une demande  à l’adresse edsc@ensea.ed.ci."),
        ("Comment proposer une amélioration de la plateforme ?",
         "Ouvrez une issue sur notre dépôt GitHub : https://github.com/enigmatiqueCodeur/data_science_club_platform/issues"),
        ("Où trouver la documentation utilisateur ?",
         "Dans le pied de page, cliquez sur **À propos**, puis sur le lien vers la doc."),
        ("Je rencontre un bug, comment le signaler ?",
         "Décrivez-le sur le forum dans la catégorie “Bugs & Support” ."),
    ]

    added = 0
    for q, a in faqs:
        if not Faq.query.filter_by(question=q).first():
            db.session.add(Faq(question=q, answer=a))
            added += 1

    db.session.commit()
    print(f"FAQ seed done. {added} entrées ajoutées / {len(faqs)-added} existantes.") 

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def envoyer_email(destinataire, sujet, corps):
    expediteur = "harrisonndiba338@gmail.com"
    mot_de_passe = "hjpqjhtromjyaeqa"

    msg = MIMEMultipart()
    msg["From"] = expediteur
    msg["To"] = destinataire
    msg["Subject"] = sujet

    msg.attach(MIMEText(corps, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as serveur:
            serveur.login(expediteur, mot_de_passe)
            serveur.send_message(msg)
            print("Email envoyé avec succès !")
    except Exception as e:
        print("Erreur lors de l'envoi :", e)

envoyer_email(
    destinataire="yvenlycee@gmail.com",
    sujet="Test d'envoi depuis Python",
    corps="Bonjour, ceci est un test automatique envoyé avec Python."
)
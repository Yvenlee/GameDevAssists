#Mail/send_mail.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

def envoyer_email(destinataire, sujet, corps, fichier_joint=None):
    expediteur = "yvenlycee@gmail.com"
    mot_de_passe = "chwzkaptbkoltcco"

    msg = MIMEMultipart()
    msg["From"] = expediteur
    msg["To"] = destinataire
    msg["Subject"] = sujet

    msg.attach(MIMEText(corps, "plain"))

    if fichier_joint:
        try:
            contenu = fichier_joint.read()
            part = MIMEApplication(contenu)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={fichier_joint.name}"
            )
            msg.attach(part)
        except Exception as e:
            return False, f"Erreur avec le fichier joint : {e}"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as serveur:
            serveur.login(expediteur, mot_de_passe)
            serveur.send_message(msg)
        return True, "Email envoyé avec succès."
    except Exception as e:
        return False, f"Erreur lors de l'envoi de l'email : {e}"
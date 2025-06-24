# Mail/send_mail.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def envoyer_email(destinataire, sujet, corps, fichier_joint=None):
    expediteur = "yvenlycee@gmail.com"
    mot_de_passe = "chwzkaptbkoltcco"  # OK pour le moment

    msg = MIMEMultipart()
    msg["From"] = expediteur
    msg["To"] = destinataire
    msg["Subject"] = sujet

    msg.attach(MIMEText(corps, "plain"))

    if fichier_joint:
        try:
            with open(fichier_joint, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(fichier_joint)}"
                )
                msg.attach(part)
        except Exception as e:
            return False, f"Erreur lors de l'ouverture du fichier : {e}"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as serveur:
            serveur.login(expediteur, mot_de_passe)
            serveur.send_message(msg)
        return True, "Email envoyé avec succès."
    except Exception as e:
        return False, f"Erreur lors de l'envoi de l'email : {e}"

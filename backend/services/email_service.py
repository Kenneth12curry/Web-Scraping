"""
Service d'envoi d'emails
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

logger = logging.getLogger(__name__)


class EmailService:
    """Service de gestion de l'envoi d'emails"""

    def __init__(self):
        self.config = Config.SMTP_CONFIG

    def send_password_reset_email(self, email, username, reset_url):
        """Envoyer un email de réinitialisation de mot de passe"""
        try:
            # Vérifier la configuration SMTP
            if not self.config["username"] or not self.config["password"]:
                logger.warning("Configuration SMTP incomplète - email non envoyé")
                return False, "Configuration SMTP incomplète"

            # Créer le message
            msg = MIMEMultipart()
            msg["From"] = self.config["username"]
            msg["To"] = email
            msg["Subject"] = "Réinitialisation de votre mot de passe - Findata IA"

            # Corps du message HTML
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                        <h1 style="margin: 0; font-size: 24px;">🔐 Réinitialisation de mot de passe</h1>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; margin-top: 20px;">
                        <h2 style="color: #2d3748; margin-bottom: 20px;">Bonjour {username},</h2>
                        
                        <p style="margin-bottom: 20px;">
                            Vous avez demandé la réinitialisation de votre mot de passe pour votre compte Findata IA.
                        </p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_url}" 
                               style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); 
                                      color: white; 
                                      padding: 15px 30px; 
                                      text-decoration: none; 
                                      border-radius: 8px; 
                                      font-weight: bold; 
                                      display: inline-block;
                                      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                                🔑 Réinitialiser mon mot de passe
                            </a>
                        </div>
                        
                        <p style="margin-bottom: 20px; font-size: 14px; color: #666;">
                            <strong>Important :</strong> Ce lien est valable pendant 30 minutes seulement.
                            Si vous n'avez pas demandé cette réinitialisation, vous pouvez ignorer cet email.
                        </p>
                        
                        <div style="background: #e2e8f0; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <p style="margin: 0; font-size: 12px; color: #4a5568;">
                                <strong>Lien de réinitialisation :</strong><br>
                                <a href="{reset_url}" style="color: #3b82f6; word-break: break-all;">{reset_url}</a>
                            </p>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding: 20px; border-top: 1px solid #e2e8f0;">
                        <p style="margin: 0; font-size: 12px; color: #666;">
                            Cet email a été envoyé automatiquement par Findata IA.<br>
                            Si vous avez des questions, contactez notre support.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Corps du message texte
            text_body = f"""
            Réinitialisation de votre mot de passe - Findata IA
            
            Bonjour {username},
            
            Vous avez demandé la réinitialisation de votre mot de passe pour votre compte Findata IA.
            
            Pour réinitialiser votre mot de passe, cliquez sur le lien suivant :
            {reset_url}
            
            Important : Ce lien est valable pendant 30 minutes seulement.
            Si vous n'avez pas demandé cette réinitialisation, vous pouvez ignorer cet email.
            
            Cet email a été envoyé automatiquement par Findata IA.
            Si vous avez des questions, contactez notre support.
            """

            # Attacher les parties du message
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            # Connexion au serveur SMTP
            if self.config["use_ssl"]:
                server = smtplib.SMTP_SSL(self.config["host"], self.config["port"])
            else:
                server = smtplib.SMTP(self.config["host"], self.config["port"])
                if self.config["use_tls"]:
                    server.starttls()

            # Authentification
            server.login(self.config["username"], self.config["password"])

            # Envoi de l'email
            server.send_message(msg)
            server.quit()

            logger.info(f"Email de réinitialisation envoyé avec succès à {email}")
            return True, "Email envoyé avec succès"

        except smtplib.SMTPAuthenticationError:
            logger.error("Erreur d'authentification SMTP")
            return False, "Erreur d'authentification SMTP"
        except smtplib.SMTPException as e:
            logger.error(f"Erreur SMTP: {e}")
            return False, f"Erreur SMTP: {str(e)}"
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email: {e}")
            return False, f"Erreur lors de l'envoi de l'email: {str(e)}"

    def send_welcome_email(self, email, username):
        """Envoyer un email de bienvenue"""
        try:
            # Vérifier la configuration SMTP
            if not self.config["username"] or not self.config["password"]:
                logger.warning(
                    "Configuration SMTP incomplète - email de bienvenue non envoyé"
                )
                return False, "Configuration SMTP incomplète"

            # Créer le message
            msg = MIMEMultipart()
            msg["From"] = self.config["username"]
            msg["To"] = email
            msg["Subject"] = "Bienvenue sur Findata IA ! 🚀"

            # Corps du message HTML
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 10px; text-align: center;">
                        <h1 style="margin: 0; font-size: 24px;">🎉 Bienvenue sur Findata IA !</h1>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; margin-top: 20px;">
                        <h2 style="color: #2d3748; margin-bottom: 20px;">Bonjour {username},</h2>
                        
                        <p style="margin-bottom: 20px;">
                            Félicitations ! Votre compte Findata IA a été créé avec succès.
                            Vous pouvez maintenant commencer à extraire et analyser des données web.
                        </p>
                        
                        <div style="background: #e6fffa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="color: #2d3748; margin-top: 0;">🚀 Ce que vous pouvez faire :</h3>
                            <ul style="color: #4a5568;">
                                <li>Extraire des articles de n'importe quel site web</li>
                                <li>Générer des résumés automatiques avec l'IA</li>
                                <li>Analyser les tendances et statistiques</li>
                                <li>Gérer vos abonnements et limites</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://localhost:3000" 
                               style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); 
                                      color: white; 
                                      padding: 15px 30px; 
                                      text-decoration: none; 
                                      border-radius: 8px; 
                                      font-weight: bold; 
                                      display: inline-block;
                                      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                                🎯 Commencer maintenant
                            </a>
                        </div>
                        
                        <p style="margin-bottom: 20px; font-size: 14px; color: #666;">
                            <strong>Plan actuel :</strong> Gratuit (30 requêtes/mois)<br>
                            Vous pouvez mettre à niveau votre abonnement à tout moment pour plus de fonctionnalités.
                        </p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding: 20px; border-top: 1px solid #e2e8f0;">
                        <p style="margin: 0; font-size: 12px; color: #666;">
                            Merci de nous faire confiance pour vos besoins d'extraction de données.<br>
                            L'équipe Findata IA
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Corps du message texte
            text_body = f"""
            Bienvenue sur Findata IA !
            
            Bonjour {username},
            
            Félicitations ! Votre compte Findata IA a été créé avec succès.
            Vous pouvez maintenant commencer à extraire et analyser des données web.
            
            Ce que vous pouvez faire :
            - Extraire des articles de n'importe quel site web
            - Générer des résumés automatiques avec l'IA
            - Analyser les tendances et statistiques
            - Gérer vos abonnements et limites
            
            Plan actuel : Gratuit (30 requêtes/mois)
            Vous pouvez mettre à niveau votre abonnement à tout moment.
            
            Merci de nous faire confiance pour vos besoins d'extraction de données.
            L'équipe Findata IA
            """

            # Attacher les parties du message
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            # Connexion au serveur SMTP
            if self.config["use_ssl"]:
                server = smtplib.SMTP_SSL(self.config["host"], self.config["port"])
            else:
                server = smtplib.SMTP(self.config["host"], self.config["port"])
                if self.config["use_tls"]:
                    server.starttls()

            # Authentification
            server.login(self.config["username"], self.config["password"])

            # Envoi de l'email
            server.send_message(msg)
            server.quit()

            logger.info(f"Email de bienvenue envoyé avec succès à {email}")
            return True, "Email de bienvenue envoyé avec succès"

        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email de bienvenue: {e}")
            return False, f"Erreur lors de l'envoi de l'email: {str(e)}"

    def test_smtp_connection(self):
        """Tester la connexion SMTP"""
        try:
            if not self.config["username"] or not self.config["password"]:
                return False, "Configuration SMTP incomplète"

            if self.config["use_ssl"]:
                server = smtplib.SMTP_SSL(self.config["host"], self.config["port"])
            else:
                server = smtplib.SMTP(self.config["host"], self.config["port"])
                if self.config["use_tls"]:
                    server.starttls()

            server.login(self.config["username"], self.config["password"])
            server.quit()

            return True, "Connexion SMTP réussie"

        except Exception as e:
            logger.error(f"Erreur de test SMTP: {e}")
            return False, f"Erreur de connexion SMTP: {str(e)}"


# Instance globale
email_service = EmailService()

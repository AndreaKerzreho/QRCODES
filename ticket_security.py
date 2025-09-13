import hashlib
import hmac
import secrets
import json
import base64
import datetime
from pathlib import Path

class TicketSecurity:
    """Système de sécurité pour l'authentification des billets QR"""
    
    def __init__(self, secret_key_file="ticket_secret.key"):
        self.secret_key_file = secret_key_file
        self.secret_key = self._load_or_create_secret_key()
    
    def _load_or_create_secret_key(self):
        """Charger ou créer une clé secrète pour la signature"""
        secret_file = Path(self.secret_key_file)
        
        if secret_file.exists():
            try:
                with open(secret_file, 'r') as f:
                    return f.read().strip()
            except Exception:
                pass
        
        # Créer une nouvelle clé secrète
        secret_key = secrets.token_urlsafe(32)
        try:
            with open(secret_file, 'w') as f:
                f.write(secret_key)
            print(f"✓ Nouvelle clé de sécurité créée: {secret_file}")
        except Exception as e:
            print(f"⚠️ Impossible de sauvegarder la clé: {e}")
        
        return secret_key
    
    def create_ticket_data(self, event_name, ticket_id, buyer_info=None, 
                          event_date=None, additional_data=None):
        """Créer les données d'un billet avec signature"""
        
        # Données du billet
        ticket_data = {
            "event_name": event_name,
            "ticket_id": ticket_id,
            "generated_at": datetime.datetime.now().isoformat(),
            "event_date": event_date,
            "buyer_info": buyer_info or {},
            "additional_data": additional_data or {}
        }
        
        # Créer la signature
        data_string = json.dumps(ticket_data, sort_keys=True, separators=(',', ':'))
        signature = self._create_signature(data_string)
        
        # Ajouter la signature aux données
        signed_ticket = {
            "data": ticket_data,
            "signature": signature,
            "version": "1.0"
        }
        
        return signed_ticket
    
    def _create_signature(self, data_string):
        """Créer une signature HMAC pour les données"""
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            data_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def validate_ticket(self, ticket_qr_data):
        """Valider un billet en vérifiant sa signature"""
        try:
            # Décoder les données du QR code
            if isinstance(ticket_qr_data, str):
                try:
                    ticket_json = json.loads(ticket_qr_data)
                except json.JSONDecodeError:
                    return {
                        "valid": False,
                        "error": "Format de données invalide",
                        "details": "Le QR code ne contient pas de JSON valide"
                    }
            else:
                ticket_json = ticket_qr_data
            
            # Vérifier la structure
            required_fields = ["data", "signature", "version"]
            if not all(field in ticket_json for field in required_fields):
                return {
                    "valid": False,
                    "error": "Structure de billet invalide",
                    "details": f"Champs requis manquants: {required_fields}"
                }
            
            # Extraire les données et signature
            ticket_data = ticket_json["data"]
            provided_signature = ticket_json["signature"]
            
            # Recalculer la signature
            data_string = json.dumps(ticket_data, sort_keys=True, separators=(',', ':'))
            expected_signature = self._create_signature(data_string)
            
            # Comparer les signatures de manière sécurisée
            is_valid = hmac.compare_digest(provided_signature, expected_signature)
            
            if is_valid:
                return {
                    "valid": True,
                    "ticket_data": ticket_data,
                    "validated_at": datetime.datetime.now().isoformat(),
                    "event_name": ticket_data.get("event_name"),
                    "ticket_id": ticket_data.get("ticket_id"),
                    "generated_at": ticket_data.get("generated_at"),
                    "event_date": ticket_data.get("event_date"),
                    "buyer_info": ticket_data.get("buyer_info", {})
                }
            else:
                return {
                    "valid": False,
                    "error": "Signature invalide",
                    "details": "Ce billet n'a pas été généré par votre système"
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": "Erreur de validation",
                "details": str(e)
            }
    
    def encode_ticket_for_qr(self, signed_ticket):
        """Encoder les données du billet pour un QR code (base64 compressé)"""
        json_string = json.dumps(signed_ticket, separators=(',', ':'))
        
        # Encoder en base64 pour réduire la taille
        encoded = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
        
        # Ajouter un préfixe pour identifier nos billets
        return f"TICKET_V1:{encoded}"
    
    def decode_ticket_from_qr(self, qr_data):
        """Décoder les données d'un QR code de billet"""
        try:
            if not qr_data.startswith("TICKET_V1:"):
                return None
            
            # Retirer le préfixe
            encoded_data = qr_data[10:]  # len("TICKET_V1:") = 10
            
            # Décoder base64
            json_string = base64.b64decode(encoded_data.encode('utf-8')).decode('utf-8')
            
            # Parser JSON
            ticket_data = json.loads(json_string)
            
            return ticket_data
            
        except Exception:
            return None
    
    def get_security_info(self):
        """Obtenir des informations sur la sécurité"""
        return {
            "secret_key_file": self.secret_key_file,
            "secret_key_exists": Path(self.secret_key_file).exists(),
            "signature_algorithm": "HMAC-SHA256",
            "encoding": "Base64",
            "version": "1.0"
        }


class TicketValidator:
    """Validateur de billets avec historique"""
    
    def __init__(self, security_system=None):
        self.security = security_system or TicketSecurity()
        self.validation_log = "ticket_validations.json"
        self.validated_tickets = self._load_validation_history()
    
    def _load_validation_history(self):
        """Charger l'historique des validations"""
        try:
            if Path(self.validation_log).exists():
                with open(self.validation_log, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_validation_history(self):
        """Sauvegarder l'historique des validations"""
        try:
            with open(self.validation_log, 'w', encoding='utf-8') as f:
                json.dump(self.validated_tickets, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde historique: {e}")
    
    def validate_and_log(self, qr_data, scanner_info=None):
        """Valider un billet et enregistrer la validation"""
        
        # S'assurer que validated_tickets est un dictionnaire
        if not isinstance(self.validated_tickets, dict):
            print(f"⚠️ validated_tickets corrigé de {type(self.validated_tickets)} vers dict")
            self.validated_tickets = {}
        
        # Décoder le QR code
        ticket_data = self.security.decode_ticket_from_qr(qr_data)
        if not ticket_data:
            return {
                "valid": False,
                "error": "QR code non reconnu",
                "details": "Ce n'est pas un billet valide de votre système"
            }
        
        # Valider la signature
        validation_result = self.security.validate_ticket(ticket_data)
        
        if validation_result["valid"]:
            ticket_id = validation_result["ticket_data"]["ticket_id"]
            
            # Vérifier si le billet a déjà été utilisé
            if ticket_id in self.validated_tickets:
                previous_use = self.validated_tickets[ticket_id]
                return {
                    "valid": False,
                    "error": "Billet déjà utilisé",
                    "details": f"Ce billet a été scanné le {previous_use['validated_at']}",
                    "previous_validation": previous_use,
                    "ticket_data": validation_result["ticket_data"]
                }
            
            # Enregistrer la validation
            validation_entry = {
                "ticket_id": ticket_id,
                "validated_at": datetime.datetime.now().isoformat(),
                "scanner_info": scanner_info or {},
                "ticket_data": validation_result["ticket_data"]
            }
            
            self.validated_tickets[ticket_id] = validation_entry
            self._save_validation_history()
            
            validation_result["first_use"] = True
            validation_result["validation_logged"] = True
        
        return validation_result
    
    def get_validation_stats(self):
        """Obtenir les statistiques de validation"""
        # S'assurer que validated_tickets est un dictionnaire (c'est sa structure normale)
        if not isinstance(self.validated_tickets, dict):
            print(f"⚠️ validated_tickets n'est pas un dictionnaire: {type(self.validated_tickets)}")
            self.validated_tickets = {}
            
        # Obtenir la liste des validations depuis le dictionnaire
        validation_list = list(self.validated_tickets.values())
        total_validated = len(validation_list)
        
        # Statistiques par événement
        events = {}
        for validation in validation_list:
            try:
                if isinstance(validation, dict) and "ticket_data" in validation:
                    event_name = validation["ticket_data"].get("event_name", "Inconnu")
                    events[event_name] = events.get(event_name, 0) + 1
            except (TypeError, KeyError, AttributeError) as e:
                print(f"⚠️ Erreur lors du traitement d'une validation: {e}")
                continue
        
        # Validations récentes - trier par date avec gestion d'erreur
        recent_validations = []
        try:
            recent_validations = sorted(
                [v for v in validation_list if isinstance(v, dict)],
                key=lambda x: x.get("validated_at", ""),
                reverse=True
            )[:10]
        except Exception as e:
            print(f"⚠️ Erreur lors du tri des validations récentes: {e}")
            recent_validations = validation_list[:10]  # Prendre les 10 premiers sans tri
        
        return {
            "total_validated": total_validated,
            "events": events,
            "recent_validations": recent_validations,
            "valid_scans": total_validated,
            "invalid_scans": 0  # Pour l'instant, on ne trace que les validations réussies
        }
    
    def reset_validations(self):
        """Réinitialiser l'historique des validations"""
        self.validated_tickets = {}
        self._save_validation_history()
        return True


# Test du système
if __name__ == "__main__":
    print("=== Test du Système de Sécurité des Billets ===")
    print()
    
    # Initialiser le système
    security = TicketSecurity()
    validator = TicketValidator(security)
    
    print("1. Création d'un billet test...")
    
    # Créer un billet
    ticket_data = security.create_ticket_data(
        event_name="Soirée Dansante 2025",
        ticket_id="TICKET_001",
        buyer_info={
            "nom": "Dupont",
            "prenom": "Jean",
            "email": "jean.dupont@email.com"
        },
        event_date="2025-12-31T20:00:00",
        additional_data={
            "type_billet": "Standard",
            "prix": "25€"
        }
    )
    
    # Encoder pour QR code
    qr_content = security.encode_ticket_for_qr(ticket_data)
    print(f"✓ Billet créé - Taille QR: {len(qr_content)} caractères")
    print(f"✓ ID Billet: {ticket_data['data']['ticket_id']}")
    print()
    
    print("2. Test de validation...")
    
    # Valider le billet
    validation = validator.validate_and_log(qr_content, 
                                           scanner_info={"scanner": "Test Scanner"})
    
    if validation["valid"]:
        print("✓ Billet valide et enregistré!")
        print(f"  Événement: {validation['event_name']}")
        print(f"  Acheteur: {validation['buyer_info']['prenom']} {validation['buyer_info']['nom']}")
    else:
        print(f"✗ Validation échouée: {validation['error']}")
    print()
    
    print("3. Test de double utilisation...")
    
    # Essayer de valider à nouveau
    second_validation = validator.validate_and_log(qr_content)
    
    if not second_validation["valid"]:
        print("✓ Double utilisation détectée correctement!")
        print(f"  Erreur: {second_validation['error']}")
    else:
        print("✗ La double utilisation n'a pas été détectée!")
    print()
    
    print("4. Test avec QR code invalide...")
    
    # Tester avec données invalides
    fake_qr = "TICKET_V1:ZmFrZV9kYXRh"  # "fake_data" en base64
    fake_validation = validator.validate_and_log(fake_qr)
    
    if not fake_validation["valid"]:
        print("✓ QR code invalide détecté correctement!")
        print(f"  Erreur: {fake_validation['error']}")
    else:
        print("✗ QR code invalide accepté!")
    print()
    
    print("5. Statistiques...")
    stats = validator.get_validation_stats()
    print(f"✓ Total billets validés: {stats['total_validated']}")
    print(f"✓ Événements: {list(stats['events'].keys())}")
    
    security_info = security.get_security_info()
    print(f"✓ Système de sécurité: {security_info['signature_algorithm']}")
    print()
    
    print("✅ Tests terminés - Système de sécurité opérationnel!")
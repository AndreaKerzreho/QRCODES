import qrcode
import json
import os
import datetime
from qr_generator import QRCodeGenerator
from ticket_security import TicketSecurity, TicketValidator

class TicketGenerator(QRCodeGenerator):
    """Générateur de billets QR sécurisés pour événements"""
    
    def __init__(self):
        super().__init__()
        self.security = TicketSecurity()
        self.validator = TicketValidator(self.security)
        self.output_dir = "generated_tickets"
        self.ticket_db = "tickets_database.json"
        self.tickets = self.load_ticket_database()
        
        # Assurer que le dossier de sortie existe
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_ticket_database(self):
        """Charger la base de données des billets"""
        try:
            if os.path.exists(self.ticket_db):
                with open(self.ticket_db, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de la BD: {e}")
        return {}
    
    def save_ticket_database(self):
        """Sauvegarder la base de données des billets"""
        try:
            with open(self.ticket_db, 'w', encoding='utf-8') as f:
                json.dump(self.tickets, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la BD: {e}")
    
    def generate_ticket(self, event_name, buyer_name, buyer_email="", 
                       event_date=None, ticket_type="Standard", price="", 
                       additional_info=None):
        """Générer un billet QR sécurisé"""
        
        # Générer un ID unique pour le billet
        ticket_id = self.generate_unique_id("uuid")
        
        # Préparer les informations de l'acheteur
        buyer_info = {
            "nom": buyer_name,
            "email": buyer_email,
            "achat_le": datetime.datetime.now().isoformat()
        }
        
        # Informations additionnelles
        additional_data = {
            "type_billet": ticket_type,
            "prix": price,
            **(additional_info or {})
        }
        
        # Créer les données sécurisées du billet
        signed_ticket = self.security.create_ticket_data(
            event_name=event_name,
            ticket_id=ticket_id,
            buyer_info=buyer_info,
            event_date=event_date,
            additional_data=additional_data
        )
        
        # Encoder pour QR code
        qr_content = self.security.encode_ticket_for_qr(signed_ticket)
        
        # Créer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        # Créer l'image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Nom du fichier
        safe_event_name = "".join(c for c in event_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_buyer_name = "".join(c for c in buyer_name if c.isalnum() or c in (' ', '-', '_')).strip()
        
        filename = f"ticket_{safe_event_name}_{safe_buyer_name}_{ticket_id[:8]}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Sauvegarder l'image
        img.save(filepath)
        
        # Enregistrer dans la base de données
        ticket_record = {
            "ticket_id": ticket_id,
            "event_name": event_name,
            "buyer_info": buyer_info,
            "event_date": event_date,
            "ticket_type": ticket_type,
            "price": price,
            "additional_data": additional_data,
            "qr_content": qr_content,
            "filename": filename,
            "filepath": filepath,
            "generated_at": datetime.datetime.now().isoformat(),
            "status": "active"
        }
        
        self.tickets[ticket_id] = ticket_record
        self.save_ticket_database()
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "filename": filename,
            "filepath": filepath,
            "qr_content": qr_content,
            "signed_ticket": signed_ticket,
            "image": img
        }
    
    def generate_batch_tickets(self, event_name, buyers_list, event_date=None, 
                              ticket_type="Standard", price=""):
        """Générer plusieurs billets en lot"""
        results = []
        
        for i, buyer in enumerate(buyers_list):
            try:
                if isinstance(buyer, str):
                    # Si c'est juste un nom
                    buyer_name = buyer
                    buyer_email = ""
                elif isinstance(buyer, dict):
                    # Si c'est un dictionnaire avec nom et email
                    buyer_name = buyer.get("nom", f"Acheteur_{i+1}")
                    buyer_email = buyer.get("email", "")
                else:
                    results.append({
                        "success": False,
                        "error": f"Format d'acheteur invalide: {buyer}",
                        "index": i + 1
                    })
                    continue
                
                # Générer le billet
                ticket_result = self.generate_ticket(
                    event_name=event_name,
                    buyer_name=buyer_name,
                    buyer_email=buyer_email,
                    event_date=event_date,
                    ticket_type=ticket_type,
                    price=price
                )
                
                if ticket_result["success"]:
                    results.append({
                        "success": True,
                        "index": i + 1,
                        "buyer_name": buyer_name,
                        "ticket_id": ticket_result["ticket_id"],
                        "filename": ticket_result["filename"],
                        "filepath": ticket_result["filepath"]
                    })
                else:
                    results.append({
                        "success": False,
                        "error": "Erreur de génération",
                        "index": i + 1
                    })
                    
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "index": i + 1
                })
        
        return results
    
    def validate_ticket_qr(self, qr_data, scanner_info=None):
        """Valider un billet scanné"""
        return self.validator.validate_and_log(qr_data, scanner_info)
    
    def get_ticket_info(self, ticket_id):
        """Obtenir les informations d'un billet"""
        return self.tickets.get(ticket_id)
    
    def get_event_statistics(self, event_name=None):
        """Obtenir les statistiques des billets"""
        total_tickets = len(self.tickets)
        
        # Filtrer par événement si spécifié
        tickets_to_analyze = self.tickets.values()
        if event_name:
            tickets_to_analyze = [t for t in tickets_to_analyze 
                                if t.get("event_name") == event_name]
        
        # Statistiques par événement
        events = {}
        ticket_types = {}
        
        for ticket in tickets_to_analyze:
            event = ticket.get("event_name", "Inconnu")
            ticket_type = ticket.get("ticket_type", "Standard")
            
            events[event] = events.get(event, 0) + 1
            ticket_types[ticket_type] = ticket_types.get(ticket_type, 0) + 1
        
        # Statistiques de validation
        validation_stats = self.validator.get_validation_stats()
        
        return {
            "total_tickets_generated": len(tickets_to_analyze),
            "total_tickets_validated": validation_stats["total_validated"],
            "events": events,
            "ticket_types": ticket_types,
            "validation_rate": (
                validation_stats["total_validated"] / len(tickets_to_analyze) * 100
                if tickets_to_analyze else 0
            ),
            "recent_tickets": sorted(
                tickets_to_analyze,
                key=lambda x: x.get("generated_at", ""),
                reverse=True
            )[:5]
        }
    
    def export_tickets_list(self, event_name=None, format="json"):
        """Exporter la liste des billets"""
        tickets_to_export = []
        
        for ticket_id, ticket_data in self.tickets.items():
            if event_name and ticket_data.get("event_name") != event_name:
                continue
            
            # Données à exporter (sans le QR content pour économiser l'espace)
            export_data = {
                "ticket_id": ticket_id,
                "event_name": ticket_data.get("event_name"),
                "buyer_name": ticket_data.get("buyer_info", {}).get("nom"),
                "buyer_email": ticket_data.get("buyer_info", {}).get("email"),
                "ticket_type": ticket_data.get("ticket_type"),
                "price": ticket_data.get("price"),
                "generated_at": ticket_data.get("generated_at"),
                "status": ticket_data.get("status"),
                "filename": ticket_data.get("filename")
            }
            tickets_to_export.append(export_data)
        
        if format == "json":
            return json.dumps(tickets_to_export, indent=2, ensure_ascii=False)
        elif format == "csv":
            if not tickets_to_export:
                return ""
            
            # Créer le CSV
            import csv
            import io
            
            output = io.StringIO()
            fieldnames = tickets_to_export[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(tickets_to_export)
            
            return output.getvalue()
        
        return tickets_to_export


# Test du générateur de billets
if __name__ == "__main__":
    print("=== Test du Générateur de Billets QR Sécurisés ===")
    print()
    
    # Initialiser le générateur
    ticket_gen = TicketGenerator()
    
    print("1. Génération d'un billet test...")
    
    # Générer un billet
    result = ticket_gen.generate_ticket(
        event_name="Soirée Dansante 2025",
        buyer_name="Jean Dupont",
        buyer_email="jean.dupont@email.com",
        event_date="2025-12-31T20:00:00",
        ticket_type="VIP",
        price="35€"
    )
    
    if result["success"]:
        print(f"✓ Billet généré: {result['filename']}")
        print(f"✓ ID Billet: {result['ticket_id']}")
        print()
        
        print("2. Test de validation...")
        
        # Valider le billet
        validation = ticket_gen.validate_ticket_qr(
            result["qr_content"],
            scanner_info={"scanner": "Test Scanner", "location": "Entrée principale"}
        )
        
        if validation["valid"]:
            print("✓ Billet valide!")
            print(f"  Événement: {validation['event_name']}")
            print(f"  Acheteur: {validation['ticket_data']['buyer_info']['nom']}")
        else:
            print(f"✗ Validation échouée: {validation['error']}")
        print()
        
        print("3. Test de double scan...")
        
        # Essayer de scanner à nouveau
        second_scan = ticket_gen.validate_ticket_qr(result["qr_content"])
        
        if not second_scan["valid"]:
            print("✓ Double utilisation bloquée!")
            print(f"  Erreur: {second_scan['error']}")
        else:
            print("✗ Double utilisation non détectée!")
        print()
    
    print("4. Génération en lot...")
    
    # Générer plusieurs billets
    buyers = [
        {"nom": "Marie Martin", "email": "marie@email.com"},
        {"nom": "Paul Durand", "email": "paul@email.com"},
        "Sophie Lefebvre"  # Juste le nom
    ]
    
    batch_results = ticket_gen.generate_batch_tickets(
        event_name="Soirée Dansante 2025",
        buyers_list=buyers,
        event_date="2025-12-31T20:00:00",
        ticket_type="Standard",
        price="25€"
    )
    
    success_count = sum(1 for r in batch_results if r["success"])
    print(f"✓ {success_count}/{len(buyers)} billets générés en lot")
    
    for result in batch_results:
        if result["success"]:
            print(f"  - {result['buyer_name']}: {result['filename']}")
        else:
            print(f"  - Erreur #{result['index']}: {result['error']}")
    print()
    
    print("5. Statistiques...")
    stats = ticket_gen.get_event_statistics()
    print(f"✓ Total billets générés: {stats['total_tickets_generated']}")
    print(f"✓ Total billets validés: {stats['total_tickets_validated']}")
    print(f"✓ Taux de validation: {stats['validation_rate']:.1f}%")
    print(f"✓ Événements: {list(stats['events'].keys())}")
    print()
    
    print("✅ Test terminé - Système de billetterie opérationnel!")
import qrcode
import uuid
import hashlib
import datetime
import os
from PIL import Image, ImageDraw, ImageFont
import json
import random
import string

class QRCodeGenerator:
    def __init__(self):
        self.output_dir = "generated_qr"
        self.history_file = "qr_history.json"
        self.generated_codes = self.load_history()
        
        # Assurer que le dossier de sortie existe
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_history(self):
        """Charger l'historique des QR codes générés"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de l'historique: {e}")
        return {}
    
    def save_history(self):
        """Sauvegarder l'historique des QR codes générés"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.generated_codes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'historique: {e}")
    
    def generate_unique_id(self, method="uuid"):
        """Générer un identifiant unique selon différentes méthodes"""
        if method == "uuid":
            return str(uuid.uuid4())
        elif method == "timestamp":
            return str(int(datetime.datetime.now().timestamp() * 1000000))
        elif method == "hash":
            data = f"{datetime.datetime.now()}{random.random()}"
            return hashlib.sha256(data.encode()).hexdigest()[:16]
        elif method == "random":
            return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        else:
            return str(uuid.uuid4())
    
    def create_qr_code(self, data, unique_id=None, size=10, border=4, error_correction='M'):
        """Créer un QR code avec les paramètres spécifiés"""
        # Configuration de la correction d'erreur
        error_corrections = {
            'L': qrcode.constants.ERROR_CORRECT_L,  # ~7%
            'M': qrcode.constants.ERROR_CORRECT_M,  # ~15%
            'Q': qrcode.constants.ERROR_CORRECT_Q,  # ~25%
            'H': qrcode.constants.ERROR_CORRECT_H   # ~30%
        }
        
        # Créer l'instance QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_corrections.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
            box_size=size,
            border=border,
        )
        
        # Ajouter les données
        qr.add_data(data)
        qr.make(fit=True)
        
        # Créer l'image
        img = qr.make_image(fill_color="black", back_color="white")
        
        return img, qr
    
    def generate_unique_qr(self, base_data="", id_method="uuid", include_timestamp=True, 
                          custom_prefix="", size=10, border=4, error_correction='M'):
        """Générer un QR code unique avec diverses options"""
        
        # Générer un identifiant unique
        unique_id = self.generate_unique_id(id_method)
        
        # Construire les données du QR code
        qr_data = ""
        if custom_prefix:
            qr_data += f"{custom_prefix}:"
        
        qr_data += unique_id
        
        if base_data:
            qr_data += f"|{base_data}"
        
        if include_timestamp:
            timestamp = datetime.datetime.now().isoformat()
            qr_data += f"|{timestamp}"
        
        # Vérifier l'unicité
        data_hash = hashlib.md5(qr_data.encode()).hexdigest()
        if data_hash in self.generated_codes:
            print("Attention: Ce QR code a déjà été généré!")
            return None, None, None
        
        # Créer le QR code
        img, qr_obj = self.create_qr_code(qr_data, unique_id, size, border, error_correction)
        
        # Générer le nom du fichier
        filename = f"qr_{unique_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Sauvegarder l'image
        img.save(filepath)
        
        # Enregistrer dans l'historique
        self.generated_codes[data_hash] = {
            "unique_id": unique_id,
            "data": qr_data,
            "filename": filename,
            "filepath": filepath,
            "created_at": datetime.datetime.now().isoformat(),
            "method": id_method,
            "size": size,
            "border": border,
            "error_correction": error_correction
        }
        
        self.save_history()
        
        return img, qr_data, filepath
    
    def generate_batch_qr(self, count=10, base_data="", id_method="uuid", **kwargs):
        """Générer plusieurs QR codes uniques en lot"""
        results = []
        
        for i in range(count):
            try:
                img, data, filepath = self.generate_unique_qr(
                    base_data=f"{base_data}_batch_{i+1}" if base_data else f"batch_{i+1}",
                    id_method=id_method,
                    **kwargs
                )
                
                if img and data and filepath:
                    results.append({
                        "index": i+1,
                        "data": data,
                        "filepath": filepath,
                        "status": "success"
                    })
                else:
                    results.append({
                        "index": i+1,
                        "status": "failed",
                        "error": "Génération échouée"
                    })
                    
            except Exception as e:
                results.append({
                    "index": i+1,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def get_statistics(self):
        """Obtenir des statistiques sur les QR codes générés"""
        total_count = len(self.generated_codes)
        
        if total_count == 0:
            return {"total": 0, "methods": {}, "recent": []}
        
        # Compter par méthode
        methods = {}
        recent_codes = []
        
        for code_hash, code_info in self.generated_codes.items():
            method = code_info.get("method", "unknown")
            methods[method] = methods.get(method, 0) + 1
            
            # Garder les 5 plus récents
            recent_codes.append({
                "id": code_info["unique_id"],
                "created_at": code_info["created_at"],
                "filename": code_info["filename"]
            })
        
        # Trier par date de création (plus récent en premier)
        recent_codes.sort(key=lambda x: x["created_at"], reverse=True)
        recent_codes = recent_codes[:5]
        
        return {
            "total": total_count,
            "methods": methods,
            "recent": recent_codes
        }
    
    def verify_uniqueness(self):
        """Vérifier l'unicité de tous les QR codes générés"""
        unique_ids = set()
        duplicates = []
        
        for code_hash, code_info in self.generated_codes.items():
            unique_id = code_info["unique_id"]
            if unique_id in unique_ids:
                duplicates.append(unique_id)
            else:
                unique_ids.add(unique_id)
        
        return {
            "total_codes": len(self.generated_codes),
            "unique_ids": len(unique_ids),
            "duplicates": duplicates,
            "is_all_unique": len(duplicates) == 0
        }


if __name__ == "__main__":
    # Exemple d'utilisation
    generator = QRCodeGenerator()
    
    print("=== Générateur de QR Codes Uniques ===")
    print()
    
    # Générer un QR code simple
    print("1. Génération d'un QR code simple...")
    img, data, filepath = generator.generate_unique_qr(
        base_data="Test QR Code",
        id_method="uuid",
        custom_prefix="DEMO"
    )
    
    if img:
        print(f"✓ QR code généré avec succès!")
        print(f"  Données: {data}")
        print(f"  Fichier: {filepath}")
    
    print()
    
    # Générer plusieurs QR codes
    print("2. Génération en lot (3 QR codes)...")
    batch_results = generator.generate_batch_qr(
        count=3,
        base_data="Lot_Test",
        id_method="hash",
        custom_prefix="BATCH"
    )
    
    for result in batch_results:
        if result["status"] == "success":
            print(f"✓ QR {result['index']}: {result['filepath']}")
        else:
            print(f"✗ QR {result['index']}: {result.get('error', 'Erreur inconnue')}")
    
    print()
    
    # Afficher les statistiques
    print("3. Statistiques:")
    stats = generator.get_statistics()
    print(f"  Total de QR codes générés: {stats['total']}")
    print(f"  Méthodes utilisées: {stats['methods']}")
    
    print()
    
    # Vérifier l'unicité
    print("4. Vérification de l'unicité:")
    uniqueness = generator.verify_uniqueness()
    print(f"  QR codes générés: {uniqueness['total_codes']}")
    print(f"  IDs uniques: {uniqueness['unique_ids']}")
    print(f"  Tous uniques: {'✓ Oui' if uniqueness['is_all_unique'] else '✗ Non'}")
    
    if uniqueness['duplicates']:
        print(f"  Doublons détectés: {uniqueness['duplicates']}")
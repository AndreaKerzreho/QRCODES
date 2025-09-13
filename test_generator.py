"""
Script de test pour le générateur de QR codes uniques
Ce script teste toutes les fonctionnalités principales du générateur
"""

import os
import sys
import time
from qr_generator import QRCodeGenerator

def test_basic_generation():
    """Test de la génération de base"""
    print("=== Test 1: Génération de base ===")
    
    generator = QRCodeGenerator()
    
    # Test avec UUID
    img, data, filepath = generator.generate_unique_qr(
        base_data="Test basique",
        id_method="uuid",
        custom_prefix="TEST"
    )
    
    assert img is not None, "Image non générée"
    assert data is not None, "Données non générées"
    assert filepath is not None, "Chemin de fichier non généré"
    assert os.path.exists(filepath), "Fichier QR code non créé"
    
    print(f"✓ QR code généré: {os.path.basename(filepath)}")
    print(f"✓ Données: {data}")
    print()

def test_all_methods():
    """Test de toutes les méthodes de génération d'ID"""
    print("=== Test 2: Toutes les méthodes d'ID ===")
    
    generator = QRCodeGenerator()
    methods = ["uuid", "timestamp", "hash", "random"]
    
    results = []
    for method in methods:
        img, data, filepath = generator.generate_unique_qr(
            base_data=f"Test {method}",
            id_method=method,
            custom_prefix="METHOD"
        )
        
        assert img is not None, f"Échec génération avec méthode {method}"
        assert os.path.exists(filepath), f"Fichier non créé pour méthode {method}"
        
        results.append({
            "method": method,
            "data": data,
            "filepath": filepath
        })
        
        print(f"✓ Méthode {method.upper()}: {os.path.basename(filepath)}")
    
    print()
    return results

def test_batch_generation():
    """Test de la génération en lot"""
    print("=== Test 3: Génération en lot ===")
    
    generator = QRCodeGenerator()
    
    # Générer 5 QR codes en lot
    batch_results = generator.generate_batch_qr(
        count=5,
        base_data="Lot test",
        id_method="hash",
        custom_prefix="BATCH"
    )
    
    assert len(batch_results) == 5, "Nombre incorrect de QR codes générés"
    
    success_count = 0
    for result in batch_results:
        if result["status"] == "success":
            success_count += 1
            assert os.path.exists(result["filepath"]), f"Fichier manquant: {result['filepath']}"
            print(f"✓ Lot {result['index']}: {os.path.basename(result['filepath'])}")
        else:
            print(f"✗ Lot {result['index']}: {result.get('error', 'Erreur inconnue')}")
    
    print(f"✓ {success_count}/5 QR codes générés avec succès")
    print()

def test_uniqueness():
    """Test de vérification d'unicité"""
    print("=== Test 4: Vérification d'unicité ===")
    
    generator = QRCodeGenerator()
    
    # Générer plusieurs QR codes
    for i in range(3):
        generator.generate_unique_qr(
            base_data=f"Unicité test {i}",
            id_method="uuid",
            custom_prefix="UNIQUE"
        )
    
    # Vérifier l'unicité
    uniqueness = generator.verify_uniqueness()
    
    print(f"✓ Total QR codes: {uniqueness['total_codes']}")
    print(f"✓ IDs uniques: {uniqueness['unique_ids']}")
    print(f"✓ Doublons: {len(uniqueness['duplicates'])}")
    print(f"✓ Tous uniques: {'Oui' if uniqueness['is_all_unique'] else 'Non'}")
    
    assert uniqueness['is_all_unique'], "Des doublons ont été détectés!"
    print()

def test_statistics():
    """Test des statistiques"""
    print("=== Test 5: Statistiques ===")
    
    generator = QRCodeGenerator()
    stats = generator.get_statistics()
    
    print(f"✓ Total générés: {stats['total']}")
    print(f"✓ Méthodes utilisées: {list(stats['methods'].keys())}")
    print(f"✓ Répartition: {stats['methods']}")
    print(f"✓ QR codes récents: {len(stats['recent'])}")
    
    assert stats['total'] > 0, "Aucun QR code dans les statistiques"
    print()

def test_custom_parameters():
    """Test des paramètres personnalisés"""
    print("=== Test 6: Paramètres personnalisés ===")
    
    generator = QRCodeGenerator()
    
    # Test avec paramètres personnalisés
    img, data, filepath = generator.generate_unique_qr(
        base_data="Paramètres personnalisés",
        id_method="random",
        custom_prefix="CUSTOM",
        include_timestamp=False,
        size=15,
        border=2,
        error_correction='H'
    )
    
    assert img is not None, "Génération échouée avec paramètres personnalisés"
    assert os.path.exists(filepath), "Fichier non créé avec paramètres personnalisés"
    
    print(f"✓ QR code avec paramètres personnalisés: {os.path.basename(filepath)}")
    print(f"✓ Données sans timestamp: {data}")
    print()

def test_edge_cases():
    """Test des cas limites"""
    print("=== Test 7: Cas limites ===")
    
    generator = QRCodeGenerator()
    
    # Test avec données vides
    img, data, filepath = generator.generate_unique_qr(
        base_data="",
        id_method="uuid"
    )
    
    assert img is not None, "Échec avec données vides"
    print("✓ Génération avec données vides: OK")
    
    # Test avec préfixe vide
    img, data, filepath = generator.generate_unique_qr(
        base_data="Test préfixe vide",
        custom_prefix="",
        id_method="timestamp"
    )
    
    assert img is not None, "Échec avec préfixe vide"
    print("✓ Génération avec préfixe vide: OK")
    
    # Test avec tous les paramètres au minimum
    img, data, filepath = generator.generate_unique_qr(
        base_data="Paramètres min",
        size=5,
        border=1,
        error_correction='L'
    )
    
    assert img is not None, "Échec avec paramètres minimums"
    print("✓ Génération avec paramètres minimums: OK")
    print()

def run_performance_test():
    """Test de performance"""
    print("=== Test 8: Performance ===")
    
    generator = QRCodeGenerator()
    
    # Mesurer le temps de génération
    start_time = time.time()
    
    batch_results = generator.generate_batch_qr(
        count=10,
        base_data="Performance test",
        id_method="uuid"
    )
    
    end_time = time.time()
    generation_time = end_time - start_time
    
    success_count = sum(1 for r in batch_results if r["status"] == "success")
    
    print(f"✓ 10 QR codes générés en {generation_time:.2f} secondes")
    print(f"✓ Taux de succès: {success_count}/10 ({success_count*10}%)")
    print(f"✓ Temps moyen par QR code: {generation_time/10:.3f} secondes")
    
    assert success_count == 10, "Tous les QR codes n'ont pas été générés"
    print()

def cleanup_test_files():
    """Nettoyer les fichiers de test"""
    print("=== Nettoyage des fichiers de test ===")
    
    output_dir = "generated_qr"
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
        print(f"✓ Suppression de {len(files)} fichiers de test...")
        
        for file in files:
            filepath = os.path.join(output_dir, file)
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"✗ Erreur suppression {file}: {e}")
    
    # Supprimer le fichier d'historique de test
    history_file = "qr_history.json"
    if os.path.exists(history_file):
        try:
            os.remove(history_file)
            print("✓ Fichier d'historique supprimé")
        except Exception as e:
            print(f"✗ Erreur suppression historique: {e}")
    
    print()

def main():
    """Fonction principale de test"""
    print("🧪 TESTS DU GÉNÉRATEUR DE QR CODES UNIQUES")
    print("=" * 50)
    print()
    
    try:
        # Exécuter tous les tests
        test_basic_generation()
        test_all_methods()
        test_batch_generation()
        test_uniqueness()
        test_statistics()
        test_custom_parameters()
        test_edge_cases()
        run_performance_test()
        
        print("🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        print()
        
        # Demander si on veut nettoyer
        response = input("Voulez-vous supprimer les fichiers de test? (o/n): ").lower()
        if response in ['o', 'oui', 'y', 'yes']:
            cleanup_test_files()
        else:
            print("✓ Fichiers de test conservés dans le dossier 'generated_qr'")
        
    except AssertionError as e:
        print(f"❌ ÉCHEC DU TEST: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"💥 ERREUR INATTENDUE: {e}")
        sys.exit(1)
    
    print()
    print("✅ Tests terminés avec succès!")

if __name__ == "__main__":
    main()
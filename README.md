# Générateur de QR Codes Uniques

Un générateur de QR codes uniques avec interface web développé en Python et Flask. Ce projet permet de créer des QR codes garantis uniques avec plusieurs méthodes de génération d'identifiants et de nombreuses options de personnalisation.

![QR Code Generator](https://img.shields.io/badge/QR%20Code-Generator-blue) ![Python](https://img.shields.io/badge/Python-3.7+-green) ![Flask](https://img.shields.io/badge/Flask-2.3+-red)

## 🚀 Fonctionnalités

### Génération de QR Codes
- **Unicité garantie** : Chaque QR code généré est unique grâce à différentes méthodes d'identification
- **Méthodes d'ID disponibles** :
  - UUID (Universally Unique Identifier) - Recommandé
  - Timestamp (Horodatage microseconde)
  - Hash SHA256 (Empreinte cryptographique)
  - Chaîne aléatoire (16 caractères)

### Options de Personnalisation
- **Données personnalisées** : Ajoutez vos propres données au QR code
- **Préfixe personnalisé** : Ajoutez un préfixe pour identifier vos QR codes
- **Inclusion de timestamp** : Option pour ajouter l'horodatage automatiquement
- **Taille ajustable** : Contrôlez la taille des cellules (5-20)
- **Bordure personnalisable** : Ajustez la bordure (1-10 pixels)
- **Correction d'erreur** : 4 niveaux disponibles (L: 7%, M: 15%, Q: 25%, H: 30%)

### Interface Web Intuitive
- **Design moderne** : Interface responsive avec Bootstrap 5
- **Génération en lot** : Créez jusqu'à 50 QR codes d'un coup
- **Prévisualisation immédiate** : Visualisez vos QR codes directement dans le navigateur
- **Téléchargement facile** : Téléchargement individuel ou en lot (ZIP)
- **Historique complet** : Consultez tous vos QR codes générés avec statistiques

### Gestion et Traçabilité
- **Historique persistant** : Toutes les générations sont sauvegardées
- **Vérification d'unicité** : Système de détection des doublons
- **Statistiques détaillées** : Suivi par méthode et analyse temporelle
- **Export complet** : Sauvegarde de tous les QR codes en ZIP

## 📋 Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

## 🛠️ Installation

### 1. Cloner ou télécharger le projet
```bash
git clone [URL_DU_REPO]
cd QRcode
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Lancer l'application
```bash
python app.py
```

L'application sera accessible à l'adresse : `http://localhost:5000`

## 📦 Dépendances

```
qrcode[pil]==7.4.2    # Génération de QR codes avec support PIL
pillow==10.0.0        # Traitement d'images
flask==2.3.3          # Framework web
uuid                  # Génération d'UUID (intégré à Python)
hashlib               # Fonctions de hachage (intégré à Python)
datetime              # Gestion des dates (intégré à Python)
```

## 🎯 Utilisation

### Interface Web

1. **Accédez à l'application** : Ouvrez `http://localhost:5000` dans votre navigateur
2. **Configurez vos paramètres** :
   - Saisissez vos données de base (optionnel)
   - Choisissez un préfixe personnalisé (optionnel)
   - Sélectionnez la méthode de génération d'ID
   - Ajustez les paramètres visuels (taille, bordure, correction d'erreur)
   - Définissez le nombre de QR codes à générer
3. **Générez** : Cliquez sur \"Générer QR Code(s)\"
4. **Téléchargez** : Récupérez vos fichiers PNG individuellement ou en lot

### Utilisation Programmatique

```python
from qr_generator import QRCodeGenerator

# Initialiser le générateur
generator = QRCodeGenerator()

# Générer un QR code simple
img, data, filepath = generator.generate_unique_qr(
    base_data=\"Mon QR Code\",
    id_method=\"uuid\",
    custom_prefix=\"DEMO\"
)

# Générer plusieurs QR codes
batch_results = generator.generate_batch_qr(
    count=5,
    base_data=\"Lot_Test\",
    id_method=\"hash\"
)

# Obtenir des statistiques
stats = generator.get_statistics()
print(f\"Total QR codes générés: {stats['total']}\")

# Vérifier l'unicité
uniqueness = generator.verify_uniqueness()
print(f\"Tous uniques: {uniqueness['is_all_unique']}\")
```

## 📊 Méthodes de Génération d'ID

| Méthode | Description | Exemple | Recommandé pour |
|---------|-------------|---------|-----------------|
| **UUID** | Identifiant universellement unique | `550e8400-e29b-41d4-a716-446655440000` | Usage général, garantie d'unicité maximale |
| **Timestamp** | Horodatage en microsecondes | `1694612345123456` | Traçabilité temporelle |
| **Hash** | SHA256 tronqué | `a1b2c3d4e5f6g7h8` | Sécurité, obfuscation |
| **Random** | Chaîne aléatoire | `Kj3mN9pQ2rT7uW8x` | Simplicité, codes courts |

## 🗂️ Structure du Projet

```
QRcode/
├── app.py                 # Application Flask principale
├── qr_generator.py        # Module de génération de QR codes
├── requirements.txt       # Dépendances Python
├── package.json          # Métadonnées du projet
├── README.md             # Cette documentation
├── templates/            # Templates HTML
│   ├── index.html        # Page d'accueil
│   ├── results.html      # Page de résultats
│   └── history.html      # Page d'historique
├── static/               # Fichiers statiques (vide par défaut)
├── generated_qr/         # QR codes générés (créé automatiquement)
└── qr_history.json       # Historique des générations (créé automatiquement)
```

## 🔧 Configuration

### Paramètres par Défaut

- **Dossier de sortie** : `generated_qr/`
- **Format de fichier** : PNG haute qualité
- **Taille par défaut** : 10 (cellules)
- **Bordure par défaut** : 4 pixels
- **Correction d'erreur** : Moyenne (15%)
- **Port web** : 5000

### Personnalisation

Vous pouvez modifier ces paramètres dans `qr_generator.py` :

```python
class QRCodeGenerator:
    def __init__(self):
        self.output_dir = \"mon_dossier_qr\"  # Changer le dossier de sortie
        self.history_file = \"mon_historique.json\"  # Changer le fichier d'historique
```

## 🌐 API REST

L'application expose également une API REST simple :

### GET `/api/stats`
Retourne les statistiques en format JSON :
```json
{
  \"stats\": {
    \"total\": 42,
    \"methods\": {\"uuid\": 30, \"hash\": 12},
    \"recent\": [...]
  },
  \"uniqueness\": {
    \"total_codes\": 42,
    \"unique_ids\": 42,
    \"duplicates\": [],
    \"is_all_unique\": true
  }
}
```

## 🛡️ Sécurité et Bonnes Pratiques

### Unicité Garantie
- Chaque QR code généré possède un identifiant unique
- Système de détection automatique des doublons
- Historique complet pour traçabilité

### Gestion des Fichiers
- Les QR codes sont stockés localement uniquement
- Aucune donnée n'est envoyée vers des serveurs externes
- Possibilité de nettoyer l'historique à tout moment

### Performance
- Génération optimisée pour de gros volumes
- Gestion intelligente de la mémoire
- Interface responsive pour tous les appareils

## 🚀 Fonctionnalités Avancées

### Génération en Lot
```python
# Générer 100 QR codes uniques
results = generator.generate_batch_qr(
    count=100,
    base_data=\"Campagne_Marketing\",
    id_method=\"uuid\",
    custom_prefix=\"CAMP2024\"
)

# Vérifier les résultats
success_count = sum(1 for r in results if r[\"status\"] == \"success\")
print(f\"{success_count}/100 QR codes générés avec succès\")
```

### Vérification d'Intégrité
```python
# Vérifier l'unicité de tous les QR codes
uniqueness = generator.verify_uniqueness()
if not uniqueness[\"is_all_unique\"]:
    print(f\"Doublons détectés: {uniqueness['duplicates']}\")
```

## 🔍 Dépannage

### Problèmes Courants

**Erreur \"Module not found\"**
```bash
pip install -r requirements.txt
```

**Port 5000 déjà utilisé**
Modifiez le port dans `app.py` :
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

**Permissions de fichier**
Assurez-vous que Python a les droits d'écriture dans le dossier du projet.

### Debug
Pour activer le mode debug détaillé :
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 📈 Statistiques et Monitoring

L'application fournit des statistiques complètes :

- **Total de QR codes générés**
- **Répartition par méthode de génération**
- **Vérification d'unicité en temps réel**
- **Historique chronologique**
- **Détection automatique des anomalies**

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Forker le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :

1. Consultez d'abord cette documentation
2. Vérifiez les issues existantes
3. Créez une nouvelle issue si nécessaire

## 🎉 Crédits

- **qrcode** : Bibliothèque Python pour la génération de QR codes
- **Flask** : Framework web micro en Python
- **Bootstrap** : Framework CSS pour l'interface utilisateur
- **Font Awesome** : Icônes vectorielles

---

**Générateur de QR Codes Uniques** - Créé avec ❤️ en Python
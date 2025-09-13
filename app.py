from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
from ticket_generator import TicketGenerator
from ticket_security import TicketSecurity, TicketValidator
import zipfile
import io
import base64
import json
from PIL import Image
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'qr_generator_secret_key_2024'

# Initialiser le générateur de billets
ticket_gen = TicketGenerator()

@app.route('/')
def index():
    """Page d'accueil avec choix entre QR codes génériques et billets"""
    return render_template('index.html')

@app.route('/ticket-generator', methods=['GET', 'POST'])
def ticket_generator():
    """Générer un billet directement sans formulaire"""
    try:
        # Génération automatique avec des valeurs par défaut
        event_name = "TROPICAL NIGHT HALLOWEEN"
        buyer_name = f"Invité-{datetime.now().strftime('%H%M%S')}"
        
        # Générer le billet
        result = ticket_gen.generate_ticket(event_name, buyer_name)
        
        if result['success']:
            results = []
            
            try:
                # Charger l'image pour l'affichage
                image_path = result['filepath']
                with open(image_path, 'rb') as img_file:
                    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                
                results.append({
                    'success': True,
                    'ticket_id': result['ticket_id'],
                    'buyer_name': buyer_name,
                    'event_name': event_name,
                    'filename': result['filename'],
                    'filepath': result['filepath'],
                    'image_base64': img_base64
                })
                
                flash(f'Billet généré automatiquement pour {buyer_name}!', 'success')
            except Exception as e:
                flash(f'Erreur lors du chargement de l\'image: {str(e)}', 'error')
                return redirect(url_for('index'))
        else:
            flash('Erreur lors de la génération du billet.', 'error')
            return redirect(url_for('index'))
        
        return render_template('ticket_results.html', results=results, batch_count=1)
        
    except Exception as e:
        flash(f'Erreur lors de la génération: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/scanner')
def scanner():
    """Page de scan et validation des billets"""
    return render_template('scanner.html')

@app.route('/validate-ticket', methods=['POST'])
def validate_ticket():
    """Valider un billet scanné"""
    try:
        qr_data = request.form.get('qr_data', '').strip()
        scanner_location = request.form.get('scanner_location', '')
        
        if not qr_data:
            return jsonify({
                'valid': False,
                'error': 'Aucune donnée QR fournie'
            })
        
        # Informations du scanner
        scanner_info = {
            'location': scanner_location,
            'validated_at': request.form.get('timestamp', ''),
            'user_agent': request.headers.get('User-Agent', '')
        }
        
        # Valider le billet
        validation_result = ticket_gen.validate_ticket_qr(qr_data, scanner_info)
        
        return jsonify(validation_result)
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': 'Erreur de validation',
            'details': str(e)
        })

@app.route('/ticket-stats')
def ticket_stats():
    """Page des statistiques de billetterie"""
    stats = ticket_gen.get_event_statistics()
    validation_stats = ticket_gen.validator.get_validation_stats()
    
    return render_template('ticket_stats.html', 
                         stats=stats, 
                         validation_stats=validation_stats)

@app.route('/download/<filename>')
def download_file(filename):
    """Télécharger un fichier QR code"""
    try:
        filepath = os.path.join(ticket_gen.output_dir, filename)
        print(f"Debug - Tentative téléchargement: {filepath}")
        print(f"Debug - Fichier existe: {os.path.exists(filepath)}")
        
        if os.path.exists(filepath):
            print(f"Debug - Envoi du fichier: {filename}")
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            print(f"Debug - Fichier non trouvé: {filepath}")
            flash('Fichier non trouvé.', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        print(f"Debug - Erreur: {str(e)}")
        flash(f'Erreur lors du téléchargement: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download_batch')
def download_batch():
    """Télécharger tous les QR codes récents dans un fichier ZIP"""
    try:
        # Créer un fichier ZIP en mémoire
        memory_file = io.BytesIO()
        
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Ajouter tous les fichiers du dossier generated_tickets
            for filename in os.listdir(ticket_gen.output_dir):
                if filename.endswith('.png'):
                    filepath = os.path.join(ticket_gen.output_dir, filename)
                    zf.write(filepath, filename)
        
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='tickets_batch.zip'
        )
        
    except Exception as e:
        flash(f'Erreur lors de la création du ZIP: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Créer les dossiers nécessaires
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('generated_tickets', exist_ok=True)
    
    print("=== Générateur de Billets Sécurisés ===")
    print("Interface web démarrée sur http://localhost:5000")
    print("Appuyez sur Ctrl+C pour arrêter")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
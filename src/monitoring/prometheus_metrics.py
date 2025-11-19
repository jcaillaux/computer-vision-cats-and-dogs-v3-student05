from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
import os

# ═══════════════════════════════════════════════════════════════════════════
# 📊 MÉTRIQUES CUSTOM - Spécifiques au modèle CV cats/dogs
# ═══════════════════════════════════════════════════════════════════════════

inference_time_histogram = Histogram(
    'cv_inference_time_seconds',
    'Temps d\'inférence en secondes'
)

def track_inference_time(inference_time_ms: float):
    """Enregistre le temps d'inférence"""
    inference_time_histogram.observe(inference_time_ms / 1000)

feedback_counter = Counter(
    name='cv_user_feedback_total',
    documentation='Nombre de feedbacks utilisateurs',
    labelnames=['feedback']  # 0 ou 1
)

def track_feedback(feedback_type: int):
    """Incrémente le compteur de feedbacks"""
    if feedback_type in [0, 1]:
        feedback_counter.labels(feedback=feedback_type).inc()

prediction_confidence_histogram = Histogram(
    'cv_prediction_confidence',
    'Confiance des prédictions du modèle',
    buckets=[0, 10.0, 20.2, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100]
)

def track_confidence(confidence: float):
    """Enregistre la confiance d'une prédiction"""
    prediction_confidence_histogram.observe(confidence)

predicted_target_counter = Counter(
    name='cv_predicted_target_total',
    documentation='Nombre de prédictions par classe',
    labelnames=['target']  # 'cat' ou 'dog'
)

def track_prediction(target: str):
    """Incrémente le compteur de prédictions par classe"""
    if target in ['cat', 'dog']:
        predicted_target_counter.labels(target=target).inc()
# ─────────────────────────────────────────────────────────────────────────────
# 📏 GAUGE : Valeur pouvant monter ET descendre (snapshot de l'état actuel)
# ─────────────────────────────────────────────────────────────────────────────
database_status = Gauge(
    'cv_database_connected',
    'Database connection status (1=connected, 0=disconnected)'
)

def setup_prometheus(app):
    """
    Configure Prometheus pour FastAPI
    
    Args:
        app: Instance FastAPI
    """
    if os.getenv('ENABLE_PROMETHEUS', 'false').lower() == 'true':
        # 📊 INSTRUMENTATION EN 2 ÉTAPES
        # 1. instrument(app) : ajoute middleware pour métriques auto
        # 2. expose(app, endpoint="/metrics") : crée route GET /metrics
        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
        print("✅ Prometheus metrics enabled at /metrics")
        
        # 💡 FORMAT DE SORTIE /metrics
        # Texte brut (Content-Type: text/plain)
        # Scrapable par Prometheus toutes les 15s (cf. prometheus.yml)
    else:
        print("ℹ️  Prometheus metrics disabled")
        # Utile en dev si on veut alléger le monitoring

# ═══════════════════════════════════════════════════════════════════════════
# 📝 HELPERS - Fonctions de tracking appelées par l'API
# ═══════════════════════════════════════════════════════════════════════════

def update_db_status(is_connected: bool):
    """
    Met à jour le statut de la base de données
    
    Args:
        is_connected: True si connexion PostgreSQL active
    """
    database_status.set(1 if is_connected else 0)

# ═══════════════════════════════════════════════════════════════════════════
# 🎓 CONCEPTS AVANCÉS (pour aller plus loin)
# ═══════════════════════════════════════════════════════════════════════════
#
# 1. MÉTRIQUES SUPPLÉMENTAIRES UTILES
#    - model_version (Gauge avec label 'version') : tracking déploiements
#    - input_image_size (Histogram) : détection images hors distribution
#    - gpu_memory_usage (Gauge) : monitoring ressources (si GPU disponible)
#
# 2. CARDINALITY (nombre de combinaisons de labels)
#    ⚠️ Attention : trop de labels = explosion mémoire Prometheus
#    Exemple à ÉVITER : .labels(user_id=...) avec 1M users
#    Limite raisonnable : <10 valeurs par label
#
# 3. MÉTRIQUES VS LOGS
#    - Métriques : agrégées, numériques, queryable (dashboards, alertes)
#    - Logs : détaillés, textuels, debugging (ex: traceback erreurs)
#    Les deux sont complémentaires (pas l'un OU l'autre)
#
# 4. TESTS DES MÉTRIQUES
#    import pytest
#    def test_track_prediction():
#        before = predictions_total._value.get()
#        track_prediction('cat', 100, 0.95)
#        assert predictions_total._value.get() == before + 1

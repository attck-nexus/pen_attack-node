#!/usr/bin/env python3
"""
Flask-based metrics server for GPU monitoring
Exposes Prometheus-compatible metrics and REST API
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from prometheus_client import Counter, Gauge, generate_latest
from monitor import GPUMonitor
import json
import threading
import time

app = Flask(__name__)
CORS(app)

# Initialize monitor
monitor = GPUMonitor()

# Prometheus metrics
gpu_utilization = Gauge('ollama_gpu_utilization_percent', 'GPU Utilization Percentage')
gpu_temperature = Gauge('ollama_gpu_temperature_celsius', 'GPU Temperature in Celsius')
gpu_memory_percent = Gauge('ollama_gpu_memory_percent', 'GPU Memory Usage Percentage')
gpu_memory_mb = Gauge('ollama_gpu_memory_mb', 'GPU Memory Usage in MB')
ollama_models_loaded = Gauge('ollama_models_loaded_total', 'Number of Models Loaded')
cpu_percent = Gauge('system_cpu_percent', 'System CPU Usage Percentage')
system_memory_percent = Gauge('system_memory_percent', 'System Memory Usage Percentage')
disk_percent = Gauge('system_disk_percent', 'System Disk Usage Percentage')

def update_metrics_background():
    """Background thread to update metrics periodically"""
    while True:
        try:
            metrics = monitor.collect_metrics()
            
            if metrics['gpu']['utilization'] is not None:
                gpu_utilization.set(metrics['gpu']['utilization'])
            if metrics['gpu']['temperature'] is not None:
                gpu_temperature.set(metrics['gpu']['temperature'])
            if metrics['gpu']['memory']:
                gpu_memory_percent.set(metrics['gpu']['memory'].get('percent', 0))
                gpu_memory_mb.set(metrics['gpu']['memory'].get('used_mb', 0))
            
            if metrics['ollama']['service_status'] == 'running':
                ollama_models_loaded.set(metrics['ollama'].get('models_loaded', 0))
            
            cpu_percent.set(metrics['system']['cpu_percent'])
            system_memory_percent.set(metrics['system']['memory_percent'])
            disk_percent.set(metrics['system']['disk_percent'])
            
        except Exception as e:
            print(f"Error updating metrics: {e}")
        
        time.sleep(monitor.config.get('update_interval', 5))

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    metrics_data = monitor.get_metrics_dict()
    
    status = 'healthy'
    if metrics_data.get('ollama', {}).get('service_status') != 'running':
        status = 'degraded'
    
    return jsonify({
        'status': status,
        'timestamp': time.time(),
        'components': {
            'gpu': 'online' if metrics_data.get('gpu', {}).get('utilization') is not None else 'offline',
            'ollama': metrics_data.get('ollama', {}).get('service_status', 'unknown'),
            'system': 'online'
        }
    }), 200

@app.route('/api/metrics', methods=['GET'])
def api_metrics():
    """REST API metrics endpoint"""
    return jsonify(monitor.get_metrics_dict()), 200

@app.route('/api/alerts', methods=['GET'])
def api_alerts():
    """Get current alerts"""
    alerts = monitor.check_alerts()
    return jsonify({
        'alerts': alerts,
        'count': len(alerts),
        'timestamp': time.time()
    }), 200

@app.route('/api/history', methods=['GET'])
def api_history():
    """Get metrics history"""
    minutes = request.args.get('minutes', default=60, type=int)
    history = monitor.get_history(minutes)
    
    return jsonify({
        'minutes': minutes,
        'samples': len(history),
        'history': history
    }), 200

@app.route('/api/status', methods=['GET'])
def status():
    """Comprehensive status endpoint"""
    metrics_data = monitor.get_metrics_dict()
    alerts = monitor.check_alerts()
    
    return jsonify({
        'gpu': {
            'utilization': metrics_data['gpu']['utilization'],
            'temperature': metrics_data['gpu']['temperature'],
            'memory': metrics_data['gpu']['memory'],
            'status': 'online' if metrics_data['gpu']['utilization'] is not None else 'offline'
        },
        'ollama': {
            'status': metrics_data['ollama']['service_status'],
            'models_loaded': metrics_data['ollama'].get('models_loaded', 0),
            'models': metrics_data['ollama'].get('models', [])
        },
        'system': metrics_data['system'],
        'alerts': {
            'count': len(alerts),
            'alerts': alerts
        },
        'timestamp': time.time()
    }), 200

if __name__ == '__main__':
    metrics_thread = threading.Thread(target=update_metrics_background, daemon=True)
    metrics_thread.start()
    
    print("Initializing GPU monitor...")
    monitor.collect_metrics()
    print("✓ GPU monitor initialized")
    print("\nStarting metrics server on 0.0.0.0:9100...")
    
    app.run(host='0.0.0.0', port=9100, debug=False, threaded=True)

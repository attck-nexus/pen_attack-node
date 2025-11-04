#!/usr/bin/env python3
"""
Mali GPU and System Monitor for RTPI-PEN
Monitors GPU utilization, memory, temperature, and Ollama service metrics
"""

import os
import json
import subprocess
import time
from datetime import datetime
import psutil
import requests
import yaml
from pathlib import Path

class GPUMonitor:
    def __init__(self, config_path='monitor.yaml'):
        self.config = self._load_config(config_path)
        self.metrics = {}
        self.history = []
        self.max_history = self.config.get('history_size', 3600)
        
    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return self._default_config()
    
    def _default_config(self):
        """Return default configuration"""
        return {
            'ollama_api_url': 'http://localhost:11434',
            'gpu_devices': ['/dev/mali0'],
            'update_interval': 5,
            'history_size': 3600,
            'alerts': {
                'gpu_utilization_threshold': 90,
                'temperature_threshold': 80,
                'memory_threshold': 85
            }
        }
    
    def get_gpu_utilization(self):
        """Get Mali GPU utilization percentage"""
        try:
            utilization_file = '/sys/class/devfreq/fb000000.gpu/cur_freq'
            max_freq_file = '/sys/class/devfreq/fb000000.gpu/max_freq'
            
            if os.path.exists(utilization_file) and os.path.exists(max_freq_file):
                with open(utilization_file, 'r') as f:
                    current_freq = int(f.read().strip())
                with open(max_freq_file, 'r') as f:
                    max_freq = int(f.read().strip())
                
                if max_freq > 0:
                    utilization = (current_freq / max_freq) * 100
                    return round(min(utilization, 100), 2)
            
            thermal_zone = '/sys/class/thermal/thermal_zone0/temp'
            if os.path.exists(thermal_zone):
                with open(thermal_zone, 'r') as f:
                    temp_millideg = int(f.read().strip())
                    temp = temp_millideg / 1000
                    if temp > 60:
                        return round((temp - 40) / 0.4, 2)
            
            return 0.0
        except Exception as e:
            print(f"Error reading GPU utilization: {e}")
            return None
    
    def get_gpu_memory(self):
        """Get GPU memory usage"""
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if 'MemTotal' in line:
                        total_mem = int(line.split()[1]) * 1024
                    elif 'MemAvailable' in line:
                        available_mem = int(line.split()[1]) * 1024
            
            used_mem = total_mem - available_mem
            gpu_mem_percent = (used_mem / total_mem) * 100
            
            return {
                'total_mb': total_mem / (1024 * 1024),
                'used_mb': used_mem / (1024 * 1024),
                'available_mb': available_mem / (1024 * 1024),
                'percent': round(gpu_mem_percent, 2)
            }
        except Exception as e:
            print(f"Error reading GPU memory: {e}")
            return None
    
    def get_gpu_temperature(self):
        """Get GPU temperature in Celsius"""
        try:
            thermal_zones = [
                '/sys/class/thermal/thermal_zone0/temp',
                '/sys/class/thermal/thermal_zone1/temp',
            ]
            
            for zone in thermal_zones:
                if os.path.exists(zone):
                    try:
                        with open(zone, 'r') as f:
                            temp_millideg = int(f.read().strip())
                            temp_celsius = temp_millideg / 1000
                            if 20 < temp_celsius < 150:
                                return round(temp_celsius, 2)
                    except:
                        continue
            
            return None
        except Exception as e:
            print(f"Error reading GPU temperature: {e}")
            return None
    
    def get_ollama_stats(self):
        """Get Ollama service statistics"""
        try:
            url = f"{self.config['ollama_api_url']}/api/tags"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                return {
                    'service_status': 'running',
                    'models_loaded': len(models),
                    'models': [m.get('name', 'unknown') for m in models],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'service_status': 'error', 'status_code': response.status_code}
        except requests.exceptions.ConnectionError:
            return {'service_status': 'offline', 'error': 'Connection refused'}
        except Exception as e:
            return {'service_status': 'error', 'error': str(e)}
    
    def get_system_stats(self):
        """Get system-level statistics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'load_average': os.getloadavg(),
            'timestamp': datetime.now().isoformat()
        }
    
    def collect_metrics(self):
        """Collect all metrics"""
        self.metrics = {
            'gpu': {
                'utilization': self.get_gpu_utilization(),
                'memory': self.get_gpu_memory(),
                'temperature': self.get_gpu_temperature(),
                'timestamp': datetime.now().isoformat()
            },
            'ollama': self.get_ollama_stats(),
            'system': self.get_system_stats()
        }
        
        self.history.append(self.metrics)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        return self.metrics
    
    def check_alerts(self):
        """Check if any metrics exceed alert thresholds"""
        alerts = []
        thresholds = self.config.get('alerts', {})
        
        gpu_util = self.metrics.get('gpu', {}).get('utilization')
        if gpu_util and gpu_util > thresholds.get('gpu_utilization_threshold', 90):
            alerts.append({
                'level': 'warning',
                'type': 'gpu_utilization',
                'value': gpu_util,
                'threshold': thresholds.get('gpu_utilization_threshold', 90)
            })
        
        gpu_temp = self.metrics.get('gpu', {}).get('temperature')
        if gpu_temp and gpu_temp > thresholds.get('temperature_threshold', 80):
            alerts.append({
                'level': 'critical' if gpu_temp > 90 else 'warning',
                'type': 'gpu_temperature',
                'value': gpu_temp,
                'threshold': thresholds.get('temperature_threshold', 80)
            })
        
        gpu_mem = self.metrics.get('gpu', {}).get('memory', {})
        if gpu_mem and gpu_mem.get('percent', 0) > thresholds.get('memory_threshold', 85):
            alerts.append({
                'level': 'warning',
                'type': 'gpu_memory',
                'value': gpu_mem.get('percent'),
                'threshold': thresholds.get('memory_threshold', 85)
            })
        
        return alerts
    
    def get_metrics_dict(self):
        """Return metrics as dictionary"""
        return self.metrics
    
    def get_metrics_json(self):
        """Return metrics as JSON string"""
        return json.dumps(self.metrics, indent=2)
    
    def get_history(self, minutes=60):
        """Get metrics history for last N minutes"""
        cutoff_time = time.time() - (minutes * 60)
        recent_history = []
        
        for metric_set in self.history:
            if metric_set.get('system', {}).get('timestamp'):
                metric_time = datetime.fromisoformat(
                    metric_set['system']['timestamp']
                ).timestamp()
                if metric_time >= cutoff_time:
                    recent_history.append(metric_set)
        
        return recent_history

if __name__ == '__main__':
    monitor = GPUMonitor()
    
    print("GPU Monitor initialized")
    print(f"Config: {monitor.config}")
    print("\nStarting metrics collection...")
    
    while True:
        metrics = monitor.collect_metrics()
        alerts = monitor.check_alerts()
        
        print(f"\n[{datetime.now().isoformat()}] Metrics collected:")
        print(f"  GPU Utilization: {metrics['gpu']['utilization']}%")
        print(f"  GPU Temperature: {metrics['gpu']['temperature']}°C")
        print(f"  GPU Memory: {metrics['gpu']['memory']['percent']}%")
        print(f"  Ollama Status: {metrics['ollama']['service_status']}")
        
        if alerts:
            print(f"\n  ⚠️  ALERTS: {len(alerts)} alert(s)")
            for alert in alerts:
                print(f"    - {alert['type']}: {alert['value']} (threshold: {alert['threshold']})")
        
        time.sleep(monitor.config.get('update_interval', 5))

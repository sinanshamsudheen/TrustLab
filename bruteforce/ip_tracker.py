import sqlite3
import json
from datetime import datetime, timedelta
import os

class IPTracker:
    def __init__(self, db_path="/home/primum/logs/ip_tracking.db"):
        self.db_path = db_path
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalous_ips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL,
                detection_time TIMESTAMP NOT NULL,
                ssh_details TEXT,
                apt_checked BOOLEAN DEFAULT FALSE,
                apt_activities TEXT,
                threat_level INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Index for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_time ON anomalous_ips (ip_address, detection_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_threat_level ON anomalous_ips (threat_level)')
        
        conn.commit()
        conn.close()
    
    def record_anomaly(self, ip, ssh_details):
        """Record a new SSH anomaly"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO anomalous_ips (ip_address, detection_time, ssh_details)
            VALUES (?, ?, ?)
        ''', (ip, datetime.now(), json.dumps(ssh_details)))
        
        conn.commit()
        conn.close()
        
        print(f"[INFO] Recorded anomaly for IP: {ip}")
    
    def get_recent_anomalous_ips(self, hours=24):
        """Get IPs that had anomalies in the last N hours"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT DISTINCT ip_address, MAX(detection_time) as last_seen, 
                   MAX(threat_level) as max_threat_level
            FROM anomalous_ips 
            WHERE detection_time >= ?
            GROUP BY ip_address
            ORDER BY max_threat_level DESC, last_seen DESC
        ''', (cutoff_time,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [(ip, last_seen, threat_level) for ip, last_seen, threat_level in results]
    
    def update_apt_analysis(self, ip, apt_activities):
        """Update the APT analysis for an IP"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate threat level based on activities
        if apt_activities:
            threat_level = 3  # Critical - both SSH anomaly and APT activities
        else:
            threat_level = 1  # Low - only SSH anomaly
        
        # Update the most recent entry for this IP
        cursor.execute('''
            UPDATE anomalous_ips 
            SET apt_checked = TRUE, apt_activities = ?, threat_level = ?
            WHERE ip_address = ? AND id = (
                SELECT id FROM anomalous_ips 
                WHERE ip_address = ? 
                ORDER BY detection_time DESC 
                LIMIT 1
            )
        ''', (
            json.dumps(apt_activities), 
            threat_level,
            ip, 
            ip
        ))
        
        conn.commit()
        conn.close()
        
        print(f"[INFO] Updated APT analysis for IP: {ip}, Threat Level: {threat_level}")
    
    def get_critical_threats(self, hours=24):
        """Get IPs with threat level >= 3 (both SSH and APT activities)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT ip_address, detection_time, ssh_details, apt_activities, threat_level
            FROM anomalous_ips 
            WHERE detection_time >= ? AND threat_level >= 3
            ORDER BY threat_level DESC, detection_time DESC
        ''', (cutoff_time,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def cleanup_old_records(self, days=7):
        """Clean up records older than N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(days=days)
        
        cursor.execute('SELECT COUNT(*) FROM anomalous_ips WHERE detection_time < ?', (cutoff_time,))
        old_count = cursor.fetchone()[0]
        
        cursor.execute('DELETE FROM anomalous_ips WHERE detection_time < ?', (cutoff_time,))
        
        conn.commit()
        conn.close()
        
        if old_count > 0:
            print(f"[INFO] Cleaned up {old_count} old records")
    
    def get_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total records
        cursor.execute('SELECT COUNT(*) FROM anomalous_ips')
        total_records = cursor.fetchone()[0]
        
        # Records by threat level
        cursor.execute('SELECT threat_level, COUNT(*) FROM anomalous_ips GROUP BY threat_level')
        threat_stats = dict(cursor.fetchall())
        
        # Recent records (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        cursor.execute('SELECT COUNT(*) FROM anomalous_ips WHERE detection_time >= ?', (cutoff_time,))
        recent_records = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_records': total_records,
            'threat_level_stats': threat_stats,
            'recent_records_24h': recent_records
        }

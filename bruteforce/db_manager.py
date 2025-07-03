#!/usr/bin/env python3
"""
Database management utility for the enhanced brute force detection system
"""

import argparse
import json
from datetime import datetime, timedelta
from ip_tracker import IPTracker

def show_stats(tracker):
    """Display database statistics"""
    stats = tracker.get_stats()
    
    print("📊 DATABASE STATISTICS")
    print("=" * 40)
    print(f"Total records: {stats['total_records']}")
    print(f"Recent activity (24h): {stats['recent_records_24h']}")
    print("\nThreat level distribution:")
    for level, count in stats['threat_level_stats'].items():
        level_name = {1: "Low", 2: "Medium", 3: "Critical"}.get(level, f"Level {level}")
        print(f"  {level_name}: {count}")

def show_recent_anomalies(tracker, hours=24):
    """Show recent anomalous IPs"""
    recent_ips = tracker.get_recent_anomalous_ips(hours=hours)
    
    print(f"\n🔍 RECENT ANOMALIES (Last {hours}h)")
    print("=" * 50)
    
    if not recent_ips:
        print("No recent anomalies found.")
        return
    
    for ip, last_seen, threat_level in recent_ips:
        level_name = {1: "Low", 2: "Medium", 3: "Critical"}.get(threat_level, f"Level {threat_level}")
        print(f"{ip:15} | {last_seen:19} | {level_name}")

def show_critical_threats(tracker, hours=24):
    """Show critical threats"""
    critical_threats = tracker.get_critical_threats(hours=hours)
    
    print(f"\n🚨 CRITICAL THREATS (Last {hours}h)")
    print("=" * 50)
    
    if not critical_threats:
        print("No critical threats found.")
        return
    
    for record in critical_threats:
        ip, detection_time, ssh_details, apt_activities, threat_level = record
        
        print(f"\nIP: {ip}")
        print(f"Detection: {detection_time}")
        print(f"Threat Level: {threat_level}")
        
        # Parse SSH details
        try:
            ssh_data = json.loads(ssh_details)
            print(f"SSH Details:")
            print(f"  - Attempts: {ssh_data.get('attempts', 'N/A')}")
            print(f"  - Users: {', '.join(ssh_data.get('users', []))}")
            print(f"  - Invalid user attempts: {ssh_data.get('invalid_user', False)}")
        except:
            print(f"SSH Details: {ssh_details}")
        
        # Parse APT activities
        try:
            apt_data = json.loads(apt_activities) if apt_activities else []
            if apt_data:
                print(f"APT Activities: {len(apt_data)} suspicious package operations")
                for activity in apt_data[:3]:  # Show first 3
                    print(f"  - {activity['action']}: {activity['packages'][:50]}...")
        except:
            print(f"APT Activities: {apt_activities}")
        
        print("-" * 30)

def cleanup_database(tracker, days=7):
    """Clean up old records"""
    print(f"\n🧹 CLEANING UP RECORDS OLDER THAN {days} DAYS")
    print("=" * 40)
    
    stats_before = tracker.get_stats()
    tracker.cleanup_old_records(days=days)
    stats_after = tracker.get_stats()
    
    cleaned = stats_before['total_records'] - stats_after['total_records']
    print(f"Cleaned up {cleaned} old records")
    print(f"Remaining records: {stats_after['total_records']}")

def export_data(tracker, hours=24, output_file=None):
    """Export recent data to JSON"""
    if not output_file:
        # Use absolute path in logs directory for default export
        output_file = f"/home/primum/logs/threat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    recent_ips = tracker.get_recent_anomalous_ips(hours=hours)
    critical_threats = tracker.get_critical_threats(hours=hours)
    
    export_data = {
        'export_time': datetime.now().isoformat(),
        'time_window_hours': hours,
        'recent_anomalies': [
            {'ip': ip, 'last_seen': last_seen, 'threat_level': threat_level}
            for ip, last_seen, threat_level in recent_ips
        ],
        'critical_threats': []
    }
    
    for record in critical_threats:
        ip, detection_time, ssh_details, apt_activities, threat_level = record
        export_data['critical_threats'].append({
            'ip': ip,
            'detection_time': detection_time,
            'ssh_details': json.loads(ssh_details) if ssh_details else {},
            'apt_activities': json.loads(apt_activities) if apt_activities else [],
            'threat_level': threat_level
        })
    
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"\n📤 EXPORTED DATA TO: {output_file}")
    print(f"Recent anomalies: {len(export_data['recent_anomalies'])}")
    print(f"Critical threats: {len(export_data['critical_threats'])}")

def main():
    parser = argparse.ArgumentParser(description="Enhanced Brute Force Detection Database Manager")
    parser.add_argument('--db-path', default="/home/primum/logs/ip_tracking.db", 
                       help="Path to the tracking database")
    parser.add_argument('--stats', action='store_true', 
                       help="Show database statistics")
    parser.add_argument('--recent', type=int, metavar='HOURS', 
                       help="Show recent anomalies (specify hours)")
    parser.add_argument('--critical', type=int, metavar='HOURS', 
                       help="Show critical threats (specify hours)")
    parser.add_argument('--cleanup', type=int, metavar='DAYS', 
                       help="Clean up records older than specified days")
    parser.add_argument('--export', type=int, metavar='HOURS', 
                       help="Export data from last N hours to JSON")
    parser.add_argument('--output', help="Output file for export")
    
    args = parser.parse_args()
    
    # Initialize tracker
    tracker = IPTracker(db_path=args.db_path)
    
    # Execute commands
    if args.stats:
        show_stats(tracker)
    
    if args.recent:
        show_recent_anomalies(tracker, hours=args.recent)
    
    if args.critical:
        show_critical_threats(tracker, hours=args.critical)
    
    if args.cleanup:
        cleanup_database(tracker, days=args.cleanup)
    
    if args.export:
        export_data(tracker, hours=args.export, output_file=args.output)
    
    # If no specific command, show default summary
    if not any([args.stats, args.recent, args.critical, args.cleanup, args.export]):
        show_stats(tracker)
        show_recent_anomalies(tracker, hours=24)
        show_critical_threats(tracker, hours=24)

if __name__ == "__main__":
    main()

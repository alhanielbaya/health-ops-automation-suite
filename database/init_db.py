"""
Database initialization script.
Run this to create the database and tables with comprehensive mock data.
"""
import sys
import os
import random
from datetime import datetime, timedelta

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models import init_db, get_session, Asset, User, NetworkConfig, SoftwareVersion, HealthCheck, Alert

def create_sample_data(session):
    """Create comprehensive sample data for testing."""
    
    print("Creating sample users...")
    users_data = [
        {
            'employee_id': 'EMP001',
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@hospital.com',
            'department': 'IT',
            'job_title': 'System Administrator',
            'hire_date': datetime(2023, 1, 15)
        },
        {
            'employee_id': 'EMP002',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'email': 'sarah.johnson@hospital.com',
            'department': 'Cardiology',
            'job_title': 'Cardiac Nurse',
            'hire_date': datetime(2022, 6, 20)
        },
        {
            'employee_id': 'EMP003',
            'first_name': 'Michael',
            'last_name': 'Chen',
            'email': 'michael.chen@hospital.com',
            'department': 'Radiology',
            'job_title': 'Radiology Technician',
            'hire_date': datetime(2023, 3, 10)
        },
        {
            'employee_id': 'EMP004',
            'first_name': 'Emily',
            'last_name': 'Rodriguez',
            'email': 'emily.rodriguez@hospital.com',
            'department': 'Emergency',
            'job_title': 'Emergency Physician',
            'hire_date': datetime(2021, 8, 5)
        },
        {
            'employee_id': 'EMP005',
            'first_name': 'David',
            'last_name': 'Wilson',
            'email': 'david.wilson@hospital.com',
            'department': 'Administration',
            'job_title': 'IT Manager',
            'hire_date': datetime(2020, 11, 12)
        },
        {
            'employee_id': 'EMP006',
            'first_name': 'Lisa',
            'last_name': 'Brown',
            'email': 'lisa.brown@hospital.com',
            'department': 'Pharmacy',
            'job_title': 'Pharmacist',
            'hire_date': datetime(2022, 9, 1)
        },
        {
            'employee_id': 'EMP007',
            'first_name': 'Robert',
            'last_name': 'Taylor',
            'email': 'robert.taylor@hospital.com',
            'department': 'Laboratory',
            'job_title': 'Lab Technician',
            'hire_date': datetime(2023, 7, 15)
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        session.add(user)
        users.append(user)
    
    session.commit()
    print(f"[OK] Created {len(users)} users")
    
    print("\nCreating sample assets...")
    assets_data = [
        # IT Department
        {
            'asset_tag': 'WS-2024-001',
            'asset_type': 'workstation',
            'hostname': 'IT-WS-001',
            'serial_number': 'SN001-DELL-789',
            'manufacturer': 'Dell',
            'model': 'OptiPlex 7090',
            'location': 'IT Department - Floor 2',
            'department': 'IT',
            'user_id': users[0].id,
            'ip': '192.168.1.101',
            'mac': 'AA:BB:CC:11:22:33'
        },
        {
            'asset_tag': 'WS-2024-002',
            'asset_type': 'laptop',
            'hostname': 'IT-LAPTOP-001',
            'serial_number': 'SN002-DELL-456',
            'manufacturer': 'Dell',
            'model': 'Latitude 5520',
            'location': 'IT Department - Floor 2',
            'department': 'IT',
            'user_id': users[4].id,
            'ip': '192.168.1.102',
            'mac': 'AA:BB:CC:11:22:44'
        },
        # Cardiology
        {
            'asset_tag': 'WS-2024-003',
            'asset_type': 'workstation',
            'hostname': 'CARD-WS-001',
            'serial_number': 'SN003-HP-123',
            'manufacturer': 'HP',
            'model': 'EliteDesk 800',
            'location': 'Cardiology - Floor 3',
            'department': 'Cardiology',
            'user_id': users[1].id,
            'ip': '192.168.1.103',
            'mac': 'AA:BB:CC:11:22:55'
        },
        {
            'asset_tag': 'WS-2024-004',
            'asset_type': 'workstation',
            'hostname': 'CARD-WS-002',
            'serial_number': 'SN004-HP-456',
            'manufacturer': 'HP',
            'model': 'EliteDesk 800',
            'location': 'Cardiology - Floor 3',
            'department': 'Cardiology',
            'user_id': None,  # Unassigned
            'ip': '192.168.1.104',
            'mac': 'AA:BB:CC:11:22:66'
        },
        # Radiology
        {
            'asset_tag': 'WS-2024-005',
            'asset_type': 'workstation',
            'hostname': 'RAD-WS-001',
            'serial_number': 'SN005-DELL-111',
            'manufacturer': 'Dell',
            'model': 'Precision 3650',
            'location': 'Radiology - Floor 1',
            'department': 'Radiology',
            'user_id': users[2].id,
            'ip': '192.168.1.105',
            'mac': 'AA:BB:CC:11:22:77'
        },
        {
            'asset_tag': 'WS-2024-006',
            'asset_type': 'server',
            'hostname': 'RAD-SERVER-001',
            'serial_number': 'SN006-DELL-222',
            'manufacturer': 'Dell',
            'model': 'PowerEdge R740',
            'location': 'Server Room - Basement',
            'department': 'Radiology',
            'user_id': None,
            'ip': '192.168.1.106',
            'mac': 'AA:BB:CC:11:22:88'
        },
        # Emergency
        {
            'asset_tag': 'WS-2024-007',
            'asset_type': 'workstation',
            'hostname': 'ER-WS-001',
            'serial_number': 'SN007-HP-789',
            'manufacturer': 'HP',
            'model': 'EliteDesk 800',
            'location': 'Emergency - Floor 1',
            'department': 'Emergency',
            'user_id': users[3].id,
            'ip': '192.168.1.107',
            'mac': 'AA:BB:CC:11:22:99'
        },
        {
            'asset_tag': 'WS-2024-008',
            'asset_type': 'laptop',
            'hostname': 'ER-LAPTOP-001',
            'serial_number': 'SN008-LENOVO-001',
            'manufacturer': 'Lenovo',
            'model': 'ThinkPad X1',
            'location': 'Emergency - Floor 1',
            'department': 'Emergency',
            'user_id': None,
            'ip': '192.168.1.108',
            'mac': 'AA:BB:CC:11:22:AA'
        },
        # Administration
        {
            'asset_tag': 'WS-2024-009',
            'asset_type': 'workstation',
            'hostname': 'ADMIN-WS-001',
            'serial_number': 'SN009-DELL-333',
            'manufacturer': 'Dell',
            'model': 'OptiPlex 7090',
            'location': 'Administration - Floor 2',
            'department': 'Administration',
            'user_id': users[4].id,
            'ip': '192.168.1.109',
            'mac': 'AA:BB:CC:11:22:BB'
        },
        # Pharmacy
        {
            'asset_tag': 'WS-2024-010',
            'asset_type': 'workstation',
            'hostname': 'PHARM-WS-001',
            'serial_number': 'SN010-HP-321',
            'manufacturer': 'HP',
            'model': 'EliteDesk 800',
            'location': 'Pharmacy - Floor 1',
            'department': 'Pharmacy',
            'user_id': users[5].id,
            'ip': '192.168.1.110',
            'mac': 'AA:BB:CC:11:22:CC'
        },
        # Laboratory
        {
            'asset_tag': 'WS-2024-011',
            'asset_type': 'workstation',
            'hostname': 'LAB-WS-001',
            'serial_number': 'SN011-DELL-444',
            'manufacturer': 'Dell',
            'model': 'OptiPlex 7090',
            'location': 'Laboratory - Floor 1',
            'department': 'Laboratory',
            'user_id': users[6].id,
            'ip': '192.168.1.111',
            'mac': 'AA:BB:CC:11:22:DD'
        },
        # Maintenance/Retired assets
        {
            'asset_tag': 'WS-2023-001',
            'asset_type': 'workstation',
            'hostname': 'OLD-WS-001',
            'serial_number': 'SN100-OLD-001',
            'manufacturer': 'Dell',
            'model': 'OptiPlex 7070',
            'location': 'Storage',
            'department': 'IT',
            'user_id': None,
            'status': 'maintenance',
            'ip': '192.168.1.200',
            'mac': 'AA:BB:CC:11:22:EE'
        },
        {
            'asset_tag': 'WS-2022-001',
            'asset_type': 'laptop',
            'hostname': 'RETIRED-001',
            'serial_number': 'SN200-OLD-001',
            'manufacturer': 'HP',
            'model': 'EliteBook 840',
            'location': 'Storage',
            'department': 'IT',
            'user_id': None,
            'status': 'retired',
            'ip': '192.168.1.201',
            'mac': 'AA:BB:CC:11:22:FF'
        }
    ]
    
    assets = []
    for asset_data in assets_data:
        network_info = {
            'ip': asset_data.pop('ip'),
            'mac': asset_data.pop('mac')
        }
        
        asset = Asset(**asset_data)
        session.add(asset)
        assets.append((asset, network_info))
    
    session.commit()
    print(f"[OK] Created {len(assets)} assets")
    
    print("\nCreating network configurations...")
    for asset, network_info in assets:
        network = NetworkConfig(
            asset_id=asset.id,
            ip_address=network_info['ip'],
            subnet_mask='255.255.255.0',
            gateway='192.168.1.1',
            dns_primary='8.8.8.8',
            dns_secondary='8.8.4.4',
            mac_address=network_info['mac'],
            domain='hospital.local',
            vpn_configured=asset.department in ['IT', 'Administration']
        )
        session.add(network)
    
    session.commit()
    print(f"[OK] Created {len(assets)} network configurations")
    
    print("\nCreating software versions...")
    software_templates = [
        {'name': 'Epic Hyperspace', 'vendor': 'Epic Systems', 'required': True, 'medical': True},
        {'name': 'Microsoft Office', 'vendor': 'Microsoft', 'required': True, 'medical': False},
        {'name': 'VPN Client', 'vendor': 'Cisco', 'required': True, 'medical': False},
        {'name': 'Antivirus', 'vendor': 'Symantec', 'required': True, 'medical': False},
        {'name': 'Adobe Acrobat', 'vendor': 'Adobe', 'required': False, 'medical': False},
        {'name': 'Chrome Browser', 'vendor': 'Google', 'required': False, 'medical': False}
    ]
    
    software_versions_list = [
        '2023.1.2', '2023.2.1', '2022.5.3', '16.0.12345', '5.2.1', '15.0.1', '1.2.3', '114.0'
    ]
    
    software_count = 0
    for asset, _ in assets:
        if asset.status != 'active':
            continue
            
        # Each active asset gets 3-5 software packages
        num_software = random.randint(3, 5)
        selected_software = random.sample(software_templates, num_software)
        
        for sw_template in selected_software:
            version = random.choice(software_versions_list)
            is_compliant = random.random() > 0.1  # 90% compliant
            
            software = SoftwareVersion(
                asset_id=asset.id,
                software_name=sw_template['name'],
                version=version,
                vendor=sw_template['vendor'],
                is_required=sw_template['required'],
                is_compliant=is_compliant,
                is_medical_device_software=sw_template['medical'],
                validation_status='validated' if sw_template['medical'] else None,
                install_date=datetime.now() - timedelta(days=random.randint(1, 365))
            )
            session.add(software)
            software_count += 1
    
    session.commit()
    print(f"[OK] Created {software_count} software version entries")
    
    print("\nCreating health check history...")
    # Create health check history for active assets
    health_check_count = 0
    now = datetime.utcnow()
    
    for asset, _ in assets:
        if asset.status != 'active':
            continue
        
        # Create 24 hours of health check history
        for i in range(48):  # Check every 30 minutes for 24 hours
            check_time = now - timedelta(minutes=i*30)
            
            # Random status with weighted probabilities
            rand = random.random()
            if rand < 0.7:  # 70% healthy
                status = 'healthy'
                response_time = random.uniform(20, 800)
                is_reachable = True
                error = None
            elif rand < 0.9:  # 20% warning
                status = 'warning'
                response_time = random.uniform(1000, 4000)
                is_reachable = True
                error = None
            else:  # 10% critical
                status = 'critical'
                response_time = random.uniform(5000, 10000)
                is_reachable = random.random() > 0.3
                error = 'Connection timeout' if not is_reachable else 'High latency'
            
            health_check = HealthCheck(
                asset_id=asset.id,
                check_type='http',
                status=status,
                response_time_ms=response_time,
                is_reachable=is_reachable,
                error_message=error,
                checked_at=check_time,
                created_at=check_time,
                threshold_warning_ms=1000.0,
                threshold_critical_ms=5000.0
            )
            session.add(health_check)
            health_check_count += 1
            
            # Create alert for critical checks (only for recent ones)
            if status == 'critical' and i < 5:  # Last 2.5 hours
                alert = Alert(
                    health_check_id=health_check.id,
                    severity='critical',
                    alert_type='health_check',
                    message=f"Asset {asset.asset_tag} is not responding properly",
                    notification_sent=True,
                    notification_method='console',
                    notification_sent_at=check_time,
                    is_resolved=i > 2,  # Resolved if not in last 1.5 hours
                    resolved_at=check_time + timedelta(minutes=30) if i > 2 else None,
                    created_at=check_time
                )
                session.add(alert)
    
    session.commit()
    print(f"[OK] Created {health_check_count} health check records")
    
    # Create some additional unresolved alerts
    print("\nCreating additional alerts...")
    alert_count = 0
    critical_assets = [a for a, _ in assets if a.status == 'active'][:3]
    
    for asset in critical_assets:
        alert = Alert(
            health_check_id=None,
            severity=random.choice(['warning', 'critical']),
            alert_type='threshold',
            message=f"Disk space low on {asset.hostname}",
            notification_sent=True,
            notification_method='console',
            notification_sent_at=now - timedelta(hours=random.randint(1, 6)),
            is_resolved=False,
            created_at=now - timedelta(hours=random.randint(1, 6))
        )
        session.add(alert)
        alert_count += 1
    
    session.commit()
    print(f"[OK] Created {alert_count} additional alerts")
    
    # Summary
    print("\n" + "="*60)
    print("[SUCCESS] Sample data created successfully!")
    print("="*60)
    print(f"\nDatabase Summary:")
    print(f"  Users: {len(users)}")
    print(f"  Assets: {len(assets)} total")
    print(f"    - Active: {len([a for a, _ in assets if a.status == 'active'])}")
    print(f"    - Maintenance: {len([a for a, _ in assets if a.status == 'maintenance'])}")
    print(f"    - Retired: {len([a for a, _ in assets if a.status == 'retired'])}")
    print(f"  Network Configs: {len(assets)}")
    print(f"  Software Versions: {software_count}")
    print(f"  Health Checks: {health_check_count}")
    print(f"  Alerts: {session.query(Alert).count()}")
    
    print(f"\nDepartments represented:")
    depts = set(a.department for a, _ in assets)
    for dept in sorted(depts):
        count = len([a for a, _ in assets if a.department == dept])
        print(f"  - {dept}: {count} assets")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    print("Initializing Health Ops Database with Mock Data...\n")
    
    # Initialize database (creates tables)
    engine = init_db()
    
    # Clear existing data if any
    from models.base import Base
    print("Clearing existing data...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("[OK] Database reset\n")
    
    # Create sample data
    session = get_session(engine)
    
    try:
        create_sample_data(session)
    except Exception as e:
        print(f"\n[ERROR] Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()
    
    print("\nDatabase setup complete!")
    print("\nYou can now:")
    print("  1. Start the dashboard: cd monitoring-service && python start_dashboard.py")
    print("  2. Run CLI commands: cd cli-tool && bun run src/index.ts report")
    print("  3. Test monitoring: cd monitoring-service && python tests/test_monitor.py")

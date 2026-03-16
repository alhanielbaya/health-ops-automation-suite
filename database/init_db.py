"""
Database initialization script.
Run this to create the database and tables.
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models import init_db, get_session, Asset, User, NetworkConfig, SoftwareVersion
from datetime import datetime

def create_sample_data(session):
    """Create sample data for testing."""
    
    # Create a user
    user = User(
        employee_id='EMP001',
        first_name='John',
        last_name='Smith',
        email='john.smith@hospital.com',
        department='IT',
        job_title='System Administrator',
        hire_date=datetime(2023, 1, 15)
    )
    session.add(user)
    session.commit()
    print(f"[OK] Created user: {user.full_name}")
    
    # Create an asset
    asset = Asset(
        asset_tag='WS-2024-001',
        asset_type='workstation',
        hostname='IT-WS-001',
        serial_number='SN123456789',
        manufacturer='Dell',
        model='OptiPlex 7090',
        location='IT Department - Floor 2',
        department='IT',
        user_id=user.id
    )
    session.add(asset)
    session.commit()
    print(f"[OK] Created asset: {asset.asset_tag}")
    
    # Create network config
    network = NetworkConfig(
        asset_id=asset.id,
        ip_address='192.168.1.100',
        subnet_mask='255.255.255.0',
        gateway='192.168.1.1',
        dns_primary='8.8.8.8',
        dns_secondary='8.8.4.4',
        mac_address='AA:BB:CC:DD:EE:FF',
        domain='hospital.local',
        vpn_configured=True
    )
    session.add(network)
    session.commit()
    print(f"[OK] Created network config for: {asset.asset_tag}")
    
    # Create software entries
    software_list = [
        SoftwareVersion(
            asset_id=asset.id,
            software_name='Epic Hyperspace',
            version='2023.1.2',
            vendor='Epic Systems',
            is_required=True,
            is_medical_device_software=True,
            validation_status='validated'
        ),
        SoftwareVersion(
            asset_id=asset.id,
            software_name='Microsoft Office',
            version='16.0.12345',
            vendor='Microsoft',
            is_required=True
        ),
        SoftwareVersion(
            asset_id=asset.id,
            software_name='VPN Client',
            version='5.2.1',
            vendor='Cisco',
            is_required=True
        )
    ]
    
    for software in software_list:
        session.add(software)
    
    session.commit()
    print(f"[OK] Created {len(software_list)} software entries")
    
    print("\n[SUCCESS] Sample data created successfully!")
    print(f"   Database location: ./health_ops.db")
    print(f"   User: {user.full_name}")
    print(f"   Asset: {asset.asset_tag}")

if __name__ == '__main__':
    print("Initializing Health Ops Database...\n")
    
    # Initialize database (creates tables)
    engine = init_db()
    
    # Create sample data
    session = get_session(engine)
    
    try:
        create_sample_data(session)
    except Exception as e:
        print(f"[ERROR] Error creating sample data: {e}")
    finally:
        session.close()
    
    print("\nDatabase setup complete!")
    print("\nYou can now:")
    print("  1. Query the database using SQLAlchemy")
    print("  2. Build the monitoring service")
    print("  3. Create the CLI tool")

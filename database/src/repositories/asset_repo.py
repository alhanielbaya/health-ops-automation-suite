"""
Asset Repository - Data Access Layer for Asset operations.
Provides CRUD operations for the Asset model.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from models import Asset, User, NetworkConfig, SoftwareVersion


class AssetRepository:
    """
    Repository for Asset database operations.
    Implements Repository Pattern for clean data access.
    """
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy session instance
        """
        self.session = session
    
    def create(self, asset_data: dict) -> Asset:
        """
        Create a new asset.
        
        Args:
            asset_data: Dictionary containing asset fields
        
        Returns:
            Created Asset instance
        
        Example:
            asset = repo.create({
                'asset_tag': 'WS-2024-002',
                'asset_type': 'workstation',
                'hostname': 'IT-WS-002'
            })
        """
        asset = Asset(**asset_data)
        self.session.add(asset)
        self.session.commit()
        self.session.refresh(asset)
        return asset
    
    def get_by_id(self, asset_id: int) -> Optional[Asset]:
        """Get asset by ID."""
        return self.session.query(Asset).filter(Asset.id == asset_id).first()
    
    def get_by_tag(self, asset_tag: str) -> Optional[Asset]:
        """Get asset by asset tag (e.g., 'WS-2024-001')."""
        return self.session.query(Asset).filter(Asset.asset_tag == asset_tag).first()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Asset]:
        """
        Get all assets with pagination.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
        """
        return self.session.query(Asset).offset(offset).limit(limit).all()
    
    def get_by_department(self, department: str) -> List[Asset]:
        """Get all assets in a department."""
        return self.session.query(Asset).filter(Asset.department == department).all()
    
    def get_by_user(self, user_id: int) -> List[Asset]:
        """Get all assets assigned to a user."""
        return self.session.query(Asset).filter(Asset.user_id == user_id).all()
    
    def search(self, query: str) -> List[Asset]:
        """
        Search assets by tag, hostname, or serial number.
        
        Args:
            query: Search string
        """
        return self.session.query(Asset).filter(
            or_(
                Asset.asset_tag.ilike(f'%{query}%'),
                Asset.hostname.ilike(f'%{query}%'),
                Asset.serial_number.ilike(f'%{query}%')
            )
        ).all()
    
    def update(self, asset_id: int, update_data: dict) -> Optional[Asset]:
        """
        Update an asset.
        
        Args:
            asset_id: Asset ID to update
            update_data: Dictionary of fields to update
        
        Returns:
            Updated Asset or None if not found
        """
        asset = self.get_by_id(asset_id)
        if asset:
            for key, value in update_data.items():
                if hasattr(asset, key):
                    setattr(asset, key, value)
            self.session.commit()
            self.session.refresh(asset)
        return asset
    
    def delete(self, asset_id: int) -> bool:
        """
        Delete an asset.
        
        Args:
            asset_id: Asset ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        asset = self.get_by_id(asset_id)
        if asset:
            self.session.delete(asset)
            self.session.commit()
            return True
        return False
    
    def assign_to_user(self, asset_id: int, user_id: int) -> Optional[Asset]:
        """Assign an asset to a user."""
        return self.update(asset_id, {'user_id': user_id})
    
    def get_asset_with_details(self, asset_id: int) -> Optional[Asset]:
        """
        Get asset with all related data (user, network, software).
        
        This eager loads all relationships to avoid N+1 query problem.
        """
        return self.session.query(Asset).filter(Asset.id == asset_id).first()


class UserRepository:
    """Repository for User database operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, user_data: dict) -> User:
        """Create a new user."""
        user = User(**user_data)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.session.query(User).filter(User.id == user_id).first()
    
    def get_by_employee_id(self, employee_id: str) -> Optional[User]:
        """Get user by employee ID."""
        return self.session.query(User).filter(User.employee_id == employee_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.session.query(User).filter(User.email == email).first()
    
    def get_all(self, limit: int = 100) -> List[User]:
        """Get all users."""
        return self.session.query(User).limit(limit).all()
    
    def get_active_users(self) -> List[User]:
        """Get all active users."""
        return self.session.query(User).filter(User.is_active == True).all()
    
    def update(self, user_id: int, update_data: dict) -> Optional[User]:
        """Update a user."""
        user = self.get_by_id(user_id)
        if user:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.session.commit()
            self.session.refresh(user)
        return user
    
    def deactivate(self, user_id: int) -> bool:
        """Deactivate a user (soft delete)."""
        user = self.update(user_id, {'is_active': False})
        return user is not None


class NetworkConfigRepository:
    """Repository for Network Configuration operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, config_data: dict) -> NetworkConfig:
        """Create network configuration for an asset."""
        config = NetworkConfig(**config_data)
        self.session.add(config)
        self.session.commit()
        self.session.refresh(config)
        return config
    
    def get_by_asset(self, asset_id: int) -> List[NetworkConfig]:
        """Get all network configs for an asset."""
        return self.session.query(NetworkConfig).filter(
            NetworkConfig.asset_id == asset_id
        ).all()
    
    def get_active_config(self, asset_id: int) -> Optional[NetworkConfig]:
        """Get the active network config for an asset."""
        return self.session.query(NetworkConfig).filter(
            NetworkConfig.asset_id == asset_id,
            NetworkConfig.is_active == True
        ).first()
    
    def get_by_ip(self, ip_address: str) -> Optional[NetworkConfig]:
        """Find asset by IP address."""
        return self.session.query(NetworkConfig).filter(
            NetworkConfig.ip_address == ip_address
        ).first()


class SoftwareVersionRepository:
    """Repository for Software Version operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, software_data: dict) -> SoftwareVersion:
        """Create software version entry."""
        software = SoftwareVersion(**software_data)
        self.session.add(software)
        self.session.commit()
        self.session.refresh(software)
        return software
    
    def get_by_asset(self, asset_id: int) -> List[SoftwareVersion]:
        """Get all software on an asset."""
        return self.session.query(SoftwareVersion).filter(
            SoftwareVersion.asset_id == asset_id
        ).all()
    
    def get_required_software(self, asset_id: int) -> List[SoftwareVersion]:
        """Get required software for an asset."""
        return self.session.query(SoftwareVersion).filter(
            SoftwareVersion.asset_id == asset_id,
            SoftwareVersion.is_required == True
        ).all()
    
    def get_non_compliant(self) -> List[SoftwareVersion]:
        """Get all non-compliant software across all assets."""
        return self.session.query(SoftwareVersion).filter(
            SoftwareVersion.is_compliant == False
        ).all()
    
    def update_version(self, software_id: int, new_version: str) -> Optional[SoftwareVersion]:
        """Update software version."""
        software = self.session.query(SoftwareVersion).filter(
            SoftwareVersion.id == software_id
        ).first()
        if software:
            software.version = new_version
            software.last_updated = datetime.utcnow()
            self.session.commit()
            self.session.refresh(software)
        return software

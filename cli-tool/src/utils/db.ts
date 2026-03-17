/**
 * Database Client - Real SQLite database connection using bun:sqlite
 * Provides actual CRUD operations for the Health Ops database
 */
import { Database } from 'bun:sqlite';
import * as path from 'path';

export class DatabaseClient {
  private db: Database;
  
  constructor() {
    // Connect to the actual SQLite database
    const dbPath = path.join(process.cwd(), '..', 'database', 'health_ops.db');
    this.db = new Database(dbPath);
    console.log(`  Connected to database: ${dbPath}`);
  }
  
  /**
   * Create a new user in the database
   */
  async createUser(userData: any): Promise<number> {
    const stmt = this.db.prepare(`
      INSERT INTO users (employee_id, first_name, last_name, email, department, job_title, phone, is_active, hire_date, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    `);
    
    const result = stmt.run(
      userData.employeeId,
      userData.firstName,
      userData.lastName,
      userData.email,
      userData.department,
      userData.jobTitle,
      userData.phone,
      userData.isActive ? 1 : 0,
      userData.hireDate || null
    );
    
    console.log(`  Created user ID: ${result.lastInsertRowid}`);
    return result.lastInsertRowid as number;
  }
  
  /**
   * Find a user by employee ID
   */
  async findUserByEmployeeId(employeeId: string): Promise<any | null> {
    const stmt = this.db.prepare('SELECT * FROM users WHERE employee_id = ?');
    const user = stmt.get(employeeId);
    return user || null;
  }
  
  /**
   * Create a new asset in the database
   */
  async createAsset(assetData: any, userId?: number): Promise<number> {
    const stmt = this.db.prepare(`
      INSERT INTO assets (asset_tag, asset_type, hostname, serial_number, manufacturer, model, status, location, department, user_id, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    `);
    
    const result = stmt.run(
      assetData.assetTag,
      assetData.assetType,
      assetData.hostname,
      assetData.serialNumber || null,
      assetData.manufacturer || null,
      assetData.model || null,
      assetData.status || 'active',
      assetData.location,
      assetData.department || null,
      userId || null
    );
    
    const assetId = result.lastInsertRowid as number;
    console.log(`  Created asset ID: ${assetId}`);
    
    // Also create network configuration
    await this.createNetworkConfig(assetId, assetData);
    
    return assetId;
  }
  
  /**
   * Create network configuration for an asset
   */
  private async createNetworkConfig(assetId: number, assetData: any): Promise<void> {
    const stmt = this.db.prepare(`
      INSERT INTO network_configs (asset_id, ip_address, subnet_mask, gateway, dns_primary, dns_secondary, mac_address, domain, vpn_configured, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    `);
    
    stmt.run(
      assetId,
      assetData.ipAddress,
      assetData.subnetMask,
      assetData.gateway,
      assetData.dnsPrimary,
      assetData.dnsSecondary,
      null, // MAC address - would need to get from system
      assetData.domain,
      0 // vpn_configured - would need to check actual system
    );
    
    console.log(`  Created network config for asset ID: ${assetId}`);
  }
  
  /**
   * Record software installation for an asset
   */
  async recordSoftware(assetTag: string, software: any): Promise<void> {
    // First find the asset ID
    const assetStmt = this.db.prepare('SELECT id FROM assets WHERE asset_tag = ?');
    const asset = assetStmt.get(assetTag) as { id: number } | undefined;
    
    if (!asset) {
      throw new Error(`Asset ${assetTag} not found`);
    }
    
    const stmt = this.db.prepare(`
      INSERT INTO software_versions (asset_id, software_name, version, vendor, is_required, is_compliant, fda_approved, is_medical_device_software, install_date, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), datetime('now'))
    `);
    
    stmt.run(
      asset.id,
      software.name,
      software.version,
      software.vendor || 'Unknown',
      software.required ? 1 : 0,
      1, // Assume compliant when just installed
      software.fdaApproved ? 1 : 0,
      software.fdaApproved ? 1 : 0 // If FDA approved, it's medical device software
    );
    
    console.log(`  Recorded software: ${software.name} v${software.version} for asset ${assetTag}`);
  }
  
  /**
   * Update VPN configuration for an asset
   */
  async updateVPNConfig(assetTag: string, vpnConfig: any): Promise<void> {
    // First find the asset ID
    const assetStmt = this.db.prepare('SELECT id FROM assets WHERE asset_tag = ?');
    const asset = assetStmt.get(assetTag) as { id: number } | undefined;
    
    if (!asset) {
      throw new Error(`Asset ${assetTag} not found`);
    }
    
    const stmt = this.db.prepare(`
      UPDATE network_configs 
      SET vpn_configured = ?, last_configured = datetime('now')
      WHERE asset_id = ?
    `);
    
    stmt.run(vpnConfig.enabled ? 1 : 0, asset.id);
    
    if (vpnConfig.enabled) {
      console.log(`  VPN enabled for ${assetTag} (${vpnConfig.profile || 'Standard'})`);
    }
  }
  
  /**
   * Get asset by tag
   */
  async getAsset(assetTag: string): Promise<any | null> {
    const stmt = this.db.prepare(`
      SELECT a.*, u.first_name || ' ' || u.last_name as user_name
      FROM assets a
      LEFT JOIN users u ON a.user_id = u.id
      WHERE a.asset_tag = ?
    `);
    return stmt.get(assetTag) || null;
  }
  
  /**
   * Get all assets with optional filtering
   */
  async getAllActiveAssets(): Promise<any[]> {
    const stmt = this.db.prepare(`
      SELECT a.*, u.first_name || ' ' || u.last_name as user_name
      FROM assets a
      LEFT JOIN users u ON a.user_id = u.id
      WHERE a.status = 'active'
      ORDER BY a.asset_tag
    `);
    return stmt.all() as any[];
  }
  
  /**
   * Get assets by department
   */
  async getAssetsByDepartment(department: string): Promise<any[]> {
    const stmt = this.db.prepare(`
      SELECT a.*, u.first_name || ' ' || u.last_name as user_name
      FROM assets a
      LEFT JOIN users u ON a.user_id = u.id
      WHERE a.department = ? AND a.status = 'active'
      ORDER BY a.asset_tag
    `);
    return stmt.all(department) as any[];
  }
  
  /**
   * Update asset assignment
   */
  async assignAssetToUser(assetTag: string, employeeId: string): Promise<void> {
    // Find user ID
    const userStmt = this.db.prepare('SELECT id FROM users WHERE employee_id = ?');
    const user = userStmt.get(employeeId) as { id: number } | undefined;
    
    if (!user) {
      throw new Error(`User with employee ID ${employeeId} not found`);
    }
    
    // Update asset
    const stmt = this.db.prepare(`
      UPDATE assets 
      SET user_id = ?, updated_at = datetime('now')
      WHERE asset_tag = ?
    `);
    
    stmt.run(user.id, assetTag);
    console.log(`  Assigned asset ${assetTag} to user ${employeeId}`);
  }
  
  /**
   * Close database connection
   */
  close(): void {
    this.db.close();
  }
}

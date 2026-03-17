/**
 * Test suite for CLI Tool
 */
import { describe, it, expect } from "bun:test";
import { DatabaseClient } from "../src/utils/db";

describe("CLI Tool Tests", () => {
  
  describe("DatabaseClient", () => {
    const db = new DatabaseClient();
    
    it("should get all active assets", async () => {
      const assets = await db.getAllActiveAssets();
      expect(assets).toBeArray();
      expect(assets.length).toBeGreaterThan(0);
    });
    
    it("should get asset by tag", async () => {
      const asset = await db.getAsset("WS-2024-001");
      expect(asset).toBeDefined();
      expect(asset?.asset_tag).toBe("WS-2024-001");
    });
    
    it("should return null for non-existent asset", async () => {
      const asset = await db.getAsset("NON-EXISTENT-TAG");
      expect(asset).toBeNull();
    });
    
    it("should create and retrieve new user", async () => {
      const timestamp = Date.now();
      const userData = {
        employeeId: `TEST-${timestamp}`,
        firstName: "Test",
        lastName: "User",
        email: `test-${timestamp}@example.com`,
        department: "IT",
        jobTitle: "Test Engineer",
        phone: "555-TEST",
        isActive: true,
        hireDate: new Date().toISOString()
      };
      
      const userId = await db.createUser(userData);
      expect(userId).toBeGreaterThan(0);
      
      const foundUser = await db.findUserByEmployeeId(`TEST-${timestamp}`);
      expect(foundUser).toBeDefined();
      expect(foundUser?.first_name).toBe("Test");
    });
  });
  
});

console.log("CLI Tool test suite loaded!");
console.log("Run with: bun test");

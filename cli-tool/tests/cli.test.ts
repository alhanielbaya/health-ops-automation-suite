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
    
    it("should return asset object for any tag", async () => {
      // Note: Mock DB always returns an asset for demo purposes
      const asset = await db.getAsset("ANY-TAG");
      expect(asset).toBeDefined();
      expect(asset?.asset_tag).toBe("ANY-TAG");
    });
  });
  
});

console.log("CLI Tool test suite loaded!");
console.log("Run with: bun test");

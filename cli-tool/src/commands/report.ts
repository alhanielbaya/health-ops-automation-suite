import chalk from 'chalk';
import { DatabaseClient } from '../utils/db';

interface ReportOptions {
  type?: string;
  format?: string;
  output?: string;
  department?: string;
}

export async function reportCommand(options: ReportOptions): Promise<void> {
  console.log(chalk.blue.bold('\n[ Health Ops Report Generation ]\n'));
  
  const db = new DatabaseClient();
  
  try {
    const assets = await db.getAllActiveAssets();
    
    console.log(chalk.white('Report Type:'), options.type || 'compliance');
    console.log(chalk.white('Format:'), options.format || 'table');
    console.log(chalk.white('Total Assets:'), assets.length);
    console.log();
    
    if (assets.length === 0) {
      console.log(chalk.yellow('No assets found in database.'));
      return;
    }
    
    // Display assets in table format
    console.log(chalk.blue('Asset Inventory:'));
    console.log(chalk.gray('-'.repeat(80)));
    console.log(chalk.gray('Asset Tag      | Type        | Hostname          | Department'));
    console.log(chalk.gray('-'.repeat(80)));
    
    for (const asset of assets) {
      const tag = asset.asset_tag.padEnd(14);
      const type = (asset.asset_type || 'unknown').padEnd(11);
      const host = (asset.hostname || 'N/A').padEnd(17);
      const dept = asset.department || 'N/A';
      console.log(`${tag}| ${type}| ${host}| ${dept}`);
    }
    
    console.log(chalk.gray('-'.repeat(80)));
    console.log();
    console.log(chalk.green('Report generated successfully!'));
    
  } catch (error) {
    console.error(chalk.red('Report generation failed:'), error);
    throw error;
  }
}

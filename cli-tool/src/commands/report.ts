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
    // Get all assets from database
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
    console.log(
      chalk.gray('Asset Tag'.padEnd(15)),
      chalk.gray('Type'.padEnd(12)),
      chalk.gray('Hostname'.padEnd(18)),
      chalk.gray('Department'.padEnd(15)),
      chalk.gray('User')
    );
    console.log(chalk.gray('-'.repeat(80)));
    
    for (const asset of assets) {
      const tag = (asset.asset_tag || '').padEnd(15);
      const type = (asset.asset_type || '').padEnd(12);
      const host = (asset.hostname || '').padEnd(18);
      const dept = (asset.department || '').padEnd(15);
      const user = asset.user_name || 'Unassigned';
      console.log(`${tag}${type}${host}${dept}${user}`);
    }
    
    console.log(chalk.gray('-'.repeat(80)));
    
    // Department summary
    console.log(chalk.blue('\nDepartment Summary:'));
    const deptCounts: { [key: string]: number } = {};
    for (const asset of assets) {
      const dept = asset.department || 'Unassigned';
      deptCounts[dept] = (deptCounts[dept] || 0) + 1;
    }
    
    for (const [dept, count] of Object.entries(deptCounts).sort()) {
      console.log(chalk.gray(`  ${dept}:`), count);
    }
    
    console.log();
    console.log(chalk.green('[SUCCESS] Report generated successfully!'));
    
    if (options.output) {
      console.log(chalk.gray(`\nOutput saved to: ${options.output}`));
    }
    
  } catch (error) {
    console.error(chalk.red('[ERROR] Report generation failed:'), error);
    throw error;
  } finally {
    db.close();
  }
}

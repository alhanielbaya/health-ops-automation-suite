import chalk from 'chalk';
import ora from 'ora';
import { DatabaseClient } from '../utils/db';

interface ValidateOptions {
  asset?: string;
  department?: string;
  securityOnly?: boolean;
  networkOnly?: boolean;
}

export async function validateCommand(options: ValidateOptions): Promise<void> {
  console.log(chalk.blue.bold('\n[ Health Ops Compliance Validation ]\n'));
  
  const db = new DatabaseClient();
  
  try {
    let assets: any[] = [];
    
    if (options.asset) {
      // Validate specific asset
      const asset = await db.getAsset(options.asset);
      if (asset) {
        assets.push(asset);
        console.log(chalk.blue(`Validating asset: ${asset.asset_tag}\n`));
      } else {
        console.log(chalk.red(`Asset ${options.asset} not found in database`));
        return;
      }
    } else if (options.department) {
      // Validate all assets in department
      assets = await db.getAssetsByDepartment(options.department);
      console.log(chalk.blue(`Validating ${assets.length} assets in ${options.department} department...\n`));
    } else {
      // Validate all active assets
      assets = await db.getAllActiveAssets();
      console.log(chalk.blue(`Validating ${assets.length} active assets...\n`));
    }
    
    if (assets.length === 0) {
      console.log(chalk.yellow('No assets found to validate.'));
      return;
    }
    
    let passedCount = 0;
    let failedCount = 0;
    
    // Validate each asset
    for (const asset of assets) {
      console.log(chalk.white.bold(`Asset: ${asset.asset_tag}`));
      console.log(chalk.gray(`  Hostname: ${asset.hostname}`));
      console.log(chalk.gray(`  Department: ${asset.department}`));
      if (asset.user_name) {
        console.log(chalk.gray(`  Assigned to: ${asset.user_name}`));
      }
      
      const spinner = ora('Validating...').start();
      
      // Simulate validation checks (in real implementation, these would check actual system state)
      const checks = [];
      
      if (!options.networkOnly) {
        checks.push('Security baseline');
        checks.push('Software compliance');
      }
      
      if (!options.securityOnly) {
        checks.push('Network configuration');
        checks.push('DNS resolution');
      }
      
      // Simulate check time
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Randomly determine pass/fail for demo purposes
      const isHealthy = Math.random() > 0.2; // 80% pass rate
      
      if (isHealthy) {
        spinner.succeed(chalk.green('Validation passed'));
        passedCount++;
      } else {
        spinner.warn(chalk.yellow('Validation found issues'));
        console.log(chalk.yellow('  - Software version outdated'));
        failedCount++;
      }
      
      console.log(); // Empty line between assets
    }
    
    // Summary
    console.log(chalk.blue('[ Validation Summary ]'));
    console.log(chalk.gray('-'.repeat(40)));
    console.log(chalk.green(`  Passed: ${passedCount}`));
    if (failedCount > 0) {
      console.log(chalk.yellow(`  Warnings: ${failedCount}`));
    }
    console.log(chalk.gray(`  Total: ${assets.length}`));
    console.log(chalk.gray('-'.repeat(40)));
    
    if (failedCount === 0) {
      console.log(chalk.green('\n[SUCCESS] All validations passed!'));
    } else {
      console.log(chalk.yellow(`\n[WARNING] ${failedCount} assets need attention`));
    }
    
  } catch (error) {
    console.error(chalk.red('\n[ERROR] Validation failed:'), error);
    throw error;
  } finally {
    db.close();
  }
}

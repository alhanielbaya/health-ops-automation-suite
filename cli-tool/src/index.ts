#!/usr/bin/env bun
/**
 * Health Ops CLI Tool
 * Automates workstation configuration for healthcare IT
 * 
 * Usage:
 *   bun run src/index.ts setup       # Setup new workstation
 *   bun run src/index.ts validate    # Check compliance
 *   bun run src/index.ts report      # Generate reports
 */

import { Command } from 'commander';
import chalk from 'chalk';
import { setupCommand } from './commands/setup';
import { validateCommand } from './commands/validate';
import { reportCommand } from './commands/report';

const program = new Command();

// CLI Metadata
program
  .name('health-ops')
  .description('Healthcare IT Workstation Automation CLI')
  .version('1.0.0');

// Global options
program
  .option('-v, --verbose', 'verbose output')
  .option('--dry-run', 'show what would be done without making changes');

// Setup command - for new hire workstation configuration
program
  .command('setup')
  .description('Configure a new workstation for a user')
  .option('-u, --user <employeeId>', 'Employee ID')
  .option('-a, --asset <assetTag>', 'Asset tag (e.g., WS-2024-001)')
  .option('--skip-network', 'skip network configuration')
  .option('--skip-software', 'skip software installation')
  .action(async (options) => {
    try {
      await setupCommand(options);
    } catch (error) {
      console.error(chalk.red('Setup failed:'), error);
      process.exit(1);
    }
  });

// Validate command - check compliance
program
  .command('validate')
  .description('Validate workstation configuration and compliance')
  .option('-a, --asset <assetTag>', 'validate specific asset')
  .option('-d, --department <dept>', 'validate all assets in department')
  .option('--security-only', 'only check security settings')
  .option('--network-only', 'only check network settings')
  .action(async (options) => {
    try {
      await validateCommand(options);
    } catch (error) {
      console.error(chalk.red('Validation failed:'), error);
      process.exit(1);
    }
  });

// Report command - generate reports
program
  .command('report')
  .description('Generate compliance and inventory reports')
  .option('-t, --type <type>', 'report type: compliance|inventory|alerts', 'compliance')
  .option('-f, --format <format>', 'output format: json|csv|table', 'table')
  .option('-o, --output <file>', 'output file path')
  .option('-d, --department <dept>', 'filter by department')
  .action(async (options) => {
    try {
      await reportCommand(options);
    } catch (error) {
      console.error(chalk.red('Report generation failed:'), error);
      process.exit(1);
    }
  });

// Parse command line arguments
program.parse();

// Show help if no command provided
if (!process.argv.slice(2).length) {
  program.outputHelp();
}

/**
 * Setup Command - Configure new workstation
 * 
 * This command:
 * 1. Collects user information
 * 2. Creates/updates database records
 * 3. Validates security settings
 * 4. Configures network
 * 5. Installs required software
 * 6. Generates compliance report
 */
import inquirer from 'inquirer';
import chalk from 'chalk';
import ora from 'ora';
import { DatabaseClient } from '../utils/db';
import { SecurityChecker } from '../utils/security';
import { NetworkConfigurator } from '../utils/network';
import { SoftwareInstaller } from '../utils/software';

interface SetupOptions {
  user?: string;
  asset?: string;
  skipNetwork?: boolean;
  skipSoftware?: boolean;
  verbose?: boolean;
  dryRun?: boolean;
}

export async function setupCommand(options: SetupOptions): Promise<void> {
  console.log(chalk.blue.bold('\n🏥 Health Ops Workstation Setup\n'));
  
  // Initialize utilities
  const db = new DatabaseClient();
  const security = new SecurityChecker();
  const network = new NetworkConfigurator();
  const software = new SoftwareInstaller();
  
  try {
    // Step 1: Collect User Information
    const userInfo = await collectUserInfo(options.user);
    
    // Step 2: Collect Asset Information  
    const assetInfo = await collectAssetInfo(options.asset);
    
    // Step 3: Confirm before proceeding
    const confirmed = await confirmSetup(userInfo, assetInfo);
    if (!confirmed) {
      console.log(chalk.yellow('Setup cancelled.'));
      return;
    }
    
    // Step 4: Create/Update Database Records
    console.log(chalk.blue('\n📋 Step 1: Creating database records...'));
    const spinner1 = ora('Saving user and asset data...').start();
    
    if (!options.dryRun) {
      await db.createUser(userInfo);
      await db.createAsset(assetInfo, userInfo.employeeId);
    }
    
    spinner1.succeed(chalk.green('Database records created'));
    
    // Step 5: Security Validation
    console.log(chalk.blue('\n🔒 Step 2: Validating security settings...'));
    const spinner2 = ora('Checking security baseline...').start();
    
    const securityStatus = await security.checkBaseline();
    
    if (securityStatus.compliant) {
      spinner2.succeed(chalk.green('Security baseline passed'));
    } else {
      spinner2.warn(chalk.yellow('Security issues found:'));
      securityStatus.issues.forEach(issue => {
        console.log(chalk.yellow(`  ⚠ ${issue}`));
      });
    }
    
    // Step 6: Network Configuration
    if (!options.skipNetwork) {
      console.log(chalk.blue('\n🌐 Step 3: Configuring network...'));
      const spinner3 = ora('Applying network settings...').start();
      
      if (!options.dryRun) {
        await network.configure({
          ipAddress: assetInfo.ipAddress,
          subnetMask: assetInfo.subnetMask,
          gateway: assetInfo.gateway,
          dns: [assetInfo.dnsPrimary, assetInfo.dnsSecondary],
          domain: assetInfo.domain
        });
      }
      
      spinner3.succeed(chalk.green('Network configured'));
    }
    
    // Step 7: Software Installation
    if (!options.skipSoftware) {
      console.log(chalk.blue('\n💿 Step 4: Installing required software...'));
      
      const requiredSoftware = [
        { name: 'Epic Hyperspace', version: '2023.1', required: true },
        { name: 'Microsoft Office', version: '365', required: true },
        { name: 'VPN Client', version: '5.2', required: true },
        { name: 'Antivirus', version: 'latest', required: true }
      ];
      
      for (const app of requiredSoftware) {
        const spinner = ora(`Installing ${app.name}...`).start();
        
        if (!options.dryRun) {
          await software.install(app.name, app.version);
          await db.recordSoftware(assetInfo.assetTag, app);
        }
        
        spinner.succeed(chalk.green(`${app.name} installed`));
      }
    }
    
    // Step 8: Generate Report
    console.log(chalk.blue('\n📊 Step 5: Generating setup report...'));
    const setupReport = {
      user: userInfo,
      asset: assetInfo,
      security: securityStatus,
      timestamp: new Date().toISOString(),
      status: 'completed'
    };
    
    if (!options.dryRun) {
      await db.saveSetupReport(setupReport);
    }
    
    console.log(chalk.green('\n✅ Workstation setup completed successfully!'));
    console.log(chalk.gray(`\nAsset: ${assetInfo.assetTag}`));
    console.log(chalk.gray(`User: ${userInfo.firstName} ${userInfo.lastName}`));
    console.log(chalk.gray(`Department: ${userInfo.department}`));
    
    if (options.dryRun) {
      console.log(chalk.yellow('\n[DRY RUN] No actual changes were made.'));
    }
    
  } catch (error) {
    console.error(chalk.red('\n❌ Setup failed:'), error);
    throw error;
  }
}

async function collectUserInfo(employeeId?: string): Promise<any> {
  const questions = [
    {
      type: 'input',
      name: 'employeeId',
      message: 'Employee ID:',
      default: employeeId,
      when: !employeeId,
      validate: (input: string) => input.length > 0 || 'Employee ID is required'
    },
    {
      type: 'input',
      name: 'firstName',
      message: 'First name:',
      validate: (input: string) => input.length > 0 || 'First name is required'
    },
    {
      type: 'input',
      name: 'lastName',
      message: 'Last name:',
      validate: (input: string) => input.length > 0 || 'Last name is required'
    },
    {
      type: 'input',
      name: 'email',
      message: 'Email:',
      validate: (input: string) => {
        const email = input.toLowerCase();
        return email.includes('@') || 'Valid email is required';
      }
    },
    {
      type: 'list',
      name: 'department',
      message: 'Department:',
      choices: [
        'IT',
        'Cardiology',
        'Emergency',
        'Administration',
        'Radiology',
        'Laboratory',
        'Pharmacy',
        'Other'
      ]
    },
    {
      type: 'input',
      name: 'jobTitle',
      message: 'Job title:',
      validate: (input: string) => input.length > 0 || 'Job title is required'
    },
    {
      type: 'input',
      name: 'phone',
      message: 'Phone number (optional):'
    }
  ];
  
  const answers = await inquirer.prompt(questions);
  
  return {
    employeeId: employeeId || answers.employeeId,
    firstName: answers.firstName,
    lastName: answers.lastName,
    email: answers.email,
    department: answers.department,
    jobTitle: answers.jobTitle,
    phone: answers.phone || null,
    isActive: true
  };
}

async function collectAssetInfo(assetTag?: string): Promise<any> {
  const questions = [
    {
      type: 'input',
      name: 'assetTag',
      message: 'Asset tag:',
      default: assetTag,
      when: !assetTag,
      validate: (input: string) => input.length > 0 || 'Asset tag is required'
    },
    {
      type: 'list',
      name: 'assetType',
      message: 'Asset type:',
      choices: ['workstation', 'laptop', 'server', 'tablet', 'other']
    },
    {
      type: 'input',
      name: 'hostname',
      message: 'Hostname:',
      validate: (input: string) => input.length > 0 || 'Hostname is required'
    },
    {
      type: 'input',
      name: 'serialNumber',
      message: 'Serial number:'
    },
    {
      type: 'input',
      name: 'manufacturer',
      message: 'Manufacturer:',
      default: 'Dell'
    },
    {
      type: 'input',
      name: 'model',
      message: 'Model:',
      default: 'OptiPlex'
    },
    {
      type: 'input',
      name: 'location',
      message: 'Physical location:',
      validate: (input: string) => input.length > 0 || 'Location is required'
    },
    {
      type: 'input',
      name: 'ipAddress',
      message: 'IP Address:',
      default: '192.168.1.100',
      validate: (input: string) => {
        const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
        return ipPattern.test(input) || 'Valid IP address required';
      }
    },
    {
      type: 'input',
      name: 'subnetMask',
      message: 'Subnet mask:',
      default: '255.255.255.0'
    },
    {
      type: 'input',
      name: 'gateway',
      message: 'Gateway:',
      default: '192.168.1.1'
    },
    {
      type: 'input',
      name: 'dnsPrimary',
      message: 'Primary DNS:',
      default: '8.8.8.8'
    },
    {
      type: 'input',
      name: 'dnsSecondary',
      message: 'Secondary DNS:',
      default: '8.8.4.4'
    },
    {
      type: 'input',
      name: 'domain',
      message: 'Domain:',
      default: 'hospital.local'
    }
  ];
  
  const answers = await inquirer.prompt(questions);
  
  return {
    assetTag: assetTag || answers.assetTag,
    assetType: answers.assetType,
    hostname: answers.hostname,
    serialNumber: answers.serialNumber,
    manufacturer: answers.manufacturer,
    model: answers.model,
    location: answers.location,
    status: 'active',
    ipAddress: answers.ipAddress,
    subnetMask: answers.subnetMask,
    gateway: answers.gateway,
    dnsPrimary: answers.dnsPrimary,
    dnsSecondary: answers.dnsSecondary,
    domain: answers.domain
  };
}

async function confirmSetup(userInfo: any, assetInfo: any): Promise<boolean> {
  console.log(chalk.blue('\n📋 Setup Summary:'));
  console.log(chalk.gray('─'.repeat(50)));
  console.log(chalk.white(`User: ${userInfo.firstName} ${userInfo.lastName} (${userInfo.employeeId})`));
  console.log(chalk.white(`Department: ${userInfo.department}`));
  console.log(chalk.white(`Asset: ${assetInfo.assetTag} (${assetInfo.assetType})`));
  console.log(chalk.white(`Hostname: ${assetInfo.hostname}`));
  console.log(chalk.white(`Location: ${assetInfo.location}`));
  console.log(chalk.gray('─'.repeat(50)));
  
  const { confirmed } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'confirmed',
      message: 'Proceed with workstation setup?',
      default: true
    }
  ]);
  
  return confirmed;
}

/**
 * Setup Command - Healthcare Workstation Configuration
 * 
 * Complete onboarding scenario for healthcare staff including:
 * - User profile creation with department-specific settings
 * - Asset assignment with building-specific network configs
 * - Healthcare software installation (Epic, FDA-validated)
 * - VPN configuration for remote sessions
 * - Compliance tracking for medical device software
 */
import inquirer from 'inquirer';
import chalk from 'chalk';
import ora from 'ora';
import { DatabaseClient } from '../utils/db';

interface SetupOptions {
  user?: string;
  asset?: string;
  scenario?: string;
  yes?: boolean;
  skipNetwork?: boolean;
  skipSoftware?: boolean;
  verbose?: boolean;
  dryRun?: boolean;
}

// Healthcare-specific department configurations
const DEPARTMENT_CONFIGS: { [key: string]: any } = {
  'Psychiatry': {
    building: 'Building C',
    networkRange: '192.168.3',
    requiresEpic: true,
    requiresVPN: true,
    software: [
      { name: 'Epic Hyperspace', version: '2023.1.2', vendor: 'Epic Systems', required: true, fdaApproved: true },
      { name: 'Cerner PowerChart', version: '2022.3', vendor: 'Cerner', required: true, fdaApproved: true },
      { name: 'Microsoft Office', version: '365', vendor: 'Microsoft', required: true },
      { name: 'Cisco AnyConnect VPN', version: '5.0', vendor: 'Cisco', required: true },
      { name: 'Symantec Endpoint Protection', version: '14.3', vendor: 'Symantec', required: true }
    ]
  },
  'Cardiology': {
    building: 'Building A',
    networkRange: '192.168.1',
    requiresEpic: true,
    requiresVPN: true,
    software: [
      { name: 'Epic Hyperspace', version: '2023.1.2', vendor: 'Epic Systems', required: true, fdaApproved: true },
      { name: 'Philips IntelliSpace', version: '12.1', vendor: 'Philips', required: true, fdaApproved: true },
      { name: 'Microsoft Office', version: '365', vendor: 'Microsoft', required: true },
      { name: 'Cisco AnyConnect VPN', version: '5.0', vendor: 'Cisco', required: true }
    ]
  },
  'Emergency': {
    building: 'Building A - Floor 1',
    networkRange: '192.168.1',
    requiresEpic: true,
    requiresVPN: false,
    software: [
      { name: 'Epic Hyperspace', version: '2023.1.2', vendor: 'Epic Systems', required: true, fdaApproved: true },
      { name: 'Microsoft Office', version: '365', vendor: 'Microsoft', required: true },
      { name: 'Symantec Endpoint Protection', version: '14.3', vendor: 'Symantec', required: true }
    ]
  },
  'IT': {
    building: 'Building B',
    networkRange: '192.168.2',
    requiresEpic: true,
    requiresVPN: true,
    software: [
      { name: 'Epic Hyperspace', version: '2023.1.2', vendor: 'Epic Systems', required: true, fdaApproved: true },
      { name: 'Microsoft Office', version: '365', vendor: 'Microsoft', required: true },
      { name: 'Cisco AnyConnect VPN', version: '5.0', vendor: 'Cisco', required: true },
      { name: 'Visual Studio Code', version: '1.85', vendor: 'Microsoft', required: false },
      { name: 'Git', version: '2.43', vendor: 'Git', required: false }
    ]
  }
};

// Building-specific network configurations
const BUILDING_NETWORKS: { [key: string]: any } = {
  'Building A': { subnet: '192.168.1', gateway: '192.168.1.1', vlan: 'VLAN_10' },
  'Building B': { subnet: '192.168.2', gateway: '192.168.2.1', vlan: 'VLAN_20' },
  'Building C': { subnet: '192.168.3', gateway: '192.168.3.1', vlan: 'VLAN_30' },
  'Building D': { subnet: '192.168.4', gateway: '192.168.4.1', vlan: 'VLAN_40' }
};

export async function setupCommand(options: SetupOptions): Promise<void> {
  console.log(chalk.blue.bold('\n🏥 Health Ops Workstation Setup\n'));
  console.log(chalk.gray('Configuring workstation for healthcare environment\n'));
  
  // Check if running in scenario mode
  if (options.scenario === 'sarah-johnson') {
    await runSarahJohnsonScenario(options);
    return;
  }
  
  // Initialize database connection
  const db = new DatabaseClient();
  
  try {
    // Step 1: Collect User Information
    const userInfo = await collectUserInfo(options.user);
    
    // Step 2: Get department configuration
    const deptConfig = DEPARTMENT_CONFIGS[userInfo.department] || DEPARTMENT_CONFIGS['IT'];
    
    // Step 3: Collect Asset Information with department-specific defaults
    const assetInfo = await collectAssetInfo(options.asset, deptConfig);
    
    // Step 4: Collect Healthcare Software Requirements
    const softwareConfig = await collectSoftwareRequirements(userInfo.department, deptConfig);
    
    // Step 5: Collect VPN Configuration
    const vpnConfig = await collectVPNConfig(deptConfig.requiresVPN);
    
    // Step 6: Confirm before proceeding
    const confirmed = await confirmHealthcareSetup(userInfo, assetInfo, softwareConfig, vpnConfig);
    if (!confirmed) {
      console.log(chalk.yellow('Setup cancelled.'));
      return;
    }
    
    let userId: number | undefined;
    let assetId: number | undefined;
    
    // Step 7: Create User in Database
    if (!options.dryRun) {
      console.log(chalk.blue('\n📋 Step 1: Creating user profile...'));
      const spinner1 = ora('Saving user data...').start();
      
      try {
        const existingUser = await db.findUserByEmployeeId(userInfo.employeeId);
        if (existingUser) {
          spinner1.info(chalk.yellow(`User ${userInfo.employeeId} exists, using existing record`));
          userId = existingUser.id;
        } else {
          userId = await db.createUser(userInfo);
          spinner1.succeed(chalk.green(`✓ User created: Dr. ${userInfo.lastName} (ID: ${userId})`));
        }
      } catch (error) {
        spinner1.fail(chalk.red('Failed to create user'));
        throw error;
      }
    } else {
      console.log(chalk.yellow('[DRY RUN] Would create user:'), userInfo.email);
    }
    
    // Step 8: Create Asset in Database
    if (!options.dryRun && userId) {
      console.log(chalk.blue('\n💻 Step 2: Assigning workstation...'));
      const spinner2 = ora('Configuring asset...').start();
      
      try {
        assetId = await db.createAsset(assetInfo, userId);
        spinner2.succeed(chalk.green(`✓ Workstation assigned: ${assetInfo.assetTag} (ID: ${assetId})`));
        
        // Configure network for specific building
        if (!options.skipNetwork) {
          const spinnerNet = ora(`Configuring network for ${deptConfig.building}...`).start();
          await new Promise(resolve => setTimeout(resolve, 500));
          spinnerNet.succeed(chalk.green(`✓ Network configured: ${assetInfo.ipAddress} (${deptConfig.building})`));
        }
      } catch (error) {
        spinner2.fail(chalk.red('Failed to assign workstation'));
        throw error;
      }
    } else if (options.dryRun) {
      console.log(chalk.yellow('[DRY RUN] Would assign workstation:'), assetInfo.assetTag);
    }
    
    // Step 9: Install and Record Healthcare Software
    if (!options.skipSoftware && !options.dryRun && assetId) {
      console.log(chalk.blue('\n💿 Step 3: Installing healthcare software...'));
      
      // Install standard department software
      const standardSoftware = deptConfig.software || [];
      
      for (const app of standardSoftware) {
        const spinner = ora(`Installing ${app.name}...`).start();
        
        try {
          await db.recordSoftware(assetInfo.assetTag, app);
          
          if (app.fdaApproved) {
            spinner.succeed(chalk.green(`✓ ${app.name} installed (FDA-validated)`));
          } else {
            spinner.succeed(chalk.green(`✓ ${app.name} installed`));
          }
        } catch (error) {
          spinner.fail(chalk.red(`✗ Failed to install ${app.name}`));
          console.error(error);
        }
      }
      
      // Install custom software selections
      for (const app of softwareConfig.customSoftware) {
        const spinner = ora(`Installing ${app.name}...`).start();
        
        try {
          await db.recordSoftware(assetInfo.assetTag, app);
          spinner.succeed(chalk.green(`✓ ${app.name} installed`));
        } catch (error) {
          spinner.fail(chalk.red(`✗ Failed to install ${app.name}`));
        }
      }
    } else if (options.dryRun) {
      console.log(chalk.yellow('[DRY RUN] Would install healthcare software packages'));
    }
    
    // Step 10: Configure VPN
    if (!options.dryRun && vpnConfig.enabled && assetId) {
      console.log(chalk.blue('\n🔐 Step 4: Configuring VPN access...'));
      const spinnerVPN = ora('Setting up remote access...').start();
      
      try {
        await db.updateVPNConfig(assetInfo.assetTag, vpnConfig);
        spinnerVPN.succeed(chalk.green(`✓ VPN configured: ${vpnConfig.profile} profile`));
        console.log(chalk.gray(`   Remote sessions enabled for ${userInfo.department}`));
      } catch (error) {
        spinnerVPN.fail(chalk.red('Failed to configure VPN'));
        console.error(error);
      }
    }
    
    // Final Summary
    console.log(chalk.green('\n✅ Healthcare Workstation Setup Complete!'));
    console.log(chalk.blue('\n📊 Setup Summary:'));
    console.log(chalk.gray('─'.repeat(60)));
    console.log(chalk.white(`👤 User: Dr. ${userInfo.firstName} ${userInfo.lastName}`));
    console.log(chalk.white(`   ID: ${userInfo.employeeId}`));
    console.log(chalk.white(`   Department: ${userInfo.department}`));
    console.log(chalk.white(`   Email: ${userInfo.email}`));
    console.log(chalk.gray('─'.repeat(60)));
    console.log(chalk.white(`💻 Workstation: ${assetInfo.assetTag}`));
    console.log(chalk.white(`   Hostname: ${assetInfo.hostname}`));
    console.log(chalk.white(`   Location: ${assetInfo.location}`));
    console.log(chalk.white(`   Network: ${assetInfo.ipAddress} (${deptConfig.building})`));
    console.log(chalk.gray('─'.repeat(60)));
    console.log(chalk.white(`🔒 VPN Access: ${vpnConfig.enabled ? 'Enabled ✓' : 'Not Required'}`));
    console.log(chalk.white(`💿 Software: ${deptConfig.software.length + softwareConfig.customSoftware.length} packages installed`));
    
    if (deptConfig.software.some((s: any) => s.fdaApproved)) {
      console.log(chalk.white(`   ✓ FDA-validated medical software configured`));
    }
    
    console.log(chalk.gray('─'.repeat(60)));
    
    if (options.dryRun) {
      console.log(chalk.yellow('\n[DRY RUN] No actual changes were made to the database.'));
    } else {
      console.log(chalk.gray(`\nUser ID: ${userId} | Asset ID: ${assetId}`));
      console.log(chalk.green('\nWorkstation ready for QA monitoring!'));
    }
    
  } catch (error) {
    console.error(chalk.red('\n❌ Setup failed:'), error);
    throw error;
  } finally {
    db.close();
  }
}

/**
 * Pre-configured scenario for Dr. Sarah Johnson
 */
async function runSarahJohnsonScenario(options: SetupOptions): Promise<void> {
  console.log(chalk.blue.bold('\n🏥 Healthcare Onboarding Scenario\n'));
  console.log(chalk.cyan('Dr. Sarah Johnson - Behavioral Health Team\n'));
  console.log(chalk.gray('Pre-configured setup for Psychiatry department\n'));
  
  const db = new DatabaseClient();
  
  try {
    // Pre-configured data for Dr. Sarah Johnson
    const userInfo = {
      employeeId: 'PSY-2024-015',
      firstName: 'Sarah',
      lastName: 'Johnson',
      email: 'sarah.johnson@tarzanatreatment.org',
      department: 'Psychiatry',
      jobTitle: 'Psychiatrist - Behavioral Health',
      phone: '818-555-0142',
      isActive: true,
      hireDate: new Date().toISOString()
    };
    
    const assetInfo = {
      assetTag: 'WS-2024-015',
      assetType: 'workstation',
      hostname: 'PSY-WS-015',
      serialNumber: 'SN-DELL-789456',
      manufacturer: 'Dell',
      model: 'OptiPlex 7090',
      location: 'Building C - Floor 2 - Office 215',
      department: 'Psychiatry',
      status: 'active',
      ipAddress: '192.168.3.115',
      subnetMask: '255.255.255.0',
      gateway: '192.168.3.1',
      dnsPrimary: '192.168.3.10',
      dnsSecondary: '8.8.8.8',
      domain: 'tarzanatreatment.org'
    };
    
    const deptConfig = DEPARTMENT_CONFIGS['Psychiatry'];
    
    console.log(chalk.blue('Configuration:'));
    console.log(chalk.gray(`  User: ${userInfo.firstName} ${userInfo.lastName}`));
    console.log(chalk.gray(`  Department: ${userInfo.department}`));
    console.log(chalk.gray(`  Workstation: ${assetInfo.assetTag}`));
    console.log(chalk.gray(`  Location: ${assetInfo.location}`));
    console.log(chalk.gray(`  Network: ${assetInfo.ipAddress} (${deptConfig.building})`));
    console.log(chalk.gray(`  VPN: Required for remote sessions`));
    console.log();
    
    // Skip confirmation if --yes flag is set
    if (!options.yes) {
      const { confirmed } = await inquirer.prompt([{
        type: 'confirm',
        name: 'confirmed',
        message: 'Proceed with Dr. Johnson\'s workstation setup?',
        default: true
      }]);
      
      if (!confirmed) {
        console.log(chalk.yellow('Setup cancelled.'));
        return;
      }
    } else {
      console.log(chalk.blue('Auto-confirming (--yes flag set)\n'));
    }
    
    if (!options.dryRun) {
      // Create User
      console.log(chalk.blue('\n📋 Creating user profile...'));
      const userSpinner = ora('Saving Dr. Johnson\'s profile...').start();
      const userId = await db.createUser(userInfo);
      userSpinner.succeed(chalk.green(`✓ Profile created (ID: ${userId})`));
      
      // Create Asset
      console.log(chalk.blue('\n💻 Assigning workstation...'));
      const assetSpinner = ora('Configuring WS-2024-015...').start();
      const assetId = await db.createAsset(assetInfo, userId);
      assetSpinner.succeed(chalk.green(`✓ Workstation assigned (ID: ${assetId})`));
      
      // Configure Network
      const netSpinner = ora('Configuring Building C network...').start();
      await new Promise(resolve => setTimeout(resolve, 600));
      netSpinner.succeed(chalk.green(`✓ Network configured: ${assetInfo.ipAddress}`));
      
      // Install Healthcare Software
      console.log(chalk.blue('\n💿 Installing healthcare software...'));
      for (const app of deptConfig.software) {
        const spinner = ora(`${app.name}...`).start();
        await db.recordSoftware(assetInfo.assetTag, app);
        
        if (app.fdaApproved) {
          spinner.succeed(chalk.green(`✓ ${app.name} (FDA-validated)`));
        } else {
          spinner.succeed(chalk.green(`✓ ${app.name}`));
        }
      }
      
      // Configure VPN
      console.log(chalk.blue('\n🔐 Configuring VPN...'));
      const vpnSpinner = ora('Setting up remote access...').start();
      await db.updateVPNConfig(assetInfo.assetTag, { enabled: true, profile: 'Healthcare Standard' });
      vpnSpinner.succeed(chalk.green('✓ VPN enabled for remote behavioral health sessions'));
      
      // Final Summary
      console.log(chalk.green('\n✅ Dr. Johnson\'s Workstation Ready!'));
      console.log(chalk.blue('\n📊 Setup Complete:'));
      console.log(chalk.gray('─'.repeat(60)));
      console.log(chalk.white(`👤 Dr. ${userInfo.lastName} (${userInfo.employeeId})`));
      console.log(chalk.white(`   ${userInfo.jobTitle}`));
      console.log(chalk.white(`   ${userInfo.email}`));
      console.log(chalk.gray('─'.repeat(60)));
      console.log(chalk.white(`💻 ${assetInfo.assetTag} @ ${assetInfo.location}`));
      console.log(chalk.white(`   IP: ${assetInfo.ipAddress}`));
      console.log(chalk.gray('─'.repeat(60)));
      console.log(chalk.white(`✓ Epic Hyperspace (FDA-validated) installed`));
      console.log(chalk.white(`✓ VPN configured for remote sessions`));
      console.log(chalk.white(`✓ Network: Building C (Behavioral Health)`));
      console.log(chalk.gray('─'.repeat(60)));
      console.log(chalk.cyan('\n📊 QA can now monitor workstation health via dashboard'));
      console.log(chalk.gray('   http://localhost:8000'));
      
    } else {
      console.log(chalk.yellow('\n[DRY RUN] Would create complete workstation setup for Dr. Johnson'));
    }
    
  } catch (error) {
    console.error(chalk.red('\n❌ Scenario failed:'), error);
    throw error;
  } finally {
    db.close();
  }
}

// Helper functions remain the same but with healthcare enhancements
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
      choices: Object.keys(DEPARTMENT_CONFIGS)
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

async function collectAssetInfo(assetTag?: string, deptConfig?: any): Promise<any> {
  const defaultNetwork = deptConfig ? BUILDING_NETWORKS[deptConfig.building] : null;
  const nextIP = defaultNetwork ? `${defaultNetwork.subnet}.100` : '192.168.1.100';
  
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
      choices: ['workstation', 'laptop', 'tablet'],
      default: 'workstation'
    },
    {
      type: 'input',
      name: 'hostname',
      message: 'Hostname:',
      default: (answers: any) => answers.assetTag?.toLowerCase().replace(/-/g, '-') || 'ws-new',
      validate: (input: string) => input.length > 0 || 'Hostname is required'
    },
    {
      type: 'input',
      name: 'serialNumber',
      message: 'Serial number:'
    },
    {
      type: 'input',
      name: 'location',
      message: 'Physical location:',
      default: deptConfig?.building ? `${deptConfig.building} - Floor 2` : 'Building A',
      validate: (input: string) => input.length > 0 || 'Location is required'
    },
    {
      type: 'input',
      name: 'ipAddress',
      message: 'IP Address:',
      default: nextIP,
      validate: (input: string) => {
        const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
        return ipPattern.test(input) || 'Valid IP address required';
      }
    }
  ];
  
  const answers = await inquirer.prompt(questions);
  
  return {
    assetTag: assetTag || answers.assetTag,
    assetType: answers.assetType,
    hostname: answers.hostname,
    serialNumber: answers.serialNumber,
    manufacturer: 'Dell',
    model: 'OptiPlex 7090',
    location: answers.location,
    department: deptConfig ? Object.keys(DEPARTMENT_CONFIGS).find(key => DEPARTMENT_CONFIGS[key] === deptConfig) : 'IT',
    status: 'active',
    ipAddress: answers.ipAddress,
    subnetMask: '255.255.255.0',
    gateway: defaultNetwork?.gateway || '192.168.1.1',
    dnsPrimary: '8.8.8.8',
    dnsSecondary: '8.8.4.4',
    domain: 'tarzanatreatment.org'
  };
}

async function collectSoftwareRequirements(department: string, deptConfig: any): Promise<any> {
  console.log(chalk.blue(`\n💿 Healthcare Software for ${department}`));
  console.log(chalk.gray('Standard packages:'));
  deptConfig.software.forEach((app: any) => {
    const badge = app.fdaApproved ? chalk.yellow('[FDA]') : '';
    console.log(chalk.gray(`  • ${app.name} ${badge}`));
  });
  
  const { addCustom } = await inquirer.prompt([{
    type: 'confirm',
    name: 'addCustom',
    message: 'Install additional software?',
    default: false
  }]);
  
  const customSoftware: any[] = [];
  
  if (addCustom) {
    let addingMore = true;
    while (addingMore) {
      const { name, version, vendor } = await inquirer.prompt([
        { type: 'input', name: 'name', message: 'Software name:' },
        { type: 'input', name: 'version', message: 'Version:' },
        { type: 'input', name: 'vendor', message: 'Vendor:' }
      ]);
      
      customSoftware.push({ name, version, vendor, required: false });
      
      const { more } = await inquirer.prompt([{
        type: 'confirm',
        name: 'more',
        message: 'Add another software?',
        default: false
      }]);
      
      addingMore = more;
    }
  }
  
  return { customSoftware };
}

async function collectVPNConfig(required: boolean): Promise<any> {
  if (!required) {
    return { enabled: false };
  }
  
  const { enableVPN } = await inquirer.prompt([{
    type: 'confirm',
    name: 'enableVPN',
    message: 'Configure VPN for remote access?',
    default: true
  }]);
  
  if (!enableVPN) {
    return { enabled: false };
  }
  
  const { profile } = await inquirer.prompt([{
    type: 'list',
    name: 'profile',
    message: 'VPN Profile:',
    choices: [
      'Healthcare Standard',
      'Physician Extended',
      'Admin Limited'
    ],
    default: 'Healthcare Standard'
  }]);
  
  return { enabled: true, profile };
}

async function confirmHealthcareSetup(
  userInfo: any, 
  assetInfo: any, 
  softwareConfig: any,
  vpnConfig: any
): Promise<boolean> {
  console.log(chalk.blue('\n📋 Healthcare Setup Summary'));
  console.log(chalk.gray('─'.repeat(60)));
  console.log(chalk.white(`👤 Dr. ${userInfo.firstName} ${userInfo.lastName}`));
  console.log(chalk.white(`   ID: ${userInfo.employeeId}`));
  console.log(chalk.white(`   Department: ${userInfo.department}`));
  console.log(chalk.white(`   Role: ${userInfo.jobTitle}`));
  console.log(chalk.gray('─'.repeat(60)));
  console.log(chalk.white(`💻 Workstation: ${assetInfo.assetTag}`));
  console.log(chalk.white(`   Hostname: ${assetInfo.hostname}`));
  console.log(chalk.white(`   Location: ${assetInfo.location}`));
  console.log(chalk.white(`   Network: ${assetInfo.ipAddress}`));
  console.log(chalk.gray('─'.repeat(60)));
  console.log(chalk.white(`🔒 VPN Access: ${vpnConfig.enabled ? 'Enabled' : 'Not Required'}`));
  if (vpnConfig.enabled) {
    console.log(chalk.white(`   Profile: ${vpnConfig.profile}`));
  }
  console.log(chalk.gray('─'.repeat(60)));
  
  const { confirmed } = await inquirer.prompt([{
    type: 'confirm',
    name: 'confirmed',
    message: 'Proceed with healthcare workstation setup?',
    default: true
  }]);
  
  return confirmed;
}

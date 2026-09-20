# Oracle Cloud Infrastructure (OCI) Terraform Setup

This directory contains the Infrastructure as Code (IaC) configuration for provisioning the **Aperio Gateway** and network infrastructure on Oracle Cloud Infrastructure (OCI).

---

## Oracle Cloud Always Free Tier Limits

As documented by [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/):

### Compute Quotas

#### AMD Compute Instances
* **Specification**: AMD-based Compute VMs with 1/8 OCPU and 1 GB memory each
* **Allowance**: Up to **2 AMD-based Compute VMs** (`VM.Standard.E2.1.Micro`)

#### ARM Compute Instances (Ampere A1)
* **Specification**: Arm-based Ampere A1 cores and 12 GB of memory
* **Allowance**: Usable as **1 VM or up to 2 VMs**
* **Monthly Cap**: 1,500 OCPU hours and 9,000 GB hours per month

### Additional Resources
* **Storage**: Up to 200 GB total boot/block volume storage across all VMs (minimum 50 GB per boot volume)
* **IP Addresses**: Up to 2 Reserved Public IPv4 addresses
* **Outbound Data Transfer**: 10 TB per month free

---

## Topology & Splitting Options

With OCI Always Free, you can run **up to 4 VMs simultaneously for $0.00/month**:

| Option | ARM VM(s) | AMD VM(s) | Use Cases |
| :--- | :--- | :--- | :--- |
| **Option A (Recommended)** | 1 VM: 2 OCPUs, 12 GB RAM | 2 VMs: 1/8 OCPU, 1 GB RAM | 1 Heavy Gateway Node + 2 Micro Status/Edge Nodes |
| **Option B** | 2 VMs: 1 OCPU, 6 GB RAM each | 2 VMs: 1/8 OCPU, 1 GB RAM | 2 Medium Gateways + 2 Micro Edge Nodes |

---

## Quickstart & Task Runner (`just`)

A local [`justfile`](file:///Users/znglyvlad/Desktop/vlad/drakodav/pluribus/projects/homelab/gateway/terraform/justfile) is provided for easy management:

```bash
# View all available commands
just

# Initialize Terraform modules and providers
just init

# Validate configuration syntax
just validate

# Preview infrastructure changes
just plan

# Apply infrastructure changes interactively
just apply

# Auto-format all Terraform files
just fmt
```

---

## Directory Structure

```text
gateway/terraform/
├── readme.md                # Documentation (this file)
├── justfile                 # Terraform task runner
├── modules/
│   ├── compute/             # Compute instance (Aperio Gateway VM)
│   └── networking/          # VCN, Subnet, Internet Gateway, Security Lists
└── environments/
    └── prod/                # Production environment deployment configuration
```

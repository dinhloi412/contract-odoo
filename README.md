# Contract Management Module

## Overview
This module provides comprehensive contract management functionality for hospital equipment sales, including:
- Sales contracts with hospitals and departments
- Contract appendices for modifications and extensions
- Enhanced quotation management

## Features

### 1. Contract Management (Hợp đồng)
- Create and manage sales contracts with hospitals
- Track contract lifecycle: Draft → Active → Expired/Cancelled
- Link multiple sale orders to a single contract
- Automatic product line import from sale orders
- Document management with file attachments and links
- Track delivery, acceptance, and liquidation dates
- Warranty and invoice tracking
- Customer interaction history

### 2. Contract Appendices (Phụ lục)
- Create appendices for contract modifications
- Types: Add goods, Adjust terms/price, Extend time, Other
- Link to original contract with automatic numbering
- Track value changes and impact on contract total
- Product line management with change actions (Add/Adjust/Remove)
- State management: Draft → Active → Cancelled

### 3. Enhanced Quotations (Báo giá)
- Extended sale.order with additional fields
- Department and contact person tracking
- Submission method and tracking
- Customer feedback management
- One-click contract creation from approved quotations
- Link quotations to CRM opportunities

## Installation

1. Copy the `contract_mgmt` folder to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "Contract Management" module

## Dependencies
- base
- sale
- product
- crm

## Usage

### Creating a Contract
1. Navigate to Hợp đồng → Quản lý hợp đồng → Hợp đồng
2. Click "Create"
3. Fill in contract details:
   - Contract name and dates
   - Legal entity (seller) information
   - Customer (hospital/department) information
   - Link sale orders
4. Products will be automatically imported from linked sale orders
5. Click "Kích hoạt" to activate the contract

### Creating an Appendix
1. Open a contract
2. Click the "Phụ lục" smart button or navigate to Phụ lục menu
3. Create new appendix
4. Select appendix type and fill in details
5. Add product lines if needed
6. Click "Kích hoạt" to activate

### Creating Contract from Quotation
1. Create a quotation (sale order)
2. Fill in quotation-specific fields in "Thông tin báo giá" tab
3. Confirm the quotation
4. Click "Tạo hợp đồng" button
5. Contract will be created with all quotation data

## Technical Details

### Models
- `contract.contract` - Main contract model
- `contract.line` - Contract product lines
- `contract.appendix` - Contract appendices
- `contract.appendix.line` - Appendix product lines
- `sale.order` (inherited) - Enhanced quotation

### Security
- User access: Read, Write, Create (no delete)
- Manager access: Full access including delete

### Sequences
- Contract: HĐ-YYYY-XXX
- Appendix: PL-[Contract Number]-XXX

## Version
18.0.1.0.0

## License
LGPL-3

## Author
Developed for Odoo 18.0


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation script for contract_mgmt module
This script validates that all related fields reference existing fields
"""

import ast
import os
import sys

# Fields available on res.partner in Odoo 18
VALID_PARTNER_FIELDS = {
    'name', 'phone', 'mobile', 'email', 'function', 'comment', 'website',
    'vat', 'ref', 'street', 'street2', 'city', 'zip', 'state_id', 'country_id',
    'parent_id', 'child_ids', 'is_company', 'company_type', 'title', 'lang',
    'category_id', 'user_id', 'company_id', 'color', 'active', 'employee',
    'type', 'barcode', 'company_name', 'industry_id', 'bank_ids',
    'partner_latitude', 'partner_longitude', 'email_formatted', 'partner_share',
    'commercial_partner_id', 'commercial_company_name', 'parent_name',
    'company_registry', 'vat_label', 'same_vat_partner_id',
}

# Fields available on product.product
VALID_PRODUCT_FIELDS = {
    'name', 'default_code', 'list_price', 'standard_price', 'type',
    'categ_id', 'uom_id', 'uom_po_id', 'description', 'description_sale',
    'description_purchase', 'active', 'barcode', 'weight', 'volume',
}

# Fields available on sale.order
VALID_SALE_ORDER_FIELDS = {
    'name', 'partner_id', 'date_order', 'validity_date', 'state',
    'amount_total', 'amount_untaxed', 'amount_tax', 'order_line',
    'user_id', 'team_id', 'company_id', 'currency_id', 'pricelist_id',
}

# Fields available on sale.order.line
VALID_SALE_ORDER_LINE_FIELDS = {
    'order_id', 'product_id', 'name', 'product_uom_qty', 'product_uom',
    'price_unit', 'price_subtotal', 'price_total', 'tax_id', 'discount',
}

# Fields available on contract.contract (our model)
VALID_CONTRACT_FIELDS = {
    'contract_number', 'name', 'currency_id', 'amount_total', 'state',
    'partner_company_id', 'partner_department_id', 'contract_date',
    'start_date', 'end_date', 'appendix_count',
}

# Fields available on contract.appendix (our model)
VALID_APPENDIX_FIELDS = {
    'appendix_number', 'name', 'currency_id', 'amount_appendix', 'state',
    'contract_id', 'effective_date', 'end_date',
}


def check_related_field(field_name, related_path, model_name):
    """Check if a related field path is valid"""
    parts = related_path.split('.')
    
    if len(parts) < 2:
        print(f"⚠️  Warning: Related field '{field_name}' in {model_name} has invalid path: {related_path}")
        return False
    
    field_ref = parts[0]
    target_field = parts[-1]
    
    # Determine which field set to check based on the reference field
    if 'partner' in field_ref or field_ref in ['investor_id', 'contact_person_id']:
        valid_fields = VALID_PARTNER_FIELDS
        target_model = 'res.partner'
    elif 'product' in field_ref:
        valid_fields = VALID_PRODUCT_FIELDS
        target_model = 'product.product'
    elif 'sale_order_line' in field_ref:
        valid_fields = VALID_SALE_ORDER_LINE_FIELDS
        target_model = 'sale.order.line'
    elif 'sale_order' in field_ref or field_ref == 'order_id':
        valid_fields = VALID_SALE_ORDER_FIELDS
        target_model = 'sale.order'
    elif 'contract' in field_ref:
        valid_fields = VALID_CONTRACT_FIELDS
        target_model = 'contract.contract'
    elif 'appendix' in field_ref:
        valid_fields = VALID_APPENDIX_FIELDS
        target_model = 'contract.appendix'
    else:
        print(f"⚠️  Warning: Unknown reference field '{field_ref}' in {model_name}.{field_name}")
        return True  # Skip validation for unknown models
    
    if target_field not in valid_fields:
        print(f"❌ ERROR: Related field '{field_name}' in {model_name} references non-existent field '{target_field}' on {target_model}")
        print(f"   Path: {related_path}")
        return False
    
    print(f"✅ OK: {model_name}.{field_name} -> {related_path}")
    return True


def validate_python_file(filepath, model_name):
    """Validate related fields in a Python model file"""
    print(f"\n📄 Validating {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple regex-based check for related fields
    import re
    pattern = r"(\w+)\s*=\s*fields\.\w+\([^)]*related\s*=\s*['\"]([^'\"]+)['\"]"
    matches = re.findall(pattern, content)
    
    if not matches:
        print(f"   No related fields found")
        return True
    
    all_valid = True
    for field_name, related_path in matches:
        if not check_related_field(field_name, related_path, model_name):
            all_valid = False
    
    return all_valid


def main():
    """Main validation function"""
    print("=" * 70)
    print("CONTRACT MANAGEMENT MODULE - RELATED FIELDS VALIDATION")
    print("=" * 70)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    models_path = os.path.join(base_path, 'models')
    
    files_to_check = [
        ('contract.py', 'contract.contract'),
        ('contract_line.py', 'contract.line'),
        ('contract_appendix.py', 'contract.appendix'),
        ('contract_appendix_line.py', 'contract.appendix.line'),
        ('quotation.py', 'sale.order'),
    ]
    
    all_valid = True
    for filename, model_name in files_to_check:
        filepath = os.path.join(models_path, filename)
        if os.path.exists(filepath):
            if not validate_python_file(filepath, model_name):
                all_valid = False
        else:
            print(f"⚠️  Warning: File not found: {filepath}")
    
    print("\n" + "=" * 70)
    if all_valid:
        print("✅ VALIDATION PASSED: All related fields are valid!")
        print("=" * 70)
        return 0
    else:
        print("❌ VALIDATION FAILED: Some related fields reference non-existent fields")
        print("=" * 70)
        return 1


if __name__ == '__main__':
    sys.exit(main())


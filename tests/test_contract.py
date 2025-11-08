# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class TestContract(TransactionCase):
    
    def setUp(self):
        super(TestContract, self).setUp()
        
        # Create test hospital (company)
        self.hospital = self.env['res.partner'].create({
            'name': 'Test Hospital',
            'is_company': True,
            'phone': '0123456789',
            'email': 'hospital@test.com',
        })
        
        # Create test department
        self.department = self.env['res.partner'].create({
            'name': 'Cardiology Department',
            'parent_id': self.hospital.id,
            'type': 'contact',
            'phone': '0987654321',
            'email': 'cardio@test.com',
        })
        
        # Create test contact person
        self.contact = self.env['res.partner'].create({
            'name': 'Dr. John Doe',
            'parent_id': self.hospital.id,
            'type': 'contact',
            'function': 'Head of Department',
            'phone': '0111222333',
            'email': 'john.doe@test.com',
        })
        
        # Create test product
        self.product = self.env['product.product'].create({
            'name': 'Medical Equipment X',
            'default_code': 'MED-001',
            'list_price': 10000.0,
        })
    
    def test_contract_creation(self):
        """Test basic contract creation"""
        contract = self.env['contract.contract'].create({
            'name': 'Test Contract',
            'partner_company_id': self.hospital.id,
            'partner_department_id': self.department.id,
            'contract_date': date.today(),
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
        })
        
        self.assertTrue(contract)
        self.assertEqual(contract.partner_company_id, self.hospital)
        self.assertEqual(contract.partner_department_id, self.department)
        # Check computed fields
        self.assertEqual(contract.partner_phone, self.department.phone)
        self.assertEqual(contract.partner_email, self.department.email)
    
    def test_department_representative_compute(self):
        """Test department representative computation"""
        # Create a contact for the department
        dept_contact = self.env['res.partner'].create({
            'name': 'Department Manager',
            'parent_id': self.department.id,
            'type': 'contact',
        })
        
        contract = self.env['contract.contract'].create({
            'name': 'Test Contract',
            'partner_company_id': self.hospital.id,
            'partner_department_id': self.department.id,
            'contract_date': date.today(),
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
        })
        
        # Should find the contact person
        self.assertTrue(contract.department_representative)
    
    def test_contract_line_creation(self):
        """Test contract line creation"""
        contract = self.env['contract.contract'].create({
            'name': 'Test Contract',
            'partner_company_id': self.hospital.id,
            'contract_date': date.today(),
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
        })
        
        line = self.env['contract.line'].create({
            'contract_id': contract.id,
            'product_id': self.product.id,
            'quantity': 5,
            'price_unit': 10000.0,
        })
        
        self.assertEqual(line.price_subtotal, 50000.0)
        self.assertEqual(contract.amount_total, 50000.0)
    
    def test_contract_date_validation(self):
        """Test contract date validation"""
        with self.assertRaises(ValidationError):
            self.env['contract.contract'].create({
                'name': 'Invalid Contract',
                'partner_company_id': self.hospital.id,
                'contract_date': date.today(),
                'start_date': date.today() + timedelta(days=10),
                'end_date': date.today(),  # End before start - should fail
            })
    
    def test_department_company_validation(self):
        """Test department must belong to selected company"""
        other_hospital = self.env['res.partner'].create({
            'name': 'Other Hospital',
            'is_company': True,
        })
        
        with self.assertRaises(ValidationError):
            self.env['contract.contract'].create({
                'name': 'Invalid Contract',
                'partner_company_id': other_hospital.id,
                'partner_department_id': self.department.id,  # Belongs to different hospital
                'contract_date': date.today(),
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=365),
            })
    
    def test_contract_appendix_creation(self):
        """Test contract appendix creation"""
        contract = self.env['contract.contract'].create({
            'name': 'Test Contract',
            'partner_company_id': self.hospital.id,
            'contract_date': date.today(),
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
        })
        
        # Activate contract first
        contract.action_set_active()
        
        appendix = self.env['contract.appendix'].create({
            'name': 'Test Appendix',
            'contract_id': contract.id,
            'appendix_type': 'add_goods',
            'appendix_scope': 'Adding more equipment',
            'effective_date': date.today(),
        })
        
        self.assertTrue(appendix)
        self.assertIn('PL-', appendix.appendix_number)
        self.assertEqual(contract.appendix_count, 1)
    
    def test_investor_representative_related(self):
        """Test investor representative related field"""
        investor = self.env['res.partner'].create({
            'name': 'Government Agency',
            'is_company': True,
            'function': 'Public Investor',
        })
        
        contract = self.env['contract.contract'].create({
            'name': 'Test Contract',
            'partner_company_id': self.hospital.id,
            'investor_id': investor.id,
            'contract_date': date.today(),
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
        })
        
        # Check related fields work correctly
        self.assertEqual(contract.investor_representative, investor.name)
        self.assertEqual(contract.investor_position, investor.function)
    
    def test_contact_person_related_fields(self):
        """Test contact person related fields"""
        contract = self.env['contract.contract'].create({
            'name': 'Test Contract',
            'partner_company_id': self.hospital.id,
            'contact_person_id': self.contact.id,
            'contract_date': date.today(),
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
        })
        
        # Check related fields work correctly
        self.assertEqual(contract.contact_job_title, self.contact.function)
        self.assertEqual(contract.contact_phone, self.contact.phone)
        self.assertEqual(contract.contact_email, self.contact.email)


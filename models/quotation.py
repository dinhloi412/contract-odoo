# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Thông tin chung
    quotation_title = fields.Char(
        string="Tiêu đề báo giá"
    )
    
    # Khách hàng
    department_id = fields.Many2one(
        'res.partner',
        string="Khoa / Phòng",
        domain="[('parent_id', '=', partner_id)]"
    )
    contact_person = fields.Many2one(
        'res.partner',
        string="Người liên hệ",
        domain="[('parent_id', '=', partner_id)]"
    )
    
    # Thông tin báo giá
    quotation_type = fields.Selection(
        [
            ('goods', 'Cung cấp hàng hóa'),
            ('service', 'Dịch vụ'),
            ('framework', 'Hợp đồng khung'),
        ],
        string="Loại báo giá"
    )
    opportunity_id = fields.Many2one(
        'crm.lead',
        string="Cơ hội liên quan"
    )
    source_id = fields.Many2one(
        'utm.source',
        string="Nguồn khách hàng"
    )
    
    # Hình thức nộp báo giá
    quotation_submission_method = fields.Selection(
        [
            ('direct', 'Trực tiếp tại bệnh viện'),
            ('email', 'Gửi email'),
            ('post', 'Gửi bưu điện'),
            ('bidding_system', 'Nộp qua hệ thống thầu'),
            ('other', 'Khác'),
        ],
        string="Hình thức nộp báo giá",
        required=True,
        default='email'
    )
    submission_date = fields.Date(
        string="Ngày nộp báo giá"
    )
    submitted_by = fields.Many2one(
        'res.users',
        string="Người nộp báo giá"
    )
    submission_note = fields.Text(
        string="Ghi chú nộp"
    )
    
    # Điều khoản
    delivery_time = fields.Char(
        string="Thời gian giao hàng"
    )
    warranty_period = fields.Integer(
        string="Thời gian bảo hành (tháng)"
    )
    terms_note = fields.Text(
        string="Ghi chú điều khoản khác"
    )
    
    # Hồ sơ & lưu trữ
    quotation_link = fields.Char(
        string="Link lưu trữ báo giá"
    )
    
    # Theo dõi
    sent_date = fields.Date(
        string="Ngày gửi khách hàng"
    )
    sent_by = fields.Many2one(
        'res.users',
        string="Người gửi"
    )
    customer_feedback = fields.Selection(
        [
            ('accepted', 'Đồng ý'),
            ('negotiate', 'Cần đàm phán'),
            ('rejected', 'Từ chối'),
        ],
        string="Phản hồi khách hàng"
    )
    feedback_note = fields.Text(
        string="Ghi chú phản hồi"
    )
    
    # Link to contract
    contract_id = fields.Many2one(
        'contract.contract',
        string="Hợp đồng",
        readonly=True,
        copy=False
    )

    # Action methods
    def action_create_contract(self):
        """Create contract from quotation"""
        self.ensure_one()
        
        if self.contract_id:
            return {
                'name': _('Hợp đồng'),
                'type': 'ir.actions.act_window',
                'res_model': 'contract.contract',
                'res_id': self.contract_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        # Create new contract
        contract_vals = {
            'name': self.quotation_title or self.name,
            'partner_company_id': self.partner_id.id,
            'partner_department_id': self.department_id.id if self.department_id else False,
            'sale_order_id': self.id,
            'contract_date': fields.Date.today(),
            'end_date': self.validity_date or fields.Date.today(),
            'service_category': 'supply' if self.quotation_type == 'goods' else 'service',
        }
        
        contract = self.env['contract.contract'].create(contract_vals)
        
        # Create contract lines from SO lines
        for line in self.order_line:
            self.env['contract.line'].create({
                'contract_id': contract.id,
                'product_id': line.product_id.id,
                'name': line.name,
                'uom_id': line.product_uom.id,
                'quantity': line.product_uom_qty,
                'price_unit': line.price_unit,
                'sale_order_line_id': line.id,
            })
        
        # Link contract to SO
        self.contract_id = contract.id
        
        return {
            'name': _('Hợp đồng'),
            'type': 'ir.actions.act_window',
            'res_model': 'contract.contract',
            'res_id': contract.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_quotation_send(self):
        """Override to update sent_date and sent_by"""
        result = super().action_quotation_send()
        self.write({
            'sent_date': fields.Date.today(),
            'sent_by': self.env.user.id,
        })
        return result


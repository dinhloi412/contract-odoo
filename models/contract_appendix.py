# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ContractAppendix(models.Model):
    _name = "contract.appendix"
    _description = "Contract Appendix"
    _order = "effective_date desc, id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Định danh
    appendix_number = fields.Char(
        string="Số phụ lục",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    name = fields.Char(
        string="Tên phụ lục",
        tracking=True
    )

    # Liên kết HĐ
    contract_id = fields.Many2one(
        'contract.contract',
        string="Hợp đồng gốc",
        required=True,
        ondelete='restrict',
        tracking=True
    )
    contract_number_display = fields.Char(
        string="Số HĐ (hiển thị)",
        related='contract_id.contract_number',
        readonly=True
    )

    # Phân loại PL
    appendix_type = fields.Selection(
        [
            ('add_goods', 'Bổ sung hàng hóa'),
            ('adjust_terms', 'Điều chỉnh điều khoản/giá'),
            ('extend_time', 'Gia hạn thời gian'),
            ('other', 'Khác'),
        ],
        string="Loại phụ lục",
        required=True,
        tracking=True
    )
    appendix_scope = fields.Text(
        string="Lý do/Phạm vi điều chỉnh",
        required=True
    )
    clause_reference = fields.Char(
        string="Điều khoản liên quan (nếu có)"
    )

    # Hiệu lực
    effective_date = fields.Date(
        string="Ngày hiệu lực",
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    end_date = fields.Date(
        string="Ngày kết thúc (nếu có)"
    )
    duration_days = fields.Integer(
        string="Thời hạn (ngày)",
        compute='_compute_duration_days',
        store=True
    )

    # Liên kết SO (tùy chọn)
    sale_order_id = fields.Many2one(
        'sale.order',
        string="Mã Đơn bán (SO)",
        tracking=True
    )

    # Chi tiết sản phẩm
    appendix_line_ids = fields.One2many(
        'contract.appendix.line',
        'appendix_id',
        string="Chi tiết sản phẩm"
    )

    # Giá trị
    currency_id = fields.Many2one(
        'res.currency',
        string="Tiền tệ",
        related='contract_id.currency_id',
        readonly=True
    )
    amount_appendix = fields.Monetary(
        string="Giá trị phụ lục",
        compute='_compute_amount_appendix',
        store=True,
        currency_field='currency_id'
    )
    affects_contract_total = fields.Boolean(
        string="Ảnh hưởng giá trị HĐ",
        default=True
    )
    amount_note = fields.Text(
        string="Ghi chú giá trị"
    )

    # Hồ sơ & liên kết
    appendix_link = fields.Char(
        string="Link lưu phụ lục"
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'appendix_attachment_rel',
        'appendix_id',
        'attachment_id',
        string="File đính kèm"
    )

    # Trạng thái
    state = fields.Selection(
        [
            ('draft', 'Nháp'),
            ('active', 'Hiệu lực'),
            ('cancelled', 'Hủy'),
        ],
        string="Trạng thái",
        default='draft',
        required=True,
        tracking=True
    )
    owner_id = fields.Many2one(
        'res.users',
        string="Người phụ trách PL",
        default=lambda self: self.env.user
    )
    activated_date = fields.Date(
        string="Ngày tạo hiệu lực",
        readonly=True
    )

    # Computed methods
    @api.depends('effective_date', 'end_date')
    def _compute_duration_days(self):
        for rec in self:
            if rec.effective_date and rec.end_date:
                delta = rec.end_date - rec.effective_date
                rec.duration_days = delta.days
            else:
                rec.duration_days = 0

    @api.depends('appendix_line_ids.price_subtotal')
    def _compute_amount_appendix(self):
        for rec in self:
            rec.amount_appendix = sum(rec.appendix_line_ids.mapped('price_subtotal'))

    # Onchange methods
    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        """Load product lines from selected sale order"""
        if self.sale_order_id:
            # Clear existing lines
            self.appendix_line_ids = [(5, 0, 0)]
            
            # Create new lines from SO
            lines = []
            for line in self.sale_order_id.order_line:
                lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'description': line.name,
                    'uom_id': line.product_uom.id,
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'change_action': 'add',
                    'sale_order_line_id': line.id,
                }))
            self.appendix_line_ids = lines

    # CRUD overrides
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('appendix_number', _('New')) == _('New'):
                # Generate appendix number based on contract
                contract = self.env['contract.contract'].browse(vals.get('contract_id'))
                if contract:
                    sequence = self.search_count([('contract_id', '=', contract.id)]) + 1
                    vals['appendix_number'] = f"PL-{contract.contract_number}-{sequence:03d}"
                else:
                    vals['appendix_number'] = self.env['ir.sequence'].next_by_code(
                        'contract.appendix'
                    ) or _('New')
        
        records = super().create(vals_list)
        
        # Update contract appendix count
        for record in records:
            record.contract_id._compute_appendix_count()
        
        return records

    def write(self, vals):
        result = super().write(vals)
        
        # Update contract appendix count if state changed
        if 'state' in vals:
            for rec in self:
                rec.contract_id._compute_appendix_count()
        
        return result

    def unlink(self):
        """Prevent deletion if appendix is active"""
        for rec in self:
            if rec.state == 'active':
                raise ValidationError(_(
                    'Không thể xóa phụ lục "%s" khi đã ở trạng thái Hiệu lực.'
                ) % rec.name)
        
        # Update contract appendix count
        contracts = self.mapped('contract_id')
        result = super().unlink()
        for contract in contracts:
            contract._compute_appendix_count()
        
        return result

    # Constraint methods
    @api.constrains('effective_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.effective_date and rec.end_date and rec.effective_date > rec.end_date:
                raise ValidationError(_(
                    'Ngày hiệu lực không thể sau ngày kết thúc.'
                ))

    # Action methods
    def action_activate(self):
        """Activate appendix"""
        self.write({
            'state': 'active',
            'activated_date': fields.Date.today()
        })
        
        # Update contract total if affects_contract_total is True
        for rec in self:
            if rec.affects_contract_total:
                rec.contract_id._compute_amount_total()

    def action_cancel(self):
        """Cancel appendix"""
        self.write({'state': 'cancelled'})


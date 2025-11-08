# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class Contract(models.Model):
    _name = "contract.contract"
    _description = "Sales Contract"
    _order = "contract_date desc, id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Thông tin chung
    contract_number = fields.Char(
        string="Số hợp đồng",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    name = fields.Char(
        string="Tên hợp đồng",
        required=True,
        tracking=True
    )
    contract_date = fields.Date(
        string="Ngày ký hợp đồng",
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    start_date = fields.Date(
        string="Ngày hiệu lực",
        tracking=True
    )
    end_date = fields.Date(
        string="Ngày kết thúc",
        required=True,
        tracking=True
    )
    service_category = fields.Selection(
        [
            ('supply', 'Cung cấp'),
            ('service', 'Dịch vụ'),
            ('rental', 'Cho thuê'),
            ('other', 'Khác'),
        ],
        string="Loại hợp đồng",
        required=True,
        tracking=True
    )

    # Hồ sơ thầu
    tender_code = fields.Char(string="Mã thầu")
    bid_notice_no = fields.Char(string="Số TBMT")

    # Pháp nhân (bên bán)
    company_id = fields.Many2one(
        'res.company',
        string="Pháp nhân phát hành",
        required=True,
        default=lambda self: self.env.company,
        tracking=True
    )
    company_signatory_id = fields.Many2one(
        'res.users',
        string="Người đại diện pháp nhân",
        required=True,
        tracking=True
    )
    responsible_user_id = fields.Many2one(
        'res.users',
        string="Nhân viên phụ trách",
        required=True,
        default=lambda self: self.env.user,
        tracking=True
    )

    # Bên mua
    partner_company_id = fields.Many2one(
        'res.partner',
        string="Bệnh viện",
        required=True,
        domain=[('is_company', '=', True)],
        tracking=True
    )
    partner_department_id = fields.Many2one(
        'res.partner',
        string="Khoa / Phòng",
        domain="[('parent_id', '=', partner_company_id)]",
        tracking=True
    )
    department_representative = fields.Char(
        string="Người đại diện khoa",
        compute='_compute_department_representative',
        store=True
    )
    partner_phone = fields.Char(
        string="Số điện thoại",
        compute='_compute_partner_contact',
        store=True
    )
    partner_email = fields.Char(
        string="Email",
        compute='_compute_partner_contact',
        store=True
    )

    # Chủ đầu tư
    investor_id = fields.Many2one(
        'res.partner',
        string="Chủ đầu tư",
        tracking=True
    )
    investor_representative = fields.Char(
        string="Người đại diện chủ đầu tư",
        related='investor_id.name',
        readonly=True
    )
    investor_position = fields.Char(
        string="Chức vụ",
        related='investor_id.function',
        readonly=True
    )

    # Giá trị & thời hạn
    currency_id = fields.Many2one(
        'res.currency',
        string="Tiền tệ",
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    amount_total = fields.Monetary(
        string="Tổng giá trị hợp đồng",
        compute='_compute_amount_total',
        store=True,
        currency_field='currency_id',
        tracking=True
    )
    duration_days = fields.Integer(
        string="Thời hạn (ngày)",
        compute='_compute_duration_days',
        store=True
    )
    extension_days = fields.Integer(
        string="Gia hạn hợp đồng (ngày)",
        default=0
    )

    # Tab Sản phẩm
    contract_line_ids = fields.One2many(
        'contract.line',
        'contract_id',
        string="Chi tiết sản phẩm"
    )

    # Tab Đơn bán & liên kết
    sale_order_id = fields.Many2one(
        'sale.order',
        string="Mã đơn bán (SO)",
        tracking=True
    )
    sale_order_ids = fields.Many2many(
        'sale.order',
        'contract_sale_order_rel',
        'contract_id',
        'sale_order_id',
        string="Các SO liên quan"
    )

    # Hồ sơ
    bidding_link = fields.Char(string="Link hồ sơ dự thầu")
    contract_link = fields.Char(string="Link hợp đồng")
    appendix_link = fields.Char(string="Link phụ lục")
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'contract_attachment_rel',
        'contract_id',
        'attachment_id',
        string="File đính kèm"
    )

    # Theo dõi & chứng từ
    delivery_date = fields.Date(string="Ngày giao hàng")
    acceptance_date = fields.Date(string="Ngày nghiệm thu")
    liquidation_date = fields.Date(string="Ngày thanh lý")
    
    handover_attachment_ids = fields.Many2many(
        'ir.attachment',
        'contract_handover_attachment_rel',
        'contract_id',
        'attachment_id',
        string="Biên bản bàn giao"
    )
    acceptance_attachment_ids = fields.Many2many(
        'ir.attachment',
        'contract_acceptance_attachment_rel',
        'contract_id',
        'attachment_id',
        string="Biên bản nghiệm thu"
    )
    liquidation_attachment_ids = fields.Many2many(
        'ir.attachment',
        'contract_liquidation_attachment_rel',
        'contract_id',
        'attachment_id',
        string="Biên bản thanh lý"
    )
    
    handover_link = fields.Char(string="Link hồ sơ bàn giao")
    acceptance_link = fields.Char(string="Link hồ sơ nghiệm thu")
    liquidation_link = fields.Char(string="Link hồ sơ thanh lý")

    # Bảo hành & hóa đơn
    warranty_months = fields.Integer(string="Thời gian bảo hành (tháng)")
    invoice_number = fields.Char(string="Số hóa đơn")
    invoice_issue_date = fields.Date(string="Ngày phát hành hóa đơn")

    # Liên hệ & ảnh hưởng
    contact_person_id = fields.Many2one(
        'res.partner',
        string="Người liên hệ chính",
        domain="[('parent_id', '=', partner_company_id)]"
    )
    contact_job_title = fields.Char(
        string="Chức vụ",
        related='contact_person_id.function',
        readonly=True
    )
    contact_phone = fields.Char(
        string="SĐT",
        related='contact_person_id.phone',
        readonly=True
    )
    contact_email = fields.Char(
        string="Email",
        related='contact_person_id.email',
        readonly=True
    )

    # Ảnh hưởng & hiệp hội
    budget_influence_level = fields.Selection(
        [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
        ],
        string="Mức độ ảnh hưởng ngân sách"
    )
    medical_association_role = fields.Char(
        string="Vai trò trong hiệp hội y khoa"
    )
    support_level = fields.Selection(
        [
            ('a', 'A'),
            ('b', 'B'),
            ('c', 'C'),
        ],
        string="Mức độ ủng hộ (A/B/C)"
    )

    # Chuyên môn & quan tâm
    specialty_field = fields.Char(
        string="Lĩnh vực chuyên môn"
    )
    interest_topics = fields.Text(
        string="Chủ đề quan tâm"
    )

    # Tab Ghi chú & nhật ký
    interaction_history = fields.Text(string="Lịch sử tương tác")
    customer_feedback = fields.Text(string="Feedback khách hàng")
    commitment_note = fields.Text(string="Cam kết / Đề xuất mở")
    last_update_date = fields.Date(
        string="Ngày cập nhật gần nhất",
        default=fields.Date.today,
        readonly=True
    )
    updated_by = fields.Many2one(
        'res.users',
        string="Người cập nhật cuối",
        default=lambda self: self.env.user,
        readonly=True
    )

    # Trạng thái & phụ lục
    state = fields.Selection(
        [
            ('draft', 'Nháp'),
            ('active', 'Hiệu lực'),
            ('expired', 'Hết hạn'),
            ('cancelled', 'Hủy'),
        ],
        string="Trạng thái hợp đồng",
        default='draft',
        required=True,
        tracking=True
    )
    appendix_count = fields.Integer(
        string="Số lượng phụ lục",
        compute='_compute_appendix_count',
        store=True
    )
    private_note = fields.Text(string="Ghi chú nội bộ")

    # Computed methods
    @api.depends('partner_department_id')
    def _compute_department_representative(self):
        """Get the name of the department contact/representative"""
        for rec in self:
            if rec.partner_department_id:
                # Try to find a contact person for the department
                contacts = self.env['res.partner'].search([
                    ('parent_id', '=', rec.partner_department_id.id),
                    ('type', '=', 'contact')
                ], limit=1)
                rec.department_representative = contacts.name if contacts else rec.partner_department_id.name
            else:
                rec.department_representative = False

    @api.depends('partner_department_id', 'partner_company_id')
    def _compute_partner_contact(self):
        for rec in self:
            if rec.partner_department_id:
                rec.partner_phone = rec.partner_department_id.phone
                rec.partner_email = rec.partner_department_id.email
            elif rec.partner_company_id:
                rec.partner_phone = rec.partner_company_id.phone
                rec.partner_email = rec.partner_company_id.email
            else:
                rec.partner_phone = False
                rec.partner_email = False

    @api.depends('contract_line_ids.price_subtotal')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.contract_line_ids.mapped('price_subtotal'))

    @api.depends('start_date', 'end_date')
    def _compute_duration_days(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                delta = rec.end_date - rec.start_date
                rec.duration_days = delta.days
            else:
                rec.duration_days = 0

    @api.depends('contract_line_ids')
    def _compute_appendix_count(self):
        for rec in self:
            rec.appendix_count = self.env['contract.appendix'].search_count([
                ('contract_id', '=', rec.id)
            ])

    # Onchange methods
    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        """Load product lines from selected sale order"""
        if self.sale_order_id:
            # Clear existing lines
            self.contract_line_ids = [(5, 0, 0)]

            # Create new lines from SO
            lines = []
            for line in self.sale_order_id.order_line:
                lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'uom_id': line.product_uom.id,
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'sale_order_line_id': line.id,
                }))
            self.contract_line_ids = lines

            # Auto-fill customer info
            if self.sale_order_id.partner_id:
                self.partner_company_id = self.sale_order_id.partner_id

    @api.onchange('partner_company_id')
    def _onchange_partner_company_id(self):
        """Clear department when company changes"""
        if self.partner_company_id:
            self.partner_department_id = False

    # CRUD overrides
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('contract_number', _('New')) == _('New'):
                vals['contract_number'] = self.env['ir.sequence'].next_by_code(
                    'contract.contract'
                ) or _('New')
        return super().create(vals_list)

    def write(self, vals):
        # Update last_update_date and updated_by
        vals['last_update_date'] = fields.Date.today()
        vals['updated_by'] = self.env.user.id
        return super().write(vals)

    def unlink(self):
        """Prevent deletion if contract has appendices or linked SOs"""
        for rec in self:
            if rec.appendix_count > 0:
                raise ValidationError(_(
                    'Không thể xóa hợp đồng "%s" vì đã có phụ lục liên kết.'
                ) % rec.name)
            if rec.sale_order_id or rec.sale_order_ids:
                raise ValidationError(_(
                    'Không thể xóa hợp đồng "%s" vì đã liên kết với đơn bán hàng.'
                ) % rec.name)
        return super().unlink()

    # Constraint methods
    @api.constrains('partner_department_id', 'partner_company_id')
    def _check_department_belongs_to_company(self):
        for rec in self:
            if rec.partner_department_id and rec.partner_company_id:
                if rec.partner_department_id.parent_id != rec.partner_company_id:
                    raise ValidationError(_(
                        'Khoa "%s" không thuộc bệnh viện "%s".'
                    ) % (rec.partner_department_id.name, rec.partner_company_id.name))

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.start_date > rec.end_date:
                raise ValidationError(_(
                    'Ngày hiệu lực không thể sau ngày kết thúc.'
                ))

    # Action methods
    def action_view_appendices(self):
        """Smart button action to view appendices"""
        self.ensure_one()
        return {
            'name': _('Phụ lục hợp đồng'),
            'type': 'ir.actions.act_window',
            'res_model': 'contract.appendix',
            'view_mode': 'list,form',
            'domain': [('contract_id', '=', self.id)],
            'context': {'default_contract_id': self.id},
        }

    def action_set_active(self):
        """Set contract to active state"""
        self.write({'state': 'active'})

    def action_set_expired(self):
        """Set contract to expired state"""
        self.write({'state': 'expired'})

    def action_cancel(self):
        """Cancel contract"""
        self.write({'state': 'cancelled'})


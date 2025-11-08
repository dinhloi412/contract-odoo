# -*- coding: utf-8 -*-
{
    "name": "Contract Management",
    "summary": "Manage sales contracts, appendices, and quotations for hospital equipment",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "depends": ["base", "sale", "product", "crm"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/contract_views.xml",
        "views/contract_appendix_views.xml",
        "views/quotation_views.xml",
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}


# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

from ..utils import is_valid_email


class AgencyProperty(models.Model):
    _name = 'agency.property'
    _description = 'Agency Property Management'

    desc = fields.Char('Description', size=255, required=True)
    adress1 = fields.Char('Address1', size=255, required=True)
    adress2 = fields.Char('Adress2', size=255)
    surface = fields.Float('Surface', required=True)
    state = fields.Selection([('for_rent', 'Rent'), ('for_sale', 'For Sale'), ('rented', 'Rented')], 'State')

    zip_id = fields.Many2one('res.city.zip', 'Ubication', required=True)

    type_id = fields.Many2one('agency.type', 'Type', required=True)

    client_id = fields.Many2one('res.partner', 'Client', required=True)

    element_ids = fields.One2many('agency.element', 'element_id', 'Elements')

    portal_ids = fields.Many2many('agency.portal', 'agency_property_portal_rel', 'property_id', 'portal_id', 'Portals', readonly=True)

    @api.depends('adress1')
    def _compute_display_name(self):
        for property in self:
            if property.ubication_id != False and property.adress1 != False:
                # display_name és un camp d'Odoo directament
                property.display_name = property.ubication_id + " - " + property.adress1
            else:
                property.display_name = "New Property"


class AgencyType(models.Model):
    _name = 'agency.type'
    _description = 'Agency Type Management'

    name = fields.Char('Name', size=60, required=True)

    property_ids = fields.One2many('agency.property', 'property_id', 'Properties')


class AgencyElement(models.Model):
    _name = 'agency.element'
    _description = 'Agency Element Management'

    name = fields.Char('Name', size=60, required=True)
    area = fields.Float('Area', required=True)
    photo = fields.Binary('Photo')


class AgencyPortal(models.Model):
    _name = 'agency.portal'
    _description = 'Agency Portal Management'

    name = fields.Char('Name', size=60, required=True)
    phone = fields.Char('Phone')
    web = fields.Char('Web', required=True)

    property_ids = fields.Many2many('agency.property', 'agency_property_portal_rel', 'portal_id', 'property_id', 'Properties', readonly=True)
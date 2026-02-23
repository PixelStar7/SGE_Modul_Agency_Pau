# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

from ..utils import is_valid_email


class AgencyProperty(models.Model):
    _name = 'agency.property'
    _description = 'Agency Property Management'

    description = fields.Html('Description', required=True)
    address1 = fields.Char('Address1', size=255, required=True)
    address2 = fields.Char('Address2', size=255)
    area = fields.Float('Area', required=True)
    state = fields.Selection([('for_rent', 'Rent'), ('for_sale', 'For Sale'), ('rented', 'Rented')], 'State', required=True)
    active = fields.Boolean('Active', default=True)
    owner_phone = fields.Char('Owner Phone', related='owner_id.phone')

    zip_id = fields.Many2one('res.city.zip', 'Ubication', required=True)

    type_id = fields.Many2one('agency.type', 'Type', required=True)

    owner_id = fields.Many2one('res.partner', 'Client', required=True)

    element_ids = fields.One2many('agency.element', 'property_id', 'Elements', readonly=True)

    portal_ids = fields.Many2many('agency.portal', 'agency_property_portal_rel', 'property_id', 'portal_id', 'Portals', readonly=True)

    @api.depends('address1', 'zip_id')
    def _compute_display_name(self):
        for property in self:
            if property.zip_id != False and property.address1 != False:
                # display_name és un camp d'Odoo directament
                ciutat = property.zip_id.city_id.name or property.zip_id.name
                property.display_name = f"{ciutat} - {property.address1}"
            else:
                property.display_name = "New Property"

    @api.constrains('area')
    def _check_area(self):
        for property in self:
            if property.area <= 0:
                raise ValidationError(_('Area must be positive.'))


class AgencyType(models.Model):
    _name = 'agency.type'
    _description = 'Agency Type Management'
    _order = 'name'

    name = fields.Char('Name', size=60, translate=True, required=True)

    property_ids = fields.One2many('agency.property', 'type_id', 'Properties')

    @api.onchange('name')
    def _capitalize_name(self):
        for atype in self:
            if atype.name:
                atype.name = atype.name.capitalize()

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'The type name must be unique!')
    ]

class AgencyElement(models.Model):
    _name = 'agency.element'
    _description = 'Agency Element Management'

    name = fields.Char('Name', size=60, required=True)
    area = fields.Float('Area', required=True)
    photo = fields.Binary('Photo')

    property_id = fields.Many2one('agency.property', 'Property', ondelete='cascade', required=True)

    @api.constrains('area')
    def _check_area(self):
        for element in self:
            if element.area <= 0:
                raise ValidationError(_('Area must be positive.'))


class AgencyPortal(models.Model):
    _name = 'agency.portal'
    _description = 'Agency Portal Management'
    _order = 'name'

    name = fields.Char('Name', size=60, required=True)
    phone = fields.Char('Phone')
    web = fields.Char('Web', required=True)

    q_properties = fields.Integer('Qty. Properties', compute='_compute_qty_properties')

    property_ids = fields.Many2many('agency.property', 'agency_property_portal_rel', 'portal_id', 'property_id', 'Properties', readonly=True)

    @api.depends('property_ids')
    def _compute_qty_properties(self):
        for portal in self:
            portal.q_properties = len(portal.property_ids)

    @api.constrains('phone')
    def _check_phone(self):
        for portal in self:
            if portal.phone and not portal.phone.isdigit():
                raise ValidationError(_('The phone number must contain only digits.'))
    
    @api.onchange('name')
    def _upper_name(self):
        for portal in self:
            if portal.name:
                portal.name = portal.name.upper()

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'The portal name must be unique!')
    ]
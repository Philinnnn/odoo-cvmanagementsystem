import requests
from odoo import models, fields, api
from odoo.exceptions import UserError


class CvPosition(models.Model):
    _name = 'cv_integration.position'
    _description = 'Imported CV Management Position'

    name = fields.Char(string='Title', required=True)
    api_base_url = fields.Char(string='API Base URL')
    api_token = fields.Char(string='API Token')
    imported_at = fields.Datetime(string='Imported At')
    attribute_ids = fields.One2many('cv_integration.position_attribute', 'position_id', string='Attributes')

    def action_import(self):
        for record in self:
            if not record.api_base_url or not record.api_token:
                raise UserError('Please provide both API Base URL and API Token.')

            url = f"{record.api_base_url.rstrip('/')}/api/positions/{record.api_token}/aggregate"
            response = requests.get(url, timeout=15)

            if response.status_code != 200:
                raise UserError(f'Import failed: HTTP {response.status_code}')

            data = response.json()
            record.name = data.get('positionTitle', record.name)
            record.imported_at = fields.Datetime.now()

            record.attribute_ids.unlink()

            for attr in data.get('attributes', []):
                summary = self._format_summary(attr)
                self.env['cv_integration.position_attribute'].create({
                    'position_id': record.id,
                    'name': attr.get('name'),
                    'data_type': attr.get('dataType'),
                    'summary': summary,
                })

    @staticmethod
    def _format_summary(attr):
        data_type = attr.get('dataType')
        filled = attr.get('filledCount', 0)
        total = attr.get('totalCount', 0)

        if data_type == 'Numeric':
            avg = attr.get('average')
            minimum = attr.get('min')
            maximum = attr.get('max')
            if avg is not None:
                return f'Avg: {avg:.2f}, Min: {minimum}, Max: {maximum} ({filled}/{total} filled)'
            return f'No data ({filled}/{total} filled)'

        top_values = attr.get('topValues', [])
        if top_values:
            parts = [f"{v['value']} ({v['count']})" for v in top_values]
            return f"Top: {', '.join(parts)} ({filled}/{total} filled)"

        return f'{filled}/{total} filled'


class CvPositionAttribute(models.Model):
    _name = 'cv_integration.position_attribute'
    _description = 'Imported Position Attribute'

    position_id = fields.Many2one('cv_integration.position', required=True, ondelete='cascade')
    name = fields.Char(string='Attribute')
    data_type = fields.Char(string='Type')
    summary = fields.Char(string='Aggregated Result')
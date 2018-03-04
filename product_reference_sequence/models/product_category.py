from openerp import models, fields, api

class product_category(models.Model):
    _inherit = "product.category"
    
    sequence_id = fields.Many2one('ir.sequence', string = 'Internal Reference Sequence')

    def get_next_id(self):
        self.ensure_one();
        result = ''
        if self.sequence_id:
             result = self.sequence_id.next_by_id() or ''
        return result

# -*- coding: utf-8 -*-
import base64
import logging
from lxml import etree
from io import BytesIO
from odoo import models

_logger = logging.getLogger(__name__)

try:
    from pytrustnfe.nfe.danfe import danfe
except ImportError:
    _logger.warning('Cannot import pytrustnfe', exc_info=True)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def render_qweb_pdf(self, res_ids, data=None):
        if self.report_name != 'br_nfe.main_template_br_nfe_danfe':
            return super(IrActionsReport, self).render_qweb_pdf(
                res_ids, data=data)

        nfes = self.env['invoice.eletronic'].search([('id', 'in', res_ids)])

        nfes_xml = []
        for nfe in nfes:
            nfe_xml = base64.decodestring(nfe.nfe_processada)
            nfes_xml.append(etree.fromstring(nfe_xml))

        cces_xml_element = []

        for cce in nfes:
            cce_list = self.env['ir.attachment'].search([
                ('res_model','=','invoice.eletronic'),
                ('res_id','=',cce.id),
                ('name','like','cce-')
            ])
            for xml in cce_list:
                cce_xml = base64.decodestring(xml[0].datas)
                cces_xml_element.append(etree.fromstring(cce_xml))

        logo = False
        if nfe.invoice_id.company_id.logo:
            logo = base64.decodestring(nfe.invoice_id.company_id.logo)
        elif nfe.invoice_id.company_id.logo_web:
            logo = base64.decodestring(nfe.invoice_id.company_id.logo_web)

        if logo:
            tmpLogo = BytesIO()
            tmpLogo.write(logo)
            tmpLogo.seek(0)
        else:
            tmpLogo = False

        oDanfe = danfe(list_xml=nfes_xml,
                       cce_xml=cces_xml_element, logo=tmpLogo)

        tmpDanfe = BytesIO()
        oDanfe.writeto_pdf(tmpDanfe)
        danfe_file = tmpDanfe.getvalue()
        tmpDanfe.close()

        return danfe_file, 'pdf'
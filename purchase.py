#coding: utf-8
import logging
from openerp.osv import fields, osv
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
class purchase_order(osv.osv):
  '''
  继承account.voucher对象,修改state,使其适用于工作流
  '''
  _name = 'purchase.order'
  _description = 'purchase order'
  _inherit = 'purchase.order'

  STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ Sent'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Order'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('subed_1','工程采购'),
        ('subed_2','技术采购'),
        ('project_stock_manager_approved','库管已审'),
        ('it_stock_manager_approved','库管已审'),
        ('it_manager_approved','技术经理已审'),
        ('support_manager_approved','保障经理已审'),
        ('houqin_manager_approved','后勤经理已审'),
    ]

  _columns = {
      'state': fields.selection(STATE_SELECTION, 'Status', readonly=True, select=True),
      }



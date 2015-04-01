#coding: utf-8
import logging
from openerp.osv import fields, osv
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
class product(osv.osv):
    '''
    定义product,添加了external_id,主要用于从视易数据库中导入
    '''
    _name = "product.product"
    _inherit = "product.product"

    _columns = {
      'external_id':fields.integer('external id')
      }
 

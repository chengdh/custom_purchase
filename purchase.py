#coding: utf-8
import logging
from openerp.osv import fields, osv
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
class purchase_order(osv.osv):
  '''
  继承purchase.order对象,修改state,使其适用于工作流
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
        ('shop_manager_approved','店长已审'),
    ]

  def _get_where_args_with_workflow(self,cr,uid):
    '''
    获取当前用户工作流审批相关的where 条件
    '''
    matched_groups = None
    pool = self.pool.get('res.users')
    user = pool.browse(cr,uid,uid)
    groups = user.groups_id
    if not groups: return None 
    #根据group_id获取group名称
    model_data_pool = self.pool.get("ir.model.data")

    #库管
    group_stock_manager = model_data_pool.get_object(cr,uid,'stock','group_stock_manager')

    #店长
    group_shop_manager = model_data_pool.get_object(cr,uid,'base','group_shop_manager')

    #保障经理
    group_support_manager = model_data_pool.get_object(cr,uid,'custom_purchase','group_support_manager')

    #后勤主管
    group_houqin_manager = model_data_pool.get_object(cr,uid,'custom_purchase','group_houqin_manager')

    #技术主管
    group_it_manager = model_data_pool.get_object(cr,uid,'custom_purchase','group_it_manager')

    #总经理
    #group_ceo = model_data_pool.get_object(cr,uid,'base','group_ceo')

    #找出当前用户属于哪个group
    list_b = [group_stock_manager,group_shop_manager,group_support_manager,group_houqin_manager,group_it_manager]
    matched_groups = list(set(groups).intersection(set(list_b)))
    if not matched_groups: return None

    state = "__not_use__"
    signal = "__not_use__"

    #FIXME 暂不支持库管在手机上看到待审批单据
    '''
    if group_stock in matched_groups:
      state = ["sub_1","sub_2"]
      signal = "stock_manager_approve_project"
    '''

    if group_shop_manager in matched_groups:
      state = ["project_stock_manager_approved"]
      signal = "shop_manager_approve"

    if group_it_manager in matched_groups:
      state = ["it_stock_manager_approved"]
      signal = "it_manager_approve"

    if group_support_manager in matched_groups:
      state = ["shop_manager_approved"]
      signal = "support_manager_approve"

    if group_houqin_manager in matched_groups:
      state = ["support_manager_approved"]
      signal = "houqin_manager_approve"

    return {"state" : state,"signal" : signal}

  def _next_workflow_signal(self,cr,uid, ids, field_name, arg, context):
    res = {}
    #获取当前用户能查看的expense的状态
    where_args = self._get_where_args_with_workflow(cr,uid)
    for record in self.browse(cr,uid,ids,context):
      res[record.id] = None
      if record.state in where_args['state']: res[record.id] = where_args['signal']

    return res


  _columns = {
      'department_id':fields.many2one('hr.department','部门', readonly=True, states={'draft':[('readonly',False)]}),
      'state': fields.selection(STATE_SELECTION, 'Status', readonly=True, select=True),
      "next_workflow_signal" : fields.function(_next_workflow_signal,string="根据当前用户计算下一个workflow signal"),
      }

  def get_waiting_audit_purchase_orders(self,cr,uid,context=None):
    #FIXME 为简单处理,此处为硬编码 
    #1 根据uid获取用户所属group_id
    #2 根据group_id找出对应的工作流state
    #3 根据state获取expense列表,返回客户端
    where_args = self._get_where_args_with_workflow(cr,uid)
    if not where_args : return []

    _logger.debug("[state,signal] = " + repr(where_args));
    _logger.debug("context = " + repr(context));
    ids = self.search(cr,uid,[("state","in",where_args['state'])])
    _logger.debug("ids = " + repr(ids));
    if not ids: return []
    purchase_orders = self.read(cr,uid,ids,context=context)
    _logger.debug("return purchase_orders =  " + repr(purchase_orders));
    return purchase_orders

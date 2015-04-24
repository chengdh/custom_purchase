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
        ('subed_zongbu_caigou','总部采购'),
        ('zongbu_caigou_support_manager_approved','保障经理已审'),
        ('zongbu_caigou_hr_manager_approved','办公室主任已审'),
        ('zongbu_caigou_ceo_approved','总经理已审'),

        ('subed_diannei_jishu','店内技术物品采购'),
        ('diannei_jishu_support_manager_approved','保障经理已审'),
        ('diannei_jishu_shop_manager_approved','店长已审'),
        ('diannei_jishu_vice_general_manager_approved','副总已审'),
        ('diannei_jishu_it_manager_approved','技术部经理已审'),

        ('subed_diannei_gongcheng','店内工程物品采购'),
        ('diannei_gongcheng_support_manager_approved','保障经理已审'),
        ('diannei_gongcheng_shop_manager_approved','店长已审'),
        ('diannei_gongcheng_vice_general_manager_approved','副总已审'),
        ('diannei_gongcheng_project_manager_approved','工程部经理已审'),

        ('subed_diannei_ryp ','店内日用品采购'),
        ('diannei_ryp_support_manager_approved','保障经理已审'),
        ('diannei_ryp_shop_manager_approved','店长已审'),
        ('diannei_ryp_vice_general_manager_approved','副总已审'),
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

    #保障经理
    group_support_manager = model_data_pool.get_object(cr,uid,'custom_purchase','group_support_manager')

    #办公室主任
    group_hr_manager = model_data_pool.get_object(cr,uid,'base','group_hr_manager')

    #店长
    group_shop_manager = model_data_pool.get_object(cr,uid,'base','group_shop_manager')

    #总经理
    group_ceo = model_data_pool.get_object(cr,uid,'base','group_ceo')

    #副总经理
    group_vice_general_manager = model_data_pool.get_object(cr,uid,'base','group_vice_general_manager')

    #工程部主管
    group_project_manager = model_data_pool.get_object(cr,uid,'custom_purchase','group_project_manager')


    #技术主管
    group_it_manager = model_data_pool.get_object(cr,uid,'custom_purchase','group_it_manager')

    #找出当前用户属于哪个group
    list_b = [group_support_manager,group_hr_manager,
              group_shop_manager,group_ceo,group_vice_general_manager,
              group_it_manager,group_project_manager]

    matched_groups = list(set(groups).intersection(set(list_b)))
    if not matched_groups: return None

    state = "__not_use__"
    signal = "__not_use__"

    if group_support_manager in matched_groups:
      state = ["subed_zongbu_caigou","subed_diannei_jishu","subed_diannei_gongcheng","subed_diannei_ryp"]
      signal = "support_manager_approve"

    if group_hr_manager in matched_groups:
      state = ["zongbu_caigou_support_manager_approved"]
      signal = "hr_manager_approve"

    if group_ceo in matched_groups:
      state = ["zongbu_caigou_hr_manager_approved"]
      signal = "ceo_approve"

    if group_shop_manager in matched_groups:
      state = ["diannei_jishu_support_manager_approved",
               "diannei_gongcheng_support_manager_approved",
               "diannei_ryp_support_manager_approved",
               ]
      signal = "shop_manager_approve"

    if group_vice_general_manager in matched_groups:
      state = ["diannei_jishu_shop_manager_approved",
               "diannei_gongcheng_shop_manager_approved",
               "diannei_ryp_shop_manager_approved",
               ]
      signal = "vice_general_manager_approve"

    if group_it_manager in matched_groups:
      state = ["diannei_jishu_vice_general_manager_approved"]
      signal = "it_manager_approve"

    if group_project_manager in matched_groups:
      state = ["diannei_gongcheng_vice_general_manager_approved"]
      signal = "project_manager_approve"

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

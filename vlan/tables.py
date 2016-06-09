from django.utils.translation import ugettext_lazy as _
 
from horizon import tables
 
from openstack_dashboard.dashboards.fabric.vlan import utils
 
class AddTableData(tables.LinkAction):
    name = "add"
    verbose_name = _("Add Vlan")
    url = "horizon:fabric:vlan:add"
    classes = ("btn-launch", "ajax-modal")
 
class DeleteTableData(tables.DeleteAction):
    data_type_singular = _("Vlan")
    data_type_plural = _("Vlans")

    def delete(self,request,obj_Id):
        utils.deleteVlan(self,obj_Id)
 
class FilterAction(tables.FilterAction):
    def filter(self, table, vlans, filter_string):
        filterString = filter_string.lower()
        return [vlan for vlan in vlans
                if filterString in vlan.title.lower()]
 
class UpdateRow(tables.Row):
    ajax = True
 
    def get_data(self, request, post_id):
        pass
 
class VlanTable(tables.DataTable):
    id = tables.Column("id",
                          verbose_name=_("Id"))
 
    name = tables.Column("name",
                          verbose_name=_("Name"))
 
    description = tables.Column("description",
                          verbose_name=_("Description"))
 
    class Meta:
        name = "vlan"
        verbose_name = _("Vlans")
        template="horizon/common/_data_table.html"
        row_class = UpdateRow
        table_actions = (AddTableData,
                         FilterAction,DeleteTableData)



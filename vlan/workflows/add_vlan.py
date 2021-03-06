import traceback

from horizon import workflows, forms, exceptions
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard.dashboards.fabric.vlan import utils

class SetAddVlanDetailsAction(workflows.Action):

    id = forms.IntegerField(
        label=_("ID"),
        required=True,
        min_value=1,
        max_value=4096,
        help_text=_("Vlan ID"))


    name = forms.CharField(
        label=_("Name"),
        required=True,
        max_length=80,
        help_text=_("VLAN Name"))

    description = forms.CharField(
        label=_("Description"),
        required=False,
        max_length=120,
        help_text=_("VLAN Description"))

    class Meta:
        name = _("Details")

    def __init__(self, request, context, *args, **kwargs):
        self.request = request
        self.context = context
        super(SetVlanDetailsAction, self).__init__(
            request, context, *args, **kwargs)

class SetAddVlanDetails(workflows.Step):
    action_class = SetAddVlanDetailsAction
    contributes = ("id","name", "description")

    def contribute(self, data, context):
        if data:
            context['id'] = data.get("name", "")
            context['name'] = data.get("name", "")
            context['description'] = data.get("description", "")
        return context

class AddVlan(workflows.Workflow):
    slug = "add"
    name = _("Add")
    finalize_button_name = _("Add")
    success_message = _('Added vlan "%s".')
    failure_message = _('Unable to add vlan "%s".')
    success_url = "horizon:fabric:vlan:index"
    failure_url = "horizon:fabric:vlan:index"
    default_steps = (SetAddVlanDetails,)

    def format_status_message(self, message):
         return message % self.context.get('name', 'unknown vlan')

    def handle(self, request, context):
        try:
            utils.addVlan(self, request, context)
            return True
        except Exception:
            print traceback.format_exc()
            exceptions.handle(request, _("Unable to add vlan"))
            return False
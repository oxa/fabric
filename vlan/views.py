# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from horizon import tables,tabs,exceptions,forms,workflows

from openstack_dashboard.dashboards.fabric.vlan.tables import VlanTable
from openstack_dashboard.dashboards.fabric.vlan import utils
from openstack_dashboard.dashboards.fabric.vlan.workflows import AddVlan


class IndexView(tables.DataTableView):
    table_class = VlanTable
    template_name = 'fabric/vlan/index.html'

    def get_data(self):
        return utils.getVlans(self)


class AddVlanView(workflows.WorkflowView):
    workflow_class= AddVlan

    def get_initial(self):
        initial = super(AddVlanView,self).get_initial()
        return initial


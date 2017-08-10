# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
# 2017 Pontus Freyhult
#
# This is a simple callback to provide more readable output by collapsing 
# reports for hosts with identical output.
# 
# It's based on the minimal callback from ansible and thus has that license.
# 
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.callback import CallbackBase
from ansible import constants as C

class CallbackModule(CallbackBase):

    '''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'minimal'

    saved = {}

    def __del__(self):

        for p,q in self.saved.items():
            # p is hosts tuple 
            if q[0] in C.MODULE_NO_JSON: 
                # self._display.display(self._command_generic_msg(','.join(sorted(p)), q[2], q[1]), color=C.COLOR_OK)                                  
                print(self._command_generic_msg(','.join(sorted(p)), q[2], q[1]))
        
    def _command_generic_msg(self, host, result, caption):
        ''' output the result of a command run '''

        buf = "%s | %s | rc=%s >>\n" % (host, caption, result.get('rc', -1))
        buf += result.get('stdout','')
        buf += result.get('stderr','')
        buf += result.get('msg','')

        return buf + "\n"

    def clean_result(self, result):
        result['end'] = None
        result['start'] = None
        result['delta'] = None
        return result

    def update_saved(self, post, host):


        # We have already, remove the old occurence and 
        # create a new with our new host name added.
        for p,q in self.saved.items():
            if str(q) == str(post):
                del self.saved[p]
                self.saved[p+(host,)] = post
                return
            
        # New post needed if we get here.    
        self.saved[(host,)] = post
            


    def v2_runner_on_failed(self, result, ignore_errors=False):

        self._handle_exception(result._result)
        self._handle_warnings(result._result)

        res = self.clean_result(result._result)
        post = (result._task.action, 'FAILED', res)

        self.update_saved(post,result._host.get_name())

        #if result._task.action in C.MODULE_NO_JSON and 'module_stderr' not in result._result:
        #    self._display.display(self._command_generic_msg(result._host.get_name(), result._result, "FAILED"), color=C.COLOR_ERROR)
        #else:
        #    self._display.display("%s | FAILED! => %s" % (result._host.get_name(), self._dump_results(result._result, indent=4)), color=C.COLOR_ERROR)

    def v2_runner_on_ok(self, result):
        self._clean_results(result._result, result._task.action)
        self._handle_warnings(result._result)

        res = self.clean_result(result._result)
        post = (result._task.action, 'SUCCESS', result._result)

        self.update_saved(post, result._host.get_name())

        #if result._task.action in C.MODULE_NO_JSON:
        #    self._display.display(self._command_generic_msg(result._host.get_name(), result._result, "SUCCESS"), color=C.COLOR_OK)
        #else:
        #    if 'changed' in result._result and result._result['changed']:
        #        self._display.display("%s | SUCCESS => %s" % (result._host.get_name(), self._dump_results(result._result, indent=4)), color=C.COLOR_CHANGED)
        #    else:
        #        self._display.display("%s | SUCCESS => %s" % (result._host.get_name(), self._dump_results(result._result, indent=4)), color=C.COLOR_OK)

    def v2_runner_on_skipped(self, result):
        post = (result._task.action, 'SKIPPED', result._result)
        self.update_saved(post, result._host.get_name())

        #self._display.display("%s | SKIPPED" % (result._host.get_name()), color=C.COLOR_SKIP)

    def v2_runner_on_unreachable(self, result):
        post = (result._task.action, 'UNREACHABLE', result._result)
        self.update_saved(post, result._host.get_name())

        #self._display.display("%s | UNREACHABLE! => %s" % (result._host.get_name(), self._dump_results(result._result, indent=4)), color=C.COLOR_UNREACHABLE)

    def v2_on_file_diff(self, result):
        if 'diff' in result._result and result._result['diff']:
            self._display.display(self._get_diff(result._result['diff']))



.. _unbelievable.hpe.oneview_inventory:


************************
unbelievable.hpe.oneview
************************

**HPE OneView inventory source**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Get iLO hosts from a HPE OneView.
- For each host model ('shortModel' from OneView) a group will be created containing all hosts with this host model. Example: 'DL360_Gen10'
- For each iLO major version ('mpModel' from OneView) a group will be created containing all hosts with this host model. Example: 'iLO5'
- All groups are children of group 'oneview_members'
- Host vars 'shortModel' and 'mpModel will be set
- Uses a configuration file as an inventory source, it must end with ``oneview.yml`` or ``oneview.yaml``



Requirements
------------
The below requirements are needed on the local Ansible controller node that executes this inventory.

- requests >= 1.1


Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
                <th>Configuration</th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>add_domain</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 1.0.0</div>
                </td>
                <td>
                </td>
                    <td>
                    </td>
                <td>
                        <div>Add domain to hostname.</div>
                        <div>Requires <code>hostname_short</code> to be <code>no</code>.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>hostname_short</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 1.0.0</div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li><div style="color: blue"><b>yes</b>&nbsp;&larr;</div></li>
                        </ul>
                </td>
                    <td>
                    </td>
                <td>
                        <div>Ues short hostnames.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>password</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 1.0.0</div>
                </td>
                <td>
                </td>
                    <td>
                                <div>env:ONEVIEW_PASSWORD</div>
                    </td>
                <td>
                        <div>OneView authentication password.</div>
                        <div>If the value is not specified in the inventory configuration, the value of environment variable <code>ONEVIEW_PASSWORD</code> will be used instead.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>plugin</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 1.0.0</div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>unbelievable.hpe.oneview</li>
                        </ul>
                </td>
                    <td>
                    </td>
                <td>
                        <div>The name of this plugin, it should always be set to <code>um.hpe.oneview</code> for this plugin to recognize it as it&#x27;s own.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>preferred_ip</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 1.0.0</div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>IPv4</b>&nbsp;&larr;</div></li>
                                    <li>IPv6</li>
                        </ul>
                </td>
                    <td>
                    </td>
                <td>
                        <div>Preferred source for ansible_host IP address.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>proxy</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 1.0.0</div>
                </td>
                <td>
                </td>
                    <td>
                                <div>env:ONEVIEW_PROXY</div>
                    </td>
                <td>
                        <div>Proxy to use when accessing OneView API.</div>
                        <div>If the value is not specified in the inventory configuration, the value of environment variable <code>ONEVIEW_PROXY</code> will be used instead.</div>
                        <div>if requests where installed like &#x27;pip install requests[socks]&#x27;, then socks proxies are supported.</div>
                        <div>example: http://localhost:8080</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>url</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 1.0.0</div>
                </td>
                <td>
                </td>
                    <td>
                                <div>env:ONEVIEW_URL</div>
                    </td>
                <td>
                        <div>URL of OneView host.</div>
                        <div>If the value is not specified in the inventory configuration, the value of environment variable <code>ONEVIEW_URL</code> will be used instead.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>user</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 1.0.0</div>
                </td>
                <td>
                </td>
                    <td>
                                <div>env:ONEVIEW_USER</div>
                    </td>
                <td>
                        <div>OneView api authentication user.</div>
                        <div>If the value is not specified in the inventory configuration, the value of environment variable <code>ONEVIEW_USER</code> will be used instead.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>validate_certs</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 1.0.0</div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>no</li>
                                    <li><div style="color: blue"><b>yes</b>&nbsp;&larr;</div></li>
                        </ul>
                </td>
                    <td>
                                <div>env:ONEVIEW_VALIDATE_CERTS</div>
                    </td>
                <td>
                        <div>Verify SSL certificate if using HTTPS.</div>
                        <div>If the value is not specified in the inventory configuration, the value of environment variable <code>ONEVIEW_VALIDATE_CERTS</code> will be used instead.</div>
                </td>
            </tr>
    </table>
    <br/>








Status
------


Authors
~~~~~~~

- Janne K. Olesen (@jakrol)


.. hint::
    Configuration entries for each entry type have a low to high priority order. For example, a variable that is lower in the list will override a variable that is higher up.

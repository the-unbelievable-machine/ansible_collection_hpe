.. _unbelievable.hpe.ilo_security_settings_module:


**************************************
unbelievable.hpe.ilo_security_settings
**************************************

**Manage iLO Security settings**



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Manage iLO Security settings




Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>hostname</b>
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
                        <div>The hostname or IP address of the iLO server</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: name, host, server, ilo_host, ilo_server</div>
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
                        <div>The password of the iLO server</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: passwd, ilo_password</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>port</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 1.0.0</div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">443</div>
                </td>
                <td>
                        <div>Port to use when connecting to the iLO server</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: ilo_port</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>protocol</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 1.0.0</div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>http</li>
                                    <li><div style="color: blue"><b>https</b>&nbsp;&larr;</div></li>
                        </ul>
                </td>
                <td>
                        <div>Protocol to use when connecting to the iLO server</div>
                        <div>Mainly for testing / devloping.</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: ilo_protocol</div>
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
                        <div>Proxy to use when connecting to the iLO server.</div>
                        <div>if requests where installed like &#x27;pip install requests[socks]&#x27;, then socks proxies are supported.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>security_state</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                    <div style="font-style: italic; font-size: small; color: darkgreen">added in 1.0.0</div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>Production</li>
                                    <li>HighSecurity</li>
                        </ul>
                </td>
                <td>
                        <div>Security state</div>
                        <div>Currently only switching between Production &lt;--&gt; HighSecurity is allowed.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>username</b>
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
                        <div>The username of the iLO server</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: user, ilo_user</div>
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
                        <div>Verify SSL certificate if using HTTPS.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>wait_for_reset</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">60</div>
                </td>
                <td>
                        <div>Max seconds to wait for iLO reset to be completed.</div>
                        <div>0 not wait at all.</div>
                </td>
            </tr>
    </table>
    <br/>




Examples
--------

.. code-block:: yaml

    - name: Set iLO SecurityState
      unbelievable.hpe.ilo_security_settings:
          security_state: HighSecurity
          hostname: '{{ inventory_hostname }}'
          user: user
          password: secret
          delegate_to: localhost




Status
------


Authors
~~~~~~~

- Janne K. Olesen (@jakrol)

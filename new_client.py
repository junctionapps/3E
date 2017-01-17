# Copyright 2017 Junction Applications Limited
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
#  opies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import base64
from ntlm import ntlm
from suds.client import Client
from suds.transport.https import WindowsHttpAuthenticated


def new_client_xml(*args, **kwargs):
    """ Returns the xml to create a client. Currently doesn't do any of the
    child forms and remains for illustration of how one might do this """
    # probably be nice to read/build this
    # from /inetpub/xml/object/schema/write/client.xsd
    # probably best to pass the object name, and make this a generic method
    # use ''<Client_Srv...'' if wanting to save automatically

    separator = ''  # use \n for new lines if desired for human readability
    client_prefix = '<Client xmlns="http://elite.com/schemas/transaction/process/write/Client_Srv"><Initialize xmlns="http://elite.com/schemas/transaction/object/write/Client"><Add><Client>'
    attribute_prefix = '<Attributes>'
    client_attributes_list = []
    for key, value in kwargs.iteritems():       # note in python 3 iteritems() becomes items()
        client_attributes_list.append('<{k}>{v}</{k}>'.format(k=key, v=value))
    client_attributes = separator.join(client_attributes_list)
    attribute_suffix = '</Attributes>'
    client_suffix = '</Client></Add></Initialize></Client>'

    return separator.join([client_prefix, attribute_prefix, client_attributes, attribute_suffix, client_suffix])


def ntlm_auth_header(domain, user):
    """ creates a header for ntlm """
    negotiate = '{d}\\{u}'.format(d=domain, u=user)
    ntlm_auth = 'NTLM {n}'.format(n=ntlm.create_NTLM_NEGOTIATE_MESSAGE(negotiate).decode('ascii'))
    return {'Authorization': ntlm_auth}


if __name__ == '__main__':

    # use the virtual environment to set this machine's variables
    # on windows likely at the bottom of /env/Scripts/activate.bat
    # as: SET WS_DOMAIN=companydomain
    # WSDL set simlar to http://host/TE_3E_instance/WebUI/Transactionservice.asmx?wsdl

    wsdl = os.environ['WSDL']
    # URL set simlar to http://host/TE_3E_instance/WebUI/Transactionservice.asmx
    url = os.environ['URL']
    ws_domain = os.environ['WS_DOMAIN']
    ws_user = os.environ['WS_USER']
    ws_pass = os.environ['WS_PASS']

    # following seems to work in a Windows SSO iis hosted pass through authentication situation
    # does not work with Python 3
    transport = WindowsHttpAuthenticated(username=ws_user, password=ws_pass)
    ntlm_header = ntlm_auth_header(domain=ws_domain, user=ws_user)
    # Make the connection (Client being a coincidence, next line refers to SOAP Client  )
    client = Client(url=wsdl, location=url, transport=transport, headers=ntlm_header)

    # deal with the Elite xml stuff
    cli_attributes = {'DisplayName': 'New User',
                      'SortString': 'New User Sort',}
    new_client_xml = new_client_xml(**cli_attributes)

    xmlReply = client.service.ExecuteProcess(processXML=new_client_xml, returnInfo=1)
    # ideally xmlReply contains the ProcessItemId, Result, Keys etc.
    # go check the Action list for the user.

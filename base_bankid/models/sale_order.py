from odoo import models, api, _
import hashlib
import hmac
import requests
import time
import json
import socket
# from requests_pkcs12 import get, p
import requests_pkcs12


from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_sign(self):
        url = 'https://appapi2.bankid.com/rp/v6.0/auth'
        # url = 'https://appapi2.test.bankid.com/auth'
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        file = "/home/ayomir/Downloads/FPTestcert4_20230629.pem"
        password = 'qwerty123'

        # r = requests_pkcs12.post(
        #     url,
        #     pkcs12_filename="/home/ayomir/Downloads/FPTestcert4_20230629.p12",
        #     pkcs12_password="qwerty123",
        #     data={'endUserIp': ip_address}
        # )

        session = requests.Session()
        # session.verify = "/home/ayomir/Downloads/FPTestcert4_20230629.crt"
        session.cert = (file, password)
        data = {"endUserIp": ip_address}

        response = session.get(url)


        # r = requests.post(url, verify='/home/ayomir/Downloads/FPTestcert4_20230629.p12', data=json.dumps({'endUserIp': ip_address}))

        # x = requests.post(url=url, data=json.dumps({'endUserIp': ip_address}))

        print(response)

        # with self.pfx_to_pem('/home/ayomir/Downloads/FPTestcert4_20230629.pem', 'qwerty123') as cert:
        #     x = requests.post(url, cert=cert, data={})
        #     print(x)

    def pfx_to_pem(self, pfx_path, pfx_password):
        pfx = Path(pfx_path).read_bytes()
        private_key, main_cert, add_certs = load_key_and_certificates(pfx, pfx_password.encode('utf-8'), None)

        with NamedTemporaryFile(suffix='.pem') as t_pem:
            with open(t_pem.name, 'wb') as pem_file:
                pem_file.write(private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
                pem_file.write(main_cert.public_bytes(Encoding.PEM))
                for ca in add_certs:
                    pem_file.write(ca.public_bytes(Encoding.PEM))
            yield t_pem.name





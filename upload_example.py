# -*- coding: utf-8 -*-

import requests
for i in range(50000):
    reply = requests.put("http://localhost:6547/doc", data=dict(title="test"),
                        files={'file': ("file",
                        open("src/scanned_docs/scanned_docs/tests/test.odt"))})
    print reply.content

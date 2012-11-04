# -*- coding: utf-8 -*-

import requests
for i in range(5):
    reply = requests.put("http://localhost:6543/docs", data=dict(title="test"),
                        files={'file': ("file",
                        open("/tmp/sentry08.pdf"))})
    print reply.content

import ftplib
from StringIO import StringIO
from time import sleep
import requests



directory = "Storage-01"
url = 'http://localhost:6543/doc'

class CustomStringIO(StringIO):
    def __len__(self):
        return self.len


bad = []
superbad = []
while True:
    conn = ftplib.FTP("192.168.178.1", 'ftpuser')
    try:
        print conn.nlst(directory)
        for filename in conn.nlst(directory):
            if filename in superbad:
                print "Skipping", filename
                continue
            print "Start:", filename
            tmpfile = CustomStringIO()
            try:
                conn.retrbinary("RETR " + filename,tmpfile.write)
            except:
                if filename in bad:
                    superbad.append(filename)
                else:
                    bad.append(filename)
                raise
            tmpfile.seek(0)
            files = {'file': ('scan.jpg', tmpfile)}
            print "Sleeping for 10 seconds"
            sleep(1)
            if filename in bad:
                req = requests.put(url, data={"title": "Automated scan",
                    'force_detection': False}, files = files)
            else:
                req = requests.put(url, data={"title": "Automated scan"}, files = files)

            if req.status_code == 302:
                print "Success"
                conn.delete(filename)
            else:
                if filename in bad:
                    superbad.append(filename)
                else:
                    bad.append(filename)
                print "Failure"
    except Exception, e:
        print "Error:", e
    print "Sleeping for 60 seconds"
    sleep(6)
    


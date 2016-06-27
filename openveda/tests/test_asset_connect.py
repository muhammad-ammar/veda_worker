
import os
import sys
import requests
from boto.s3.connection import S3Connection


"""
Test for deliverable connection

"""

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from reporting import ErrorObject, TestReport


class AssetConnection():
    
    def __init__(self, Settings):
        self.Settings = Settings

        self.multiserver = False
        self.hotstore = False
        self.ingest = False
        self.deliver = False

        self.passed = self.test_broker()


    def test_broker(self):
        setup = self.asset_setup_test()
        # print setup
        if setup is False: return False
        ## Asset Location
        if self.Settings.S3_ASSET_STORE is False:
            if len(self.Settings.MEZZ_HOTSTORE_LOCATION) == 0:
                 self.hotstore = False
            else:
                self.hotstore = self._http_test(location=self.Settings.MEZZ_HOTSTORE_LOCATION)
        else:
            self.hotstore = self._s3_test(location=self.Settings.MEZZ_HOTSTORE_LOCATION)

        ## Ingest
        if len(self.Settings.MEZZ_INGEST_LOCATION) != 0:
            if 'http' in self.Settings.MEZZ_INGEST_LOCATION:
                self.ingest = self._http_test(location=sself.Settings.MEZZ_INGEST_LOCATION)
            else:
                self.ingest = self._s3_test(location=self.Settings.MEZZ_INGEST_LOCATION)

        ## Delivery
        if self.multiserver is False:
            self.deliver = True
            return True

        if self.Settings.S3_DELIVER is True:
            self.deliver = self._s3_test(location=self.Settings.DELIVERY_ENDPOINT)
        else:
            self.deliver = self._http_test(location=self.Settings.DELIVERY_ENDPOINT)
        return True

        if not os.path.exists(self.Settings.VEDA_WORK_DIR):
            os.mkdir(self.Settings.VEDA_WORK_DIR)


    def asset_setup_test(self):
        """
        This one's slighly more complicated -- 
        as the DELIVERY_ID and DELIVERY_PASS variables default 
        to the S3 ingest/hotstore credentials if left blank

        """
        if len(self.Settings.MEZZ_INGEST_LOCATION) > 0 and \
        len(self.Settings.MEZZ_HOTSTORE_LOCATION) == 0:
            raise ErrorObject(
                message = 'HOTSTORE/INGEST setup',
                method=self
                )

        salient_variables = [
            'S3_ACCESS_KEY_ID',
            'S3_SECRET_ACCESS_KEY',
            'MEZZ_HOTSTORE_LOCATION'
            ]
        if self.Settings.S3_ASSET_STORE is True:
            for s in salient_variables:

                if len(eval('self.Settings.' + s)) == 0:
                    raise ErrorObject(
                        method=self,
                        message=s
                        )
                    return False

        if self.Settings.DELIVERY_ID == self.Settings.S3_ACCESS_KEY_ID:
            return True

        self.multiserver = True

        salient_variables = [
            'DELIVERY_ID',
            'DELIVERY_PASS',
            'DELIVERY_ENDPOINT'
            ]

        for s in salient_variables:
            if len(eval(s)) == 0:
                """
                This just means we won't deliver, but shouldn't 
                throw an ErrorObject
                """
                return False

        return True


    def _http_test(self, location):
        if 'http' not in location:
            if os.path.exists(location):
                return True
            raise ErrorObject(
                method=self,
                message='%s : %s' % ('NOT URL', location)
                )
            return False
        try:
            s = requests.head(location)    
        except:
            raise ErrorObject(
                method=self,
                message='%s : %s' % ('NOT VALID URL', location)
                )
            return False
        if s.status_code > 399:
            raise ErrorObject(
                method=self,
                message='%s : %s' % ('URL CONN PROBLEM', location)
                )
            return False
        return True

                        

    def _s3_test(self, location):
        if self.multiserver is True:
            conn = S3Connection(self.Settings.DELIVERY_ID, self.Settings.DELIVERY_PASS)
        else:
            conn = S3Connection(self.Settings.S3_ACCESS_KEY_ID, self.Settings.S3_SECRET_ACCESS_KEY)
        try:
            bucket = conn.get_bucket(location)
        except:
            raise ErrorObject(
                method=self,
                message='%s : %s' % ('S3 BUCKET PROBLEM', location)
                )
            return False

        return True
        

def main():
    pass





if __name__ == '__main__':
    sys.exit(main())


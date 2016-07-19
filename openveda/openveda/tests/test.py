
import os
import sys
import unittest
import yaml
import subprocess


"""
Generalized Tests

"""
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
from global_vars import *
from config import OVConfig
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'ffmpeg_compiler'
        )
    )
from ffmpeg_compile import FFCompiler


class TestVariables(unittest.TestCase):

    def test_openveda_config(self):

        """
        must run from default/unconfigged yaml

        """
        CF = OVConfig(settings_yaml=DEFAULT_YAML)
        CF.run()
        settings = CF.settings_dict

        ## test for nones
        salient_variables = [
            'workdir',
            'aws_access_key',
            'aws_secret_key',
            'aws_deliver_bucket',
            'aws_storage_bucket',
            'aws_ingest_bucket',
            'val_token_url',
            'val_api_url',
            'val_client_id',
            'val_secret_key',
            'val_username',
            'val_password',
            ]
        for s in salient_variables:
            if s == 'workdir':
                self.assertTrue(settings[s] is not None)
            else:
                self.assertTrue(settings[s] is None)

        for name, entry in settings['encode_library'].iteritems():
            self.assertTrue(
                isinstance(
                    settings['encode_library'][name], 
                    dict
                    )
                )
            self.assertTrue(
                isinstance(
                    settings['encode_library'][name]['resolution'], 
                    int
                    )
                )
            self.assertTrue(
                isinstance(
                    settings['encode_library'][name]['rate_factor'], 
                    int
                    )
                )

    def test_openveda_globals(self):
        """Test Globals"""
        self.assertTrue(isinstance(TARGET_ASPECT_RATIO, float))
        self.assertTrue(os.path.exists(TEST_VIDEO_DIR))


class TestBuild(unittest.TestCase):

    def setUp(self):
        """
        Basic Class Compile test
        """
        self.settings_yaml = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__)
                ))), 
                'test_config.yaml'
                )

        CF = OVConfig(
            test=True,
            testvar='TestVariable',
            settings_yaml=self.settings_yaml
            )
        CF.run()
        self.settings = CF.settings_dict


    def tearDown(self):
        os.remove(self.settings_yaml)

    def test_config(self):
        self.assertTrue(os.path.exists(self.settings_yaml))

    def test_yaml(self):
        with open(self.settings_yaml, 'r') as stream:
            try:
                settings_dict = yaml.load(stream)
                self.assertTrue(True)
            except yaml.YAMLError as exc:
                self.assertTrue(False)

    def test_openveda_build(self):
        self.assertTrue(self.settings['testvar'] == 'TestVariable')


# @unittest.skip("FFmpeg Compile Test")
class TestFFcompile(unittest.TestCase):

    # def setUp(self):
    def test_ff(self):
        FF = FFCompiler()
        print FF.check()
        if FF.check() is False:
            FF.run()
        
        CF = OVConfig(test=True)
        CF.run()
        self.settings = CF.settings_dict
        print self.settings
        self.assertTrue(isinstance(self.settings, dict))

        compiled = self._ff()
        self.assertTrue(compiled)


    def _ff(self):

        process = subprocess.Popen(
            self.settings['ffmpeg'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            shell=True, 
            universal_newlines=True
            )
        for line in iter(process.stdout.readline, b''):
            print line
            if 'ffmpeg version' in line:
                return True
            if 'ffmpeg: command not found' in line:
                return False


def main():
    unittest.main()

if __name__ == '__main__':
    sys.exit(main())

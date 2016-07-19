
import os
import sys
import json
import yaml

"""
This will read a default yaml file and generate a config class 
based on variables within

"""
from reporting import ErrorObject

# class VEDAConfig():

    # config = None



class WorkerSetup():


    def __init__(self, **kwargs):
        self.instance_yaml = kwargs.get(
            'instance_yaml', 
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'instance_config.yaml'
                )
            )
        self.default_yaml = kwargs.get(
            'default_yaml', 
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'default_config.yaml'
                )
            )

        self.setup = kwargs.get('setup', False)


    def run(self):
        """
        Generate Settings dict
        """
        if self.setup is False and not os.path.exists(self.instance_yaml):
            self._CONFIGURE()
        elif self.setup is True:
            self._CONFIGURE()
        else:
            self._READ_SETTINGS()


    def _READ_SETTINGS(self):
        """
        Read Extant Settings or Generate New Ones
        """
        if not os.path.exists(self.instance_yaml):
            ErrorObject.print_error(
                message = 'Not Configured'
                )
            return None

        with open(self.instance_yaml, 'r') as stream:
            try:
                self.settings_dict = yaml.load(stream)

            except yaml.YAMLError as exc:
                ErrorObject.print_error(
                    message = 'Config YAML read error'
                    )

                return None


    def _CONFIGURE(self):
        """
        Prompt user for settings as needed for yaml
        """
        with open(self.default_yaml, 'r') as stream:
            try:
                config_dict = yaml.load(stream)
            except yaml.YAMLError as exc:
                ErrorObject.print_error(
                    message = 'default YAML read error'
                    )
                return None

        self.settings_dict = {}

        for j, k in config_dict.iteritems():
            sys.stdout.write('\r')
            sys.stdout.write('%s : \n' % (j))

            new_value = raw_input('%s :' % (k))

            self.settings_dict[k] = new_value
            sys.stdout.flush()

        with open(self.instance_yaml, 'w') as outfile:
            outfile.write(
                yaml.dump(
                    self.settings_dict, 
                    default_flow_style=False
                    )
                )


def main():
    """
    For example
    """
    V = WorkerSetup()
    V.run()


if __name__ == '__main__':
    sys.exit(main())












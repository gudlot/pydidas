import abc

BASE_PLUGIN = -1
INPUT_PLUGIN = 0
PROC_PLUGIN = 1
OUTPUT_PLUGIN = 2

ptype = {BASE_PLUGIN: 'Base plugin',
         INPUT_PLUGIN: 'Input plugin',
         PROC_PLUGIN: 'Processing plugin',
         OUTPUT_PLUGIN: 'Output plugin'}

class BasePlugin:
    """
    The base plugin class from which all plugins inherit.
    """
    basic_plugin = True
    plugin_type = BASE_PLUGIN
    plugin_name = 'Base plugin'
    params = []
    input_data = []
    output_data = []

    def __init__(self):
        pass

    def execute(self, *data, **kwargs):
        """
        Execute the processing step."""
        raise NotImplementedError('Execute method has not been implemented.')

    def get_class_description(self, return_list=False):
        try:
            _name = self.__name__
        except:
            _name = self.__class__.__name__
        if return_list:
            rvals = []
            rvals = [['Name', f'{self.plugin_name}\n']]
            rvals.append(['Class name', f'{_name}\n'])
            rvals.append(['Plugin type', f'{ptype[self.plugin_type]}\n'])
            rvals.append(['Plugin description', f'{self.__doc__}\n'])
            pstr = ''
            for param in self.params:
                pstr += f'\n{param}: {self.params[param]}'
            rvals.append(['Parameters', pstr[1:]])
        else:
            rvals = (f'Name: {self.plugin_name}\n'
                     f'Class name: {_name}\n'
                     f'Plugin type: {ptype[self.plugin_type]}\n\n'
                     f'Plugin description:\n{self.__doc__}\n\n'
                     'Parameters:')
            for param in self.params:
                rvals += f'\n{param}: {self.params[param]}'
        return rvals

    def set_param(self, param_name, value):
        for param in self.params:
            if param.name == param_name:
                param.set(value)

    def add_param(self, param):
        if param.name in [p.name for p in self.params]:
            raise KeyError(f'A parameter with the name {param.name} already'
                           'exists.')
        self.params.append(param)

    def get_param_names(self):
        return [p.name for p in self.params]

    def restore_defaults(self, force=False):
        if not force:
            raise NotImplementedError('Confirmation of restoring plugin defaults not yet implemented.')
        print('restore defaults')
        for p in self.params:
            p.restore_default()


class InputPlugin(BasePlugin):
    """
    The base plugin class for input plugins.
    """
    basic_plugin = True
    plugin_type = INPUT_PLUGIN

    def __init__(self):
        super().__init__()


class ProcPlugin(BasePlugin):
    """
    The base plugin class for processing plugins.
    """
    basic_plugin = True
    plugin_type = PROC_PLUGIN

    def __init__(self):
        super().__init__()


class OutputPlugin(BasePlugin):
    """
    The base class for output (file saving / plotting) plugins.
    """
    basic_plugin = True
    plugin_type = OUTPUT_PLUGIN

    def __init__(self):
        super().__init__()


class NoPlugin:
    basic_plugin = False

class PluginMeta(metaclass=abc.ABCMeta):
    ...

PluginMeta.register(InputPlugin)
PluginMeta.register(OutputPlugin)
PluginMeta.register(ProcPlugin)
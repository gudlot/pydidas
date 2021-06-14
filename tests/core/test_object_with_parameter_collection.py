import unittest

from pydidas.core import (ObjectWithParameterCollection, Parameter,
                          ParameterCollection)


class TestObjectWithParameterCollection(unittest.TestCase):

    def setUp(self):
        self._params = ParameterCollection(
            Parameter('Test0', int, default=12),
            Parameter('Test1', str, default='test str'),
            Parameter('Test2', int, default=3),
            Parameter('Test3', float, default=12))

    def tearDown(self):
        ...

    def test_creation(self):
        obj = ObjectWithParameterCollection()
        self.assertIsInstance(obj, ObjectWithParameterCollection)

    def test_add_params_with_args(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(*self._params.values())
        for index in range(4):
            self.assertEqual(obj.params[f'Test{index}'],
                             self._params.get(f'Test{index}'))

    def test_add_params_with_dict(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        for index in range(4):
            self.assertEqual(obj.params[f'Test{index}'],
                             self._params.get(f'Test{index}'))

    def test_add_params_with_kwargs(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(param1=self._params.get('Test0'),
                       param2=self._params.get('Test1'),
                       param3=self._params.get('Test2'),
                       param4=self._params.get('Test3'),
                       )
        for index in range(4):
            self.assertEqual(obj.params[f'Test{index}'],
                             self._params.get(f'Test{index}'))

    def test_add_param(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj.add_param(Parameter('Test5', float, default=-1))
        self.assertIsInstance(obj.get_param('Test5'), Parameter)

    def test_add_param_duplicate(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj.add_param(Parameter('Test5', float, default=-1))
        with self.assertRaises(KeyError):
            obj.add_param(Parameter('Test5', float, default=-1))

    def test_get_param_value(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        self.assertEqual(obj.get_param_value('Test2'), 3)

    def test_get_param_value_no_key(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        with self.assertRaises(KeyError):
            obj.get_param_value('Test5')

    def test_set_param_value(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj.set_param_value('Test2', 12)
        self.assertEqual(obj.get_param_value('Test2'), 12)

    def test_set_param_value_no_key(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        with self.assertRaises(KeyError):
            obj.set_param_value('Test5', 12)

    def test_apply_param_modulo(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj._apply_param_modulo('Test0', 10)
        self.assertEqual(obj.get_param_value('Test0'), 2)

    def test_apply_param_modulo_ii(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        obj.set_param_value('Test0', -1)
        obj._apply_param_modulo('Test0', 10)
        self.assertEqual(obj.get_param_value('Test0'), 10)

    def test_apply_param_modulo_iii(self):
        obj = ObjectWithParameterCollection()
        obj.add_params(self._params)
        with self.assertRaises(ValueError):
            obj._apply_param_modulo('Test3', 10)

if __name__ == "__main__":
    unittest.main()

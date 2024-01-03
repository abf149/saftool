# -*- coding: utf-8 -*-
import csv, os, sys, pickle, importlib.util

from contextlib import contextmanager

""" @contextmanager
def change_directory(path):
    original_path = os.getcwd()
    original_sys_path = sys.path.copy()  # Copy the original sys.path
    os.chdir(path)
    sys.path.append(path)  # Add the new directory to sys.path
    try:
        yield
    finally:
        os.chdir(original_path)
        sys.path = original_sys_path  # Restore the original sys.path

# Calculate the path
relative_path = os.path.join('..', '..', '..')
saftools_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), relative_path))

with change_directory(saftools_src_path):
    print("Current Working Directory:", os.getcwd())
    print("Python Path:", sys.path)

    # Try importing the module
    try:
        import export.export_support.modeling_backends.Accelergy as acc_
        print("Module imported successfully.")
    except ModuleNotFoundError as e:
        print("Import Error:", e)
        print("Check if the 'export' directory is a Python package and located at:", saftools_src_path) """


NAME_IDX = 0
ACTION_ENERGY_IDX = 1
ENERGY_UNIT_IDX = 2
TOTAL_AREA_IDX = 9
COMBINATIONAL_AREA_IDX = 10
CRITICAL_PATH_LENGTH_IDX = 14

default_install_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.join('..', '..', './data/primitives_ERT_ART.pkl')))

print("DEFAULT_INSTALL_PATH:",default_install_path)

class SAFPrimitives(object):
    """
    A SAF uarch primitive component estimation plug-in
    """
    # -------------------------------------------------------------------------------------
    # Interface functions, function name, input arguments, and output have to adhere
    # -------------------------------------------------------------------------------------
    def __init__(self):
        self.estimator_name =  "saf_primitives_estimator"
        self.primitives_table=[]
        #with open(acc_.getDefaultInstallPath(),'rb') as fp:
        with open(default_install_path,'rb') as fp:
            self.ERTART=pickle.load(fp)
        #with open('accelergy/data/primitives_table.csv', newline='') as csvfile: 
        #    csvreader = csv.reader(csvfile, delimiter=',')
        #    for row in csvreader:
        #        self.primitives_table.append(row)

    def category_supported(self,instance_category):
        print("self.ERTART:",self.ERTART)

        return instance_category in self.ERTART

    def interface_breakout(self,interface,energy=True):
        if energy:
            return interface['class_name'],interface['attributes'], \
                interface['action_name'],interface['arguments']
        else: #area
            return interface['class_name'],interface['attributes']

    def match_interface_to_category_ERTART(self,instance_attributes_dict,instance_category):
        print("MATCH")
        if self.category_supported(instance_category):
            print("ONE")
            cat_ERTART=self.ERTART[instance_category]
            for attribute_values_tuple in cat_ERTART:
                ERTART_=cat_ERTART[attribute_values_tuple]
                attribute_names_tuple=ERTART_['attribute_names']
                if all([str(instance_attributes_dict[attr_name])==str(attribute_values_tuple[idx]) \
                            for idx,attr_name in enumerate(attribute_names_tuple)]):
                    # Category & instance match!

                    print("RES:",{'ERT':ERTART_['ERT'],'ART':ERTART_['ART'], \
                            'names':attribute_names_tuple, 'values':attribute_values_tuple})

                    return {'ERT':ERTART_['ERT'],'ART':ERTART_['ART'], \
                            'names':attribute_names_tuple, 'values':attribute_values_tuple}
        else:
            print("TWO")
            # No class_name match
            return None

        return None

    def getERTActionEnergy(self,ERT,action):
        return float(ERT[action])

    def primitive_action_supported(self, interface):
        """
        :param interface:
        - contains four keys:
        1. class_name : string
        2. attributes: dictionary of name: value
        3. action_name: string
        4. arguments: dictionary of name: value
        :type interface: dict
        :return return the accuracy if supported, return 0 if not
        :rtype: int
        """
        print("INTERFACE:",interface)

        category, \
        attributes_dict, \
        action_name, \
        _ = self.interface_breakout(interface)

        print("CATEGORY:",category)
        print("ATTRIBUTES_DICT:",attributes_dict)
        print("ACTION_NAME:",action_name)

        instance_ERTART=self.match_interface_to_category_ERTART(attributes_dict,category)
        if instance_ERTART is None:
            print("NOT SUPPORTED")
            # Instance mismatch
            return 0
        else:
            ERT=instance_ERTART['ERT']
            if action_name in ERT:
                # Action match!
                return 0.1
            else:
                # Action mismatch.
                return 0

        return 0

    def estimate_energy(self, interface):
        """
        :param interface:
        - contains four keys:
        1. class_name : string
        2. attributes: dictionary of name: value
        3. action_name: string
        4. arguments: dictionary of name: value
       :return the estimated energy
       :rtype float
        """
        category, \
        attributes_dict, \
        action_name, \
        _ = self.interface_breakout(interface)

        if self.category_supported(category):        
            ERT=self.match_interface_to_category_ERTART(attributes_dict,category)['ERT']
            if action_name in ERT:
                return self.getERTActionEnergy(ERT,action_name)
            else:
                assert(False)
                return 0.0

        # Unsupported
        assert(False)
        return 0.0

    def primitive_area_supported(self, interface):
        """
        :param interface:
        - contains two keys:
        1. class_name : string
        2. attributes: dictionary of name: value
        :type interface: dict
        :return return the accuracy if supported, return 0 if not
        :rtype: int
        """

        print("INTERFACE:",interface)

        category, \
        attributes_dict = self.interface_breakout(interface,energy=False)

        print("CATEGORY:")
        print("ATTRIBUTES_DICT:",attributes_dict)
        #print("ACTION_NAME:",action_name)

        instance_ERTART=self.match_interface_to_category_ERTART(attributes_dict,category)
        if instance_ERTART is None:
            # Instance mismatch
            return 0
        else:
            ART=instance_ERTART['ART']
            if ART is not None:
                # Area match!
                return 0.1
            else:
                # Area mismatch.
                return 0

        return 0

    def estimate_area(self, interface):
        """
        :param interface:
        - contains two keys:
        1. class_name : string
        2. attributes: dictionary of name: value
        :type interface: dict
        :return the estimated area
        :rtype: float
        """

        category, \
        attributes_dict = self.interface_breakout(interface,energy=False)

        if self.category_supported(category):        
            return float(self.match_interface_to_category_ERTART(attributes_dict,category)['ART'])

        # Unsupported
        assert(False)
        return 0.0
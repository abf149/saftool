# -*- coding: utf-8 -*-
import csv, os, sys, pickle
import export.export_support.modeling_backends.Accelergy as acc_
#from accelergy.helper_functions import oneD_linear_interpolation

NAME_IDX = 0
ACTION_ENERGY_IDX = 1
ENERGY_UNIT_IDX = 2
TOTAL_AREA_IDX = 9
COMBINATIONAL_AREA_IDX = 10
CRITICAL_PATH_LENGTH_IDX = 14

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
        with open(acc_.getDefaultInstallPath(),'rb') as fp:
            self.ERTART=pickle.load(fp)
        #with open('accelergy/data/primitives_table.csv', newline='') as csvfile: 
        #    csvreader = csv.reader(csvfile, delimiter=',')
        #    for row in csvreader:
        #        self.primitives_table.append(row)

    def category_supported(self,instance_category):
        return instance_category in self.ERTART

    def interface_breakout(self,interface,energy=True):
        if energy:
            return interface['class_name'],interface['attributes'], \
                interface['action_name'],interface['arguments']
        else: #area
            return interface['class_name'],interface['attributes']

    def match_interface_to_category_ERTART(self,instance_attributes_dict,instance_category):
        if self.category_supported(instance_category):
            cat_ERTART=self.ERTART[instance_category]
            for attribute_values_tuple in cat_ERTART:
                ERTART_=cat_ERTART[attribute_values_tuple]
                attribute_names_tuple=ERTART_['attribute_names']
                if all([str(instance_attributes_dict[attr_name])==str(attribute_values_tuple[idx]) \
                            for idx,attr_name in enumerate(attribute_names_tuple)]):
                    # Category & instance match!
                    return {'ERT':ERTART_['ERT'],'ART':ERTART_['ART'], \
                            'names':attribute_names_tuple, 'values':attribute_values_tuple}
        else:
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
        category, \
        attributes_dict, \
        action_name, \
        _ = self.interface_breakout(interface)

        instance_ERTART=self.match_interface_to_category_ERTART(attributes_dict,category)
        if instance_ERTART is None:
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
        category, \
        attributes_dict, \
        action_name, \
        _ = self.interface_breakout(interface)

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
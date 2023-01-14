# -*- coding: utf-8 -*-
#import csv, os, sys
#from accelergy.helper_functions import oneD_linear_interpolation

class SAFPrimitives(object):
    """
    A SAF uarch primitive component estimation plug-in
    """
    # -------------------------------------------------------------------------------------
    # Interface functions, function name, input arguments, and output have to adhere
    # -------------------------------------------------------------------------------------
    def __init__(self):
        self.estimator_name =  "saf_primitives_estimator"

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
        if 'regfile' in interface['class_name']:
            return 1

        supported = 1 # dummy support everything
        if ('format_uarch' not in interface['class_name']) and ('intersect' not in interface['class_name']) and ('pgen' not in interface['class_name']) and ('md_parser' not in interface['class_name']):
            supported = 0        
        return 0.1  if supported \
                    else 0  # if not supported, accuracy is 0

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
        supported = 1 # dummy support everything
        if ('format_uarch' not in interface['class_name']) and ('intersect' not in interface['class_name']) and ('pgen' not in interface['class_name']) and ('md_parser' not in interface['class_name']):
            supported = 0
        if supported:        
            if interface['action_name'] == 'idle':
                return 0
                '''if interface["class_name"] == "SRAM" and interface["attributes"]["depth"] == 0:
                return 0 # zero depth SRAM has zero energy'''
            elif 'format_uarch' in interface['class_name']:
                return 0
            elif 'intersect' in interface['class_name']:
                if interface['attributes']['metadataformat']=='B':
                    return 1000.0*0.000283
                elif interface['attributes']['metadataformat']=='C':
                    return 18.0  
            elif 'pgen' in interface['class_name']:
                if interface['attributes']['metadataformat']=='B':
                    return 1000.0*1.8
                elif interface['attributes']['metadataformat']=='C':
                    return 0.0
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
        if 'regfile' in interface['class_name']:
            return 1

        supported = 1 # dummy support everything
        if ('format_uarch' not in interface['class_name']) and ('intersect' not in interface['class_name']) and ('pgen' not in interface['class_name']) and ('md_parser' not in interface['class_name']):
            supported = 0        
        return 0.1  if supported \
                    else 0  # if not supported, accuracy is 0

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

        supported = 1 # dummy support everything
        if ('format_uarch' not in interface['class_name']) and ('intersect' not in interface['class_name']) and ('pgen' not in interface['class_name']) and ('md_parser' not in interface['class_name']):
            supported = 0
        if supported:
            if 'format_uarch' in interface['class_name']:
                return 0.0
            elif 'intersect' in interface['class_name']:
                if interface['attributes']['metadataformat']=='B':
                    return 160.0
                elif interface['attributes']['metadataformat']=='C':
                    return 220.0
            elif 'pgen' in interface['class_name']:
                if interface['attributes']['metadataformat']=='B':
                    return 154.0
                elif interface['attributes']['metadataformat']=='C':
                    return 0.0                    
        return 0

        """if interface["class_name"] == "SRAM" and interface["attributes"]["depth"] == 0:
            return 0 # zero depth SRAM has zero area
        return 1 # dummy returns 1 for all areas"""
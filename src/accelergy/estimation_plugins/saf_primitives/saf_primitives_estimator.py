# -*- coding: utf-8 -*-
import csv, os, sys
#from accelergy.helper_functions import oneD_linear_interpolation

NAME_IDX = 0
ACTION_ENERGY_IDX = 1
ENERGY_UNIT_IDX = 2
TOTAL_AREA_IDX = 9
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
        with open('accelergy/data/primitives_table.csv', newline='') as csvfile: 
            csvreader = csv.reader(csvfile, delimiter=',')
            for row in csvreader:
                self.primitives_table.append(row)

    def find_in_table(self,baseComponentName,paramList,paramValues):
        suffix_str = "_"
        for idx in range(len(paramList)):
            suffix_str = suffix_str + paramList[idx]
            suffix_str = suffix_str + str(paramValues[paramList[idx]])
        targetComponentName=baseComponentName+suffix_str
        for row in self.primitives_table:
            if row[NAME_IDX] == targetComponentName:
                return row

        return None

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
                    baseComponentName='BidirectionalBitmaskIntersectDecoupled'
                    paramList=['metaDataWidth']
                    paramValues={'metaDataWidth':interface['attributes']['metadatawidth']}
                    targetTableRow = self.find_in_table(baseComponentName,paramList,paramValues)
                    assert(targetTableRow is not None)
                    return float(targetTableRow[ACTION_ENERGY_IDX])
                elif interface['attributes']['metadataformat']=='C':
                    baseComponentName='BidirectionalCoordinatePayloadIntersectDecoupled'
                    paramList=['metaDataWidth']
                    paramValues={'metaDataWidth':interface['attributes']['metadatawidth']}
                    targetTableRow = self.find_in_table(baseComponentName,paramList,paramValues)
                    assert(targetTableRow is not None)
                    return float(targetTableRow[ACTION_ENERGY_IDX])
            elif 'pgen' in interface['class_name']:
                if interface['attributes']['metadataformat']=='B':
                    baseComponentName='ParallelDec2PriorityEncoderRegistered'
                    paramList=['inputbits']
                    paramValues={'inputbits':128}#interface['attributes']['metadatawidth']}
                    targetTableRowPenc = self.find_in_table(baseComponentName,paramList,paramValues)
                    PencAreaAmortizationOverMemories=0.5
                    baseComponentName='ParallelPrefixSumRegistered'
                    PfsumAreaAmortizationOverCycles=1.0/paramValues['inputbits']
                    paramList=['bitwidth']
                    paramValues={'bitwidth':128}#interface['attributes']['metadatawidth']}
                    targetTableRowPfsum = self.find_in_table(baseComponentName,paramList,paramValues)                    
                    assert((targetTableRowPenc is not None) and (targetTableRowPfsum is not None))
                    return float(targetTableRowPenc[ACTION_ENERGY_IDX]*PencAreaAmortizationOverMemories + \
                                 targetTableRowPfsum[ACTION_ENERGY_IDX]*PfsumAreaAmortizationOverCycles)     
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
                    baseComponentName='BidirectionalBitmaskIntersectDecoupled'
                    paramList=['metaDataWidth']
                    paramValues={'metaDataWidth':128} #interface['attributes']['metadatawidth']}
                    targetTableRow = self.find_in_table(baseComponentName,paramList,paramValues)
                    assert(targetTableRow is not None)
                    return float(targetTableRow[TOTAL_AREA_IDX])
                elif interface['attributes']['metadataformat']=='C':
                    baseComponentName='BidirectionalCoordinatePayloadIntersectDecoupled'
                    paramList=['metaDataWidth']
                    paramValues={'metaDataWidth':interface['attributes']['metadatawidth']}
                    targetTableRow = self.find_in_table(baseComponentName,paramList,paramValues)
                    assert(targetTableRow is not None)
                    return float(targetTableRow[TOTAL_AREA_IDX])
            elif 'pgen' in interface['class_name']:
                if interface['attributes']['metadataformat']=='B':
                    baseComponentName='ParallelDec2PriorityEncoderRegistered'
                    paramList=['inputbits']
                    paramValues={'inputbits':128}#interface['attributes']['metadatawidth']}
                    targetTableRowPenc = self.find_in_table(baseComponentName,paramList,paramValues)
                    PencAreaAmortizationOverMemories=0.5
                    baseComponentName='ParallelPrefixSumRegistered'
                    PfsumAreaAmortizationOverCycles=1.0 #/paramValues['inputbits']
                    paramList=['bitwidth']
                    paramValues={'bitwidth':128}#interface['attributes']['metadatawidth']}
                    targetTableRowPfsum = self.find_in_table(baseComponentName,paramList,paramValues)                    
                    assert((targetTableRowPenc is not None) and (targetTableRowPfsum is not None))
                    return float(targetTableRowPenc[TOTAL_AREA_IDX]*PencAreaAmortizationOverMemories + \
                                 targetTableRowPfsum[TOTAL_AREA_IDX]*PfsumAreaAmortizationOverCycles)                    
                    #return 154.0
                elif interface['attributes']['metadataformat']=='C':
                    return 0.0                    
        return 0

        """if interface["class_name"] == "SRAM" and interface["attributes"]["depth"] == 0:
            return 0 # zero depth SRAM has zero area
        return 1 # dummy returns 1 for all areas"""
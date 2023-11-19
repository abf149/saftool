'''Create microarchitecture subcategories and subcategory instances'''

from util.taxonomy.designelement import Primitive, Component, Architecture, Net, FormatType, \
                                        Topology, NetType, Port, SAF
import util.notation.model as mo_
import solver.model.build_support.scale as sc_
import solver.model.build_support.abstraction as ab_
from util.helper import info,warn,error
import sympy as sp, copy

fmt_str_convert={"UOP":"U", "RLE":"R", "C":"C","B":"B"}

class TopologyWrapper:
    def __init__(self,component_list=[],net_list=[],generator_type=None,topological_hole=True):
        self.generator_type=generator_type
        self.net_class=False
        if topological_hole:
            self.topological_hole_=True
            self.component_list=[]
            self.net_list=[]
        else:
            self.topological_hole_=False
            self.component_list=component_list
            self.net_list=net_list          
        if self.generator_type is not None:
            error("Topology does not yet support generator_type")
            assert(False)

    def topological_hole(self):
        self.topological_hole_=True
        return self

    def generator(self,generator_type):
        self.generator_type=generator_type
        return self

    def component(self,id,component):
        self.topological_hole_=False
        self.component_list.append((id,component))
        return self

    def components(self,id_component_list):
        self.topological_hole_=False
        for id,component in id_component_list:
            self.component_list.append((id,component))
        return self

    def net(self,net):
        self.topological_hole_=False
        self.net_class=False
        self.net_list.append(net)
        return self

    def nets(self,net_list_):
        self.topological_hole_=False
        self.net_list.extend(net_list_)
        return self

    def generate_topology(self,generator_type=None,generator_config_arg=None):
        if generator_type is None:
            pass
        else:
            assert(False)

    def build(self,id="TestTopology"):
        topology=[]
        if self.topological_hole_:
            topology=Topology.holeFromId(id)
        else:
            component_list=[comp.build(cid) for cid,comp in self.component_list]
            net_list=[Net.fromIdAttributes("net" + str(id), \
                                        self.net_list[idx][0], \
                                        self.net_list[idx][1], \
                                        list(self.net_list[idx][2:])) \
                                                for idx in range(len(self.net_list)) \
                    ]

            # build topology
            topology = Topology.fromIdNetlistComponentList(id,net_list,component_list)

        return topology

class PrimitiveCategory:

    def __init__(self):
        self.design_element_type="Primitive"
        self.name_="PrimitiveCategory"
        self.attributes_=[]
        self.attribute_vals=[]
        self.default_attributes_=[]
        self.port_attribute_refs=[]
        self.ports_=[]
        self.generator_type=None

        # Scale-inference-related initialization
        self.obj_id=None
        self.category_id=None
        self.scale_attributes_=[]
        self.scale_default_attributes_=[]
        self.scale_attribute_vals=[]
        self.taxonomic_instance_alias_list=[]
        self.port_thrpt_attr_dict={}
        self.port_thrpt_thresh_mode=None
        self.port_thrpt_thresh_attr_dict=None
        self.instance_to_implementations={}
        self.actions_=[]
        self.constraint_list=[]
        self.final_constraint_list=[]
        self.symbol_list=[]
        self.symbol_types_dict={}
        self.symbol_types_list=[]
        self.yield_symbol_dict={}
        self.yield_taxo_attributes=None
        self.scale_parameters=[]
        self.scale_default_parameters=[]
        self.scale_parameter_vals=[]
        self.applicable_taxo_instance_alias=None
        self.supported_instances=None
        self.area_objective=""
        self.energy_objective_dict={}
        self.uri_prefix=None
        self.final_yield_values_dict={}
        self.ART=None
        self.ERT=None
        self.characterization_metrics_model_dict={}
        self.characterization_metrics_expression_dict={}
        self.characterization_model_constraints_dict={}

    def copy(self):
        return copy.deepcopy(self)

    def name(self,name_param):
        '''
        Category name\n\n

        Arguments:\n
        - name_param -- New Primitive cat
        '''
        self.name_=name_param
        return self

    def getName(self):
        return self.name_

    def attribute(self,attr_name,attr_type,attr_default="?"):
        '''
        Add an attribute\n\n

        Arguments:\n
        - attr_name -- Primitive category attribute name\n
        - attr_type -- Primitive category attribute type ("fibertree","format","net_type","buffer","int","string","any","list(<type>)","list(*)",[<type>,type,...])
        - attr_default -- Primitive category attribute default value (can be specific value, or "?")
        '''
        if attr_default is None:
            warn("Changing",self.name_,"attribute",attr_name,"default from",attr_default,"to \'none\'")
            attr_default='none'

        self.attributes_.append((attr_name,attr_type))
        self.default_attributes_.append((attr_name,attr_default))
        self.attribute_vals=copy.deepcopy(self.attributes_)
        return self

    def set_attributes(self,val_list):
        safe_val_list=[]
        for idx,attr_val in enumerate(val_list):
            if attr_val is None:
                warn("Changing",self.name_,"new value for attribute num.", \
                     str(idx),"in list",str(val_list),"from",attr_val,"to \'none\'")
                safe_val_list.append('none')
            else:  
                safe_val_list.append(attr_val)
        self.attribute_vals=safe_val_list

    def set_attribute(self,attr_name,val,att_type=None):
        '''
        Set an attribute\n\n

        Arguments:\n
        - attr_name -- Primitive category attribute name\n
        - val -- Updated attribute value
        - att_type -- None==typical setter behavior, or fibertree, or rank_list
        '''
        if val is None:
            warn("Changing",self.name_,"attribute",attr_name,"new value from",val,"to \'none\'")
            val='none'
        if att_type is None:
            attr_names=[att[0] for att in self.attributes_]
            self.attribute_vals[attr_names.index(attr_name)]=val
        elif att_type == "fibertree":
            # - Flatten the interface formats associated with this buffer stub
            flat_rank_fmts=[]
            for dtype in val:
                flat_rank_fmts.extend([fmt_str_convert[fmt_iface['format']] for fmt_iface in val[dtype]])
            flat_rank_fmts=[FormatType.fromIdValue('format',fmt_str) for fmt_str in flat_rank_fmts]
            self.set_attribute(attr_name,flat_rank_fmts)
        elif att_type == "rank_list":
            # Assume val is a list of flattened rank formats
            self.set_attribute(attr_name,val)
        else:
            assert(False)
        return self
    
    def get_attribute(self,attr_name):
        attr_names=[att[0] for att in self.attributes_]
        return self.attribute_vals[attr_names.index(attr_name)]

    def get_attributes(self):
        return self.attributes_
    
    def get_attribute_names(self):
        return [att[0] for att in self.attributes_]

    def port_in(self,port_name,port_net_type,port_fmt,attr_reference=None):
        self.ports_.append((port_name,"in",port_net_type,port_fmt,attr_reference))
        return self

    def port_out(self,port_name,port_net_type,port_fmt,attr_reference=None):
        if port_fmt is None:
            warn("Changing",self.getName(),"port",port_name,"format from",port_fmt,"to \'none\'")
            port_fmt="none"
        self.ports_.append((port_name,"out",port_net_type,port_fmt,attr_reference))
        return self

    def generator(self,generator_type):
        self.generator_type=generator_type
        return self

    def generate_ports(self,generator_type=None,generator_config_attribute=None):
        if self.generator_type is None:
            # Ports don't contain variables and don't need to be expanded
            return self
        elif generator_type == "fibertree":
            assert(generator_config_attribute is not None)
            # generator_config_attribute is a fibertree
            ports=self.ports_
            self.ports_=[]
            idx=0
            att_names=[att[0] for att in self.attributes_]
            for fiber in self.attribute_vals[att_names.index(generator_config_attribute)]:
                # Repeat the same pattern of ports for each fiber format
                # $v = fiber format
                # $x = fiber index
                for port in ports:
                    port_name=port[0].replace("$x",str(idx))
                    port_dir=port[1]
                    port_net_type=port[2]
                    port_net_fmt=port[3].replace("$v",fiber.getValue())
                    port_attr_ref=port[4]
                    self.ports_.append((port_name,port_dir,port_net_type,port_net_fmt,port_attr_ref))
                idx+=1
        else:
            error("Unrecognized generator type in Primitive")
            assert(False)

        return self

    def buildInterface(self,net_type_id="TestNetType",format_type_id="TestFormatType"):
        iface=[]
        for port in self.ports_:
            net_type=NetType.fromIdValue(net_type_id,port[2])
            format_type=FormatType.fromIdValue(format_type_id,port[3])
            attr_names = [attr_[0] for attr_ in self.attributes_]
            if port[4] is None:
                iface.append(Port.fromIdDirectionNetTypeFormatType(port[0], port[1], net_type, format_type))
            else:
                attr_ref_idx = attr_names.index(port[4])
                assert(attr_ref_idx >= 0)
                iface.append(Port.fromIdDirectionNetTypeFormatType(port[0], port[1], net_type, format_type, attr_ref=attr_ref_idx))

        return iface

    def build(self, id):
        iface=self.buildInterface()
        prim=Primitive.fromIdCategoryAttributesInterface(id, \
                                                         self.name_, \
                                                         self.attribute_vals, \
                                                         iface)
        return prim
    
    '''Scale inference settings'''
    def scale_parameter(self,param_name,param_type,yield_=False,inherit_=False,param_default=None):
        '''
        Add a global scale parameter.\n\n

        Arguments:\n
        - param_name -- Scale parameter name\n
        - param_type -- Scale parameter type: real, categorical (provide list of values), list\n
        - param_default -- Default parameter value
        '''
        self.scale_parameters.append((param_name,param_type,yield_,inherit_))
        self.scale_default_parameters.append((param_name,param_default))
        self.scale_parameter_vals=copy.deepcopy(self.scale_parameters)

        return self

    def set_scale_parameter(self,param_name,val,param_type=None):
        if (param_type is None) or \
           (param_type == "real") or \
           (param_type == "string") or \
           (param_type == "list"):
            scale_param_names=[att[0] for att in self.scale_parameters]
            self.scale_parameter_vals[scale_param_names.index(param_name)]=val
        else:
            error("Unrecognized scale parameter type",str(param_type),also_stdout=True)
            info("Terminating.")
            assert(False)
        return self

    def get_scale_param_spec_list(self):
        return self.scale_parameters

    def get_scale_parameters_name_list(self):
        return [scale_param_tuple[0] for scale_param_tuple in self.get_scale_param_spec_list()]

    def get_scale_parameters_values_list(self):
        return self.scale_parameter_vals

    def get_scale_parameters_dict(self):
        res={}
        scale_param_vals_list=self.get_scale_parameters_values_list()
        for idx,scale_param_name in enumerate(self.get_scale_parameters_name_list()):
            res[scale_param_name]=scale_param_vals_list[idx]
        return res

    def get_scale_parameter(self,param_name):
        scale_param_names=[att[0] for att in self.scale_parameters]
        return self.scale_parameter_vals[scale_param_names.index(param_name)]

    def is_scale_parameter_inherited(self,param_name):
        scale_param_names=[att[0] for att in self.scale_parameters]
        return self.scale_parameters[scale_param_names.index(param_name)][3]

    def is_scale_parameter(self,param_name):
        scale_param_names=[att[0] for att in self.scale_parameters]
        return param_name in scale_param_names

    def is_taxo_attribute(self,attr_name):
        return attr_name in [attr_tuple[0] for attr_tuple in self.attributes_]

    #def inherit_scale_parameter(self,param_name,param_type=None):
    #    return self.set_scale_parameter(param_name,param_name,param_type)

    def scale_attribute(self,attr_name,attr_type,solution=False,attr_default="?"):
        '''
        Add a global scale inference attribute\n\n

        Arguments:\n
        - attr_name -- Scale inference attribute name\n
        - attr_type -- Scale inference attribute type - most likely list of allowed values
        - attr_default -- Primitive category attribute default value
        '''
        self.scale_attributes_.append((attr_name,attr_type,solution))
        self.scale_default_attributes_.append((attr_name,attr_default))
        self.scale_attribute_vals=copy.deepcopy(self.scale_attributes_)

        if attr_type=="int":
            self.symbol_types_dict[attr_name]="int"
        elif attr_type=="float":
            self.symbol_types_dict[attr_name]="float"
        else:
            assert(False)

        return self

    def yield_scale_attribute(self,attr_name,attr_type,attr_default="?"):
        '''
        Add a global scale inference attribute which should comprise part of the solution to scale inference
        '''
        self.scale_attribute(attr_name,attr_type,solution=True,attr_default=attr_default)

    def yield_port_throughput_thresholds(self,port_attr_dict=None):
        self.port_thrpt_thresh_mode="yield"
        self.port_thrpt_thresh_attr_dict=port_attr_dict

        return self

    def yield_taxonomic_attributes(self,attrs_=None):
        if attrs_ is None:
            self.yield_taxo_attributes="all"
        else:
            self.yield_taxo_attributes=attrs_
        return self

    def set_scale_attribute(self,attr_name,val,att_type=None):
        '''
        Set a scale inference attribute\n\n

        Arguments:\n
        - attr_name -- Scale inference attribute name\n
        - val -- Updated attribute value
        - att_type -- TBD
        '''
        if att_type is None:
            scale_attr_names=[att[0] for att in self.scale_attributes_]
            self.scale_attribute_vals[scale_attr_names.index(attr_name)]=val
        
        '''
        elif att_type == "fibertree":
            # - Flatten the interface formats associated with this buffer stub
            flat_rank_fmts=[]
            for dtype in val:
                flat_rank_fmts.extend([fmt_str_convert[fmt_iface['format']] for fmt_iface in val[dtype]])
            flat_rank_fmts=[FormatType.fromIdValue('format',fmt_str) for fmt_str in flat_rank_fmts]
            self.set_attribute(attr_name,flat_rank_fmts)
        elif att_type == "rank_list":
            # Assume val is a list of flattened rank formats
            self.set_attribute(attr_name,val)
        else:
            assert(False)
        return self
        '''

        return self

    def taxonomic_instance_alias(self,instance_list,alias_):
        '''Define a convenient alias for referencing a taxonomic supported instance'''
        self.taxonomic_instance_alias_list.append({"instance_list":instance_list,"alias":alias_})
        self.instance_to_implementations[alias_]=[]
        return self

    def require_port_throughput_attributes(self,port_name,thrpt_attr_list=sc_.sym_suffixes):
        '''
        Require that information about the specified port throughput attributes be available
        at the specified port.\n\n

        Arguments:\n
        - port_name -- Port for which to require specified throughput attributes
        - thrpt_attr_list -- List of throughput attributes required at port
        '''
        self.port_thrpt_attr_dict[port_name]=thrpt_attr_list
        return self

    '''Component scale inference methods'''
    def action(self,name_,args_=[]):
        '''
        Add a modeling action against this primitive component.\n\n

        Arguments:\n
        - name_ -- The action name.\n
        - args_ -- Action arguments spec: [("<arg_name>","type",<default>),...]\n\n

            type can be categorical (a list of allowed values), numerical, or string\n\n
        '''

        self.actions_.append((name_,args_))
        return self

    def getActions(self):
        return self.actions_

    def add_implementation(self,name,taxonomic_instance,energy_objective,area_objective,attributes=[],constraints=[], \
                           attr_range_specs=[], attr_combo_specs=[], constraints_from_characterization_models=[]):
        self.instance_to_implementations[taxonomic_instance].append({
            "name":name,
            "taxonomic_instance":taxonomic_instance,
            "attributes":attributes,
            "constraints":constraints,
            "attr_range_specs":attr_range_specs,
            "attr_combo_specs":attr_combo_specs,
            "energy_objective":energy_objective,
            "area_objective":area_objective,
            "constraints_from_characterization_models":constraints_from_characterization_models
        })
        return self



    def register_supported_instances(self,insts):
        self.supported_instances=insts
        return self

    def find_applicable_taxo_instance(self):
        for inst_name in self.supported_instances:
            inst_attrs=self.supported_instances[inst_name]
            all_match=True
            for inst_attr,attr_ in zip(inst_attrs,self.attribute_vals):
                if type(attr_).__name__!='str':
                    if type(attr_).__name__!= 'list':
                        if attr_.getValue() != inst_attr:
                            all_match=False
                else:
                    if attr_ != inst_attr:
                        all_match=False

            if all_match:
                return inst_name

        # Should be a match
        assert(False)

    def get_applicable_taxo_instance(self):
        return self.applicable_taxo_instance_alias

    def find_applicable_taxo_instance_alias(self):
        inst_name=self.find_applicable_taxo_instance()
        for alias_ in self.taxonomic_instance_alias_list:
            if inst_name in alias_["instance_list"]:
                self.applicable_taxo_instance_alias=alias_["alias"]
                return

        # Should be a match
        assert(False)

    def set_uri_prefix(self,uri_prefix):
        self.uri_prefix=uri_prefix
        return self

    def from_taxo_obj(self,obj,param_vals={}):
        '''
        Instantiate new model instance from a taxonomic object of corresponding category,
        i.e. pass in a MetadataParser taxonomic object to construct a MetadataParser model.
        '''
        for idx,val in enumerate(obj.getAttributes()):
            self.attribute_vals[idx]=val
        self.obj_id=obj.getId()
        self.category_id=obj.getCategory()

        # Match attributes to a corresponding taxonomic instance alias
        self.find_applicable_taxo_instance_alias()
        return self

    def get_category(self):
        return self.category_id

    def get_taxo_instances(self):
        #   TODO: handle multiple-implementation scenario correctly
        return [taxo_instance for taxo_instance in self.instance_to_implementations]

    '''Routines to build characterization metrics models'''
    def register_characterization_metrics_model(self,characterization_metrics_model,id_=None):
        '''
        Arguments:\n
        - characterization_metrics_model -- CharacterizationMetricModel instance capturing energy/area relationship of some
        characterized RTL\n
        - id_ = None - metrics model ID; if None, id_ is the function id (.getFunctionId()) of the model
        '''
        if id_ is None:
            id_=characterization_metrics_model.getFunctionId()
        self.characterization_metrics_model_dict[id_]=characterization_metrics_model
        return self

    def get_characterization_metrics_model_dict(self):
        return self.characterization_metrics_model_dict

    def get_characterization_metrics_model_id_list(self):
        return list(self.get_characterization_metrics_model_dict().keys())

    def get_characterization_metrics_model_by_id(self,id_):
        return self.get_characterization_metrics_model_dict()[id_]

    def build_characterization_metrics_model(self,id_,char_metrics_model,uri_prefix=""):

        char_metrics_model.parentComponentUri(uri_prefix) \
        .inheritParameters(self.get_scale_parameters_dict()) \
        .buildSymbolMap() \
        .buildSymList() \
        .buildCharacterizationTableView() \
        .buildSupportedConfigurations() \
        .buildSupportedSymbolValuesConstraints() \
        .buildSupportedSymbolValueCombosConstraints() \
        .buildRowEnergyMetricExpressionIfDerivedFromPower() \
        .buildRowEnergyLambda() \
        .buildRowAreaLambda() \
        .buildEnergyAreaLatencyTable() \
        .buildEnergyAreaMetricModels()
        return self

    def get_metrics_model_expressions_dict(self):
        return self.characterization_metrics_expression_dict

    def get_energy_metrics_model_expressions_dict(self):
        dct=self.get_metrics_model_expressions_dict()
        return {id_:dct[id_]['energy'] for id_ in dct}

    def get_area_metrics_model_expressions_dict(self):
        dct=self.get_metrics_model_expressions_dict()
        return {id_:dct[id_]['area'] for id_ in dct}

    def get_metrics_model_expressions_dict_by_id(self,id_):
        return self.get_metrics_model_expressions_dict()[id_]

    def get_characterization_model_constraints_dict(self):
        return self.characterization_model_constraints_dict

    def get_characterization_model_constraints_dict_by_id(self,id_):
        return self.get_characterization_model_constraints_dict()[id_]

    def get_characterization_model_sym_supp_vals_by_id(self,id_):
        return self.get_characterization_model_constraints_dict_by_id(id_)["values"]

    def get_characterization_model_sym_val_combos_by_id(self,id_):
        return self.get_characterization_model_constraints_dict_by_id(id_)["combos"]

    def get_characterization_model_unified_constraints_list_by_id(self,id_):
        return self.get_characterization_model_constraints_dict_by_id(id_)["values_combos"]

    def build_characterization_metrics_model_expressions(self,id_,char_metrics_model,uri_prefix=""):
        # Build objective expressions
        energy_metric_expression=char_metrics_model.getEnergyMetricModelExpression()
        area_metric_expression=char_metrics_model.getAreaMetricModelExpression()
        self.characterization_metrics_expression_dict[id_]={
            'energy':energy_metric_expression,
            'area':area_metric_expression
        }

        # Build supported symbol values constraints/combos
        self.characterization_model_constraints_dict[id_] = {
            "values":char_metrics_model.getSupportedSymbolValuesConstraints(),
            "combos":char_metrics_model.getSupportedSymbolValueCombosConstraints()
        }
        self.characterization_model_constraints_dict[id_]["values_combos"] = \
            self.characterization_model_constraints_dict[id_]["values"] + \
                self.characterization_model_constraints_dict[id_]["combos"]
        return self

    def build_characterization_metrics_models(self,uri_prefix=""):
        for char_metrics_model_id in self.get_characterization_metrics_model_id_list():
            char_metrics_model=self.get_characterization_metrics_model_dict()[char_metrics_model_id]
            self.build_characterization_metrics_model(char_metrics_model_id, \
                                                      char_metrics_model, \
                                                      uri_prefix=uri_prefix)
            self.build_characterization_metrics_model_expressions(char_metrics_model_id, \
                                                                  char_metrics_model, \
                                                                  uri_prefix=uri_prefix)
        return self

    '''Routines to build symbols'''
    def build_symbols_for_port_attributes(self,uri_prefix=""):
        '''Build mathematical symbols representing port throughput attributes'''
        return [ab_.uri(uri_prefix,port_name)+"_"+attr_ \
            for port_name in self.port_thrpt_attr_dict for attr_ in self.port_thrpt_attr_dict[port_name]], \
               ["float" \
            for port_name in self.port_thrpt_attr_dict for attr_ in self.port_thrpt_attr_dict[port_name]]

    def build_symbols_for_port_threshold_attributes(self,uri_prefix=""):
        syms=[]
        sym_types=[]

        if self.port_thrpt_thresh_mode is not None:
            if self.port_thrpt_thresh_attr_dict is None:
                syms.extend([ab_.uri(uri_prefix,port_name)+"_"+attr_+"_thresh"\
                    for port_name in self.port_thrpt_attr_dict for attr_ in self.port_thrpt_attr_dict[port_name]])
            
                sym_types.extend(["int"\
                    for port_name in self.port_thrpt_attr_dict for _ in self.port_thrpt_attr_dict[port_name]])
            else:
                #new_syms=[]
                #new_sym_types=[]

                for port_name in self.port_thrpt_thresh_attr_dict:
                    for attr_ in self.port_thrpt_thresh_attr_dict[port_name]:
                        syms.append(ab_.uri(uri_prefix,port_name)+"_"+attr_+"_thresh")
                        sym_types.append("int")

        return syms,sym_types     

    '''Routines to build yield lists'''

    def build_yields_for_scale_parameters(self,uri_prefix=""):
        yield_symbol_dict_updates={}

        for idx,scl_param in enumerate(self.scale_parameters):
            yield_=scl_param[2]
            if yield_:
                param_name=scl_param[0]
                param_val=self.scale_parameter_vals[idx]
                yield_symbol_dict_updates[param_name]=(param_val,"val")
            
        return yield_symbol_dict_updates

    def build_yields_for_taxonomic_attributes(self,uri_prefix=""):
        yield_symbol_dict_updates={}

        '''Build yield symbols for taxonomic attributes'''
        if self.yield_taxo_attributes=="all":
            # yield all taxonomic attributes
            for idx,attr_ in enumerate(self.attributes_):
                val=self.attribute_vals[idx]
                if not isinstance(val,FormatType):
                    yield_symbol_dict_updates[attr_[0]]=(val,"val")
                    #self.yield_symbol_dict[attr_[0]]=(val,"val")
                else:
                    yield_symbol_dict_updates[attr_[0]]=(val.getValue(),"val")
                    #self.yield_symbol_dict[attr_[0]]=(val.getValue(),"val")
        else:
            if "include" in self.yield_taxo_attributes:
                attrs_include=self.yield_taxo_attributes["include"]
                # yield some taxonomic attributes
                if type(attrs_include[0]).__name__ == 'int':
                    # by index
                    for idx in attrs_include:
                        val=self.attribute_vals[idx]
                        if not isinstance(val,FormatType):
                            yield_symbol_dict_updates[self.attributes_[idx][0]]=(val,"val")
                            #self.yield_symbol_dict[self.attributes_[idx][0]]=(val,"val")
                        else:
                            yield_symbol_dict_updates[self.attributes_[idx][0]]=(val.getValue(),"val")
                            #self.yield_symbol_dict[self.attributes_[idx][0]]=(val.getValue(),"val")
                elif type(attrs_include[0]).__name__ == 'str':
                    # by name
                    for idx,attr_ in enumerate(self.attributes_):
                        if attr_ in attrs_include:
                            val=self.attribute_vals[idx]
                            if not isinstance(val,FormatType):
                                yield_symbol_dict_updates[attr_[0]]=(val,"val")
                                #self.yield_symbol_dict[attr_[0]]=(val,"val")
                            else:
                                yield_symbol_dict_updates[attr_[0]]=(val.getValue(),"val")
                                #self.yield_symbol_dict[attr_[0]]=(val.getValue(),"val")
            elif "exclude" in self.yield_taxo_attributes:
                attrs_exclude=self.yield_taxo_attributes["exclude"]
                # yield some taxonomic attributes
                if type(attrs_exclude[0]).__name__ == 'int':
                    # by index
                    for idx,attr_ in enumerate(self.attributes_):
                        if idx not in attrs_exclude:
                            val=self.attribute_vals[idx]
                            if not isinstance(val,FormatType):
                                yield_symbol_dict_updates[attr_[0]]=(val,"val")
                                #self.yield_symbol_dict[attr_[0]]=(val,"val")
                            else:
                                yield_symbol_dict_updates[attr_[0]]=(val.getValue(),"val")
                                #self.yield_symbol_dict[attr_[0]]=(val.getValue(),"val")
                elif type(attrs_exclude[0]).__name__ == 'str':
                    # by name
                    for idx,attr_ in enumerate(self.attributes_):
                        if attr_ not in attrs_exclude:
                            val=self.attribute_vals[idx]
                            if not isinstance(val,FormatType):
                                yield_symbol_dict_updates[attr_[0]]=(val,"val")
                                #self.yield_symbol_dict[attr_[0]]=(val,"val")
                            else:
                                yield_symbol_dict_updates[attr_[0]]=(val.getValue(),"val")
                                #self.yield_symbol_dict[attr_[0]]=(val.getValue(),"val")

        return yield_symbol_dict_updates

    def build_yields_for_port_threshold_attributes(self,uri_prefix=""):
        yield_symbol_dict_updates={}

        if (self.port_thrpt_thresh_mode is not None) and (self.port_thrpt_thresh_mode=="yield"):
            # - Yield port throughput threshold attributes, if required
            if self.port_thrpt_thresh_attr_dict is None:
                for port_name in self.port_thrpt_attr_dict:
                    for attr_ in self.port_thrpt_attr_dict[port_name]:
                        yield_symbol_dict_updates[port_name+"_"+attr_+"_thresh"]= \
                            (ab_.uri(uri_prefix,port_name)+"_"+attr_+"_thresh","sym")
            else:
                for port_name in self.port_thrpt_thresh_attr_dict:
                    for attr_ in self.port_thrpt_thresh_attr_dict[port_name]:
                        yield_symbol_dict_updates[port_name+"_"+attr_+"_thresh"]= \
                            (ab_.uri(uri_prefix,port_name)+"_"+attr_+"_thresh","sym")
                        
        return yield_symbol_dict_updates

    def get_superset_yields(self,uri_prefix=""):
        superset_yield_symbols={}
        superset_yield_symbols.update(self.build_yields_for_scale_parameters(uri_prefix))
        superset_yield_symbols.update(self.build_yields_for_taxonomic_attributes(uri_prefix))
        superset_yield_symbols.update(self.build_yields_for_port_threshold_attributes(uri_prefix))
        # TODO: implementation-specific yields
        return superset_yield_symbols


    def build_symbols(self,uri_prefix=""):

        # Top-level attributes - TODO
        # Port attributes
        pa_syms,pa_types=self.build_symbols_for_port_attributes(uri_prefix)
        self.symbol_list.extend(pa_syms)
        self.symbol_types_list.extend(pa_types)

        self.yield_symbol_dict.update(self.build_yields_for_scale_parameters(uri_prefix))

        # - Yield taxonomic attributes, if required
        self.yield_symbol_dict.update(self.build_yields_for_taxonomic_attributes(uri_prefix))

        # - Port throughput threshold attributes, if required
        pa_thr_syms,pa_thr_types=self.build_symbols_for_port_threshold_attributes(uri_prefix)
        self.symbol_list.extend(pa_thr_syms)
        self.symbol_types_list.extend(pa_thr_types)
        self.yield_symbol_dict.update(self.build_yields_for_port_threshold_attributes(uri_prefix))

        # Top-level params
        #self.symbol_list.extend( \
        #    [ab_.uri(uri_prefix,param[0]) for param in self.scale_parameters]
        #)

        # Implementation attributes
        #   TODO: handle multiple-implementation scenario correctly
        args={"port_thrpt_attrs":self.port_thrpt_attr_dict}
        self.symbol_list.extend( \
            [expr_ \
                for impl_ in self.instance_to_implementations[self.applicable_taxo_instance_alias] \
                    for attr_ in impl_["attributes"] \
                        for expr_ in mo_.evalAttributeExpression(attr_,uri_prefix,args=args)] \
        )

        self.symbol_types_list.extend(["int" \
                for impl_ in self.instance_to_implementations[self.applicable_taxo_instance_alias] \
                    for attr_ in impl_["attributes"] \
                        for expr_ in mo_.evalAttributeExpression(attr_,uri_prefix,args=args)])

        return self

    def build_constraints(self,uri_prefix=""):

        # Port throughput threshold attributes, if required
        if self.port_thrpt_thresh_mode is not None:
            if self.port_thrpt_thresh_attr_dict is None:
                self.final_constraint_list.extend([ \
                    ab_.uri(uri_prefix,port_name)+"_"+attr_+"_thresh >= " \
                        + ab_.uri(uri_prefix,port_name)+"_"+attr_ \
                    for port_name in self.port_thrpt_attr_dict \
                        for attr_ in self.port_thrpt_attr_dict[port_name]])
            else:
                new_constraints=[]

                for port_name in self.port_thrpt_thresh_attr_dict:
                    for attr_ in self.port_thrpt_thresh_attr_dict[port_name]:
                        new_constraints.append(ab_.uri(uri_prefix,port_name)+"_"+attr_+"_thresh >= " \
                                               + ab_.uri(uri_prefix,port_name)+"_"+attr_)

                self.final_constraint_list.extend(new_constraints)

        # Top-level constraints - TODO
        for cnst in self.constraint_list:
            self.final_constraint_list.extend( \
                mo_.evalConstraintExpression(cnst,uri_prefix,args={"port_thrpt_attrs":self.port_thrpt_attr_dict}) \
            )        
        # Taxonomic-instance constraints - TODO
        # Implementation-level constraints
        # - Explicit constraints
        #   TODO: handle multiple-implementation scenario correctly
        idx=0
        for impl_ in self.instance_to_implementations[self.applicable_taxo_instance_alias]:
            assert(idx==0)
            impl_constraints=impl_["constraints"]
            for cnst in impl_constraints:
                self.final_constraint_list.extend( \
                    mo_.evalConstraintExpression(cnst,uri_prefix,args={"port_thrpt_attrs":self.port_thrpt_attr_dict}) \
                )

            idx+=1
        # - Ranges of allowed values for attributes
        #   TODO: handle multiple-implementation scenario correctly
        for impl_ in self.instance_to_implementations[self.applicable_taxo_instance_alias]:
            impl_range_specs=impl_["attr_range_specs"]
            for chmm_name in impl_["constraints_from_characterization_models"]:
                impl_range_specs.extend(\
                    self.get_characterization_model_sym_supp_vals_by_id(chmm_name)
                )

            for spec_ in impl_range_specs:
                self.final_constraint_list.extend( \
                    mo_.evalAttributeRangeExpression(spec_,uri_prefix,args={"port_thrpt_attrs":self.port_thrpt_attr_dict}) \
                )

        # - Allowed combinations of attribute values
        #   TODO: handle multiple-implementation scenario correctly
        for impl_ in self.instance_to_implementations[self.applicable_taxo_instance_alias]:
            impl_combo_specs=impl_["attr_combo_specs"]
            for chmm_name in impl_["constraints_from_characterization_models"]:
                impl_combo_specs.extend(\
                    self.get_characterization_model_sym_val_combos_by_id(chmm_name)
                )
            for expr_ in impl_combo_specs:
                self.final_constraint_list.extend( \
                    mo_.evalAttributeComboExpression(expr_,uri_prefix) \
                )
        return self

    def build_objective_for_taxo_instance(self,taxo_instance,uri_prefix=""):
        #TODO: support multiple implementations
        #print("taxo_instance:",taxo_instance)
        #print("uri_prefix:",uri_prefix)
        #print(self.instance_to_implementations[taxo_instance])
        #print(self.instance_to_implementations)

        if taxo_instance not in self.instance_to_implementations:
            error("Taxonomic instance",taxo_instance,"not found in model instance implementations.",also_stdout=True)
            info("- uri prefix:",uri_prefix)
            info("- supported instance aliases:",str(list(self.instance_to_implementations.keys())))
            info("Terminating.")
            assert(False)

        if len(self.instance_to_implementations[taxo_instance])==0:
            error("No model implementation(s) specified for taxonomic instance",taxo_instance,also_stdout=True)
            info("- uri prefix:",uri_prefix)
            info("- supported instance aliases:",str(list(self.instance_to_implementations.keys())))
            info("Terminating.")
            assert(False)

        energy_metrics_model_expressions_dict=self.get_energy_metrics_model_expressions_dict()
        area_metrics_model_expressions_dict=self.get_area_metrics_model_expressions_dict()
        impl_=self.instance_to_implementations[taxo_instance][0]
        energy_obj=impl_["energy_objective"]
        return {action:mo_.evalObjectiveExpression(energy_obj[action], \
                                                   uri_prefix, \
                                                   energy_metrics_model_expressions_dict) for action in energy_obj}, \
               mo_.evalObjectiveExpression(impl_["area_objective"], \
                                           uri_prefix, \
                                           area_metrics_model_expressions_dict)

    def build_objectives(self,uri_prefix=""):
        self.energy_objective_dict,self.area_objective = \
            self.build_objective_for_taxo_instance(self.applicable_taxo_instance_alias,uri_prefix)
        return self

    def build_symbols_constraints_objectives_attributes(self,uri_prefix=""):
        if self.uri_prefix is not None:
            uri_prefix=self.uri_prefix

        uri_prefix_with_self=ab_.uri(uri_prefix,self.obj_id)
        self.symbol_list=[]
        self.final_constraint_list=[]
        #self.yield_symbol_dict
        self.build_characterization_metrics_models(uri_prefix_with_self)
        self.build_symbols(uri_prefix_with_self)
        self.build_constraints(uri_prefix_with_self)
        self.build_objectives(uri_prefix_with_self)
        return self
    
    def get_constraints(self):
        return self.final_constraint_list

    def get_symbols(self):
        return self.symbol_list, self.symbol_types_list

    def get_yields(self):
        return self.yield_symbol_dict

    def get_area_objective(self):
        return self.area_objective

    def get_energy_objectives(self):
        return self.energy_objective_dict

    def get_scale_inference_problem(self):
        symbol_list,symbol_types_list=self.get_symbols()
        return symbol_list, \
               symbol_types_list, \
               self.get_constraints(), \
               self.get_energy_objectives(), \
               self.get_area_objective(), \
               self.get_yields()

    def set_analytical_modeling_attributes(self,mnilp_solution_dict):
        obj_uri=ab_.uri(self.uri_prefix,self.obj_id)
        for yield_id in self.yield_symbol_dict:
            yield_info=self.yield_symbol_dict[yield_id]
            yield_type=yield_info[1]
            if yield_type=='val':
                # Accelergy model attribute derived from taxonomic attribute
                yield_val=yield_info[0]
                self.final_yield_values_dict[yield_id]=yield_val
            else: #yield_type=='sym'     
                # Accelergy model attribute derived from scale inference solution    
                yield_uri=ab_.uri(obj_uri,yield_id)
                if yield_uri in mnilp_solution_dict:
                    self.final_yield_values_dict[yield_id]=mnilp_solution_dict[yield_uri]
                else:
                    error("--- => Solution lacks",yield_uri,"during",obj_uri,"set_analytical_modeling_attributes()")
                    info("Terminating.")
                    assert(False)

        return self

    def get_analytical_modeling_attributes(self,force_inherit=False):
        if force_inherit:
            res={}
            for yield_id in self.final_yield_values_dict:
                if ((self.is_scale_parameter(yield_id)) and \
                    (self.is_scale_parameter_inherited(yield_id))):

                    res[yield_id]=yield_id

                else:

                    res[yield_id]=self.final_yield_values_dict[yield_id]

            return res
        else:
            return self.final_yield_values_dict

    def build_ART(self):
        #TODO: support multiple implementations
        impl_=self.instance_to_implementations[self.applicable_taxo_instance_alias][0]
        area_metrics_model_expressions_dict=self.get_area_metrics_model_expressions_dict()
        area_obj_str=mo_.evalObjectiveExpression(impl_["area_objective"],"",area_metrics_model_expressions_dict)
        target_attrs=[]
        for y in self.final_yield_values_dict:
            val=self.final_yield_values_dict[y]
            try:
                float(val)
                target_attrs.append(y)
            except:
                pass

        ART_fxn=lambda model_attr_dict: \
                    sp.sympify(area_obj_str).subs({y:model_attr_dict[y] for y in target_attrs})

        self.ART=ART_fxn(self.final_yield_values_dict)
        return self

    def get_ART(self):
        return self.ART

    def build_ERT(self):
        #TODO: support multiple implementations
        impl_=self.instance_to_implementations[self.applicable_taxo_instance_alias][0]
        energy_metrics_model_expressions_dict=self.get_energy_metrics_model_expressions_dict()
        energy_obj=impl_["energy_objective"]
        energy_obj_str_dict={action:mo_.evalObjectiveExpression(energy_obj[action], \
                                                                "", \
                                                                energy_metrics_model_expressions_dict) for action in energy_obj}
        target_attrs=[]
        for y in self.final_yield_values_dict:
            val=self.final_yield_values_dict[y]
            try:
                float(val)
                target_attrs.append(y)
            except:
                pass
        ERT_fxn=lambda model_attr_dict: \
                    { \
                        action: \
                            sp.sympify(energy_obj_str_dict[action]) \
                                .subs({y:model_attr_dict[y] for y in target_attrs}) \
                                    for action in energy_obj_str_dict
                    }
        self.ERT=ERT_fxn(self.final_yield_values_dict)
        return self

    def get_ERT(self):
        return self.ERT

    def get_yield_attributes_names_and_vec(self):
        attr_names=[attr_name for attr_name in self.final_yield_values_dict]
        attr_vals=[self.final_yield_values_dict[attr_name] for attr_name in attr_names]
        return attr_names, attr_vals

class SAFCategory(PrimitiveCategory):

    def __init__(self):
        super().__init__()
        self.target_=None

    def target(self,target_str):
        self.target_=target_str
        return self

    def build(self,id=None):
        if id is None:
            # Default id: Test<category name>
            id="Test"+self.name_
        saf=SAF.fromIdCategoryAttributesTarget(id, self.name_, self.attribute_vals, self.target_)
        return saf

class ComponentCategory(PrimitiveCategory):

    def __init__(self):
        # Primitive taxonomy & scale inference notation inits
        super().__init__()
        # Component taxonomy inits
        self.topology_=TopologyWrapper(component_list=[],net_list=[],topological_hole=True)
        # Component scale inference inits
        self.sub_actions_={}
        self.sub_action_list=[]
        self.action_map_list=[]
        self.subcomponent_list=[]

    '''Component taxonomy methods'''
    def topological_hole(self):
        self.topology_=TopologyWrapper(component_list=[],net_list=[],topological_hole=True)
        return self

    def topology(self,topology_):
        self.topology_=topology_
        return self

    def from_taxo_obj(self,obj,param_vals={}):
        super().from_taxo_obj(obj,param_vals=param_vals)
        self.subcomponent_list=[subcomp.getId() for subcomp in obj.getTopology().getComponentList()]
        return self

    def build(self,id):
        iface=self.buildInterface()
        topology=self.topology_.build()
        comp=Component.fromIdCategoryAttributesInterfaceTopology(id,self.name_,self.attribute_vals,iface,topology)
        return comp

    '''Component scale inference methods'''

    def build_subaction_incremental_base(self,impl_,action_name_,sub_component,sub_action,arg_map={},uri_prefix=""):
        sub_comp_sub_action_spec_list=self.sub_actions_.setdefault(impl_,{}) \
                                                       .setdefault(action_name_,{}) \
                                                       .setdefault(sub_component,[])
        
        sub_comp_sub_action_spec_list.append({ \
                                                "sub-component-actions":{}
                                            })

        assert(sub_action not in sub_comp_sub_action_spec_list[-1]["sub-component-actions"])
        sub_comp_sub_action_spec_list[-1]["sub-component-actions"][sub_action]={"arg_map":arg_map}

        return self

    def build_subaction_incremental(self,impl_,action_name_,sub_component,sub_action,arg_map={},foralls=[],uri_prefix=""):
        if foralls is None or len(foralls)==0:
            # The sub-action definition contains no variables
            self.build_subaction_incremental_base(impl_=impl_, \
                                                  action_name_=action_name_, \
                                                  sub_component=sub_component, \
                                                  sub_action=sub_action, \
                                                  arg_map=arg_map, \
                                                  uri_prefix=uri_prefix)

        else:
            # The sub-action definition contains variables which are set by an iterator
            # ("x","param","high_impact_mdparser_indices",None)
            # ("x,v","taxo_fibertree","fibertree",("not in","param","high_impact_mdparser_indices"))
            spec=foralls[0]
            var_name_spec=spec[0]
            forall_type=spec[1]
            forall_type_arg=spec[2]
            exclude_spec=spec[3]

            include_idxs=[]
            exclude_idxs=[]

            if forall_type == "param":
                # forall_type_arg is scale parameter name
                include_idxs=self.get_scale_parameter(forall_type_arg)
            elif forall_type == "taxo_fibertree":
                # forall_type_arg is taxonomic attribute name of fibertree
                taxo_fibertree_val=self.get_attribute(forall_type_arg)
                include_idxs=list(range(len(taxo_fibertree_val)))
            else:
                error("Invalid iterator type",forall_type,also_stdout=True)
                info("Terminating.")
                assert(False)

            if exclude_spec is not None:
                exclude_type=exclude_spec[1]
                exclude_type_arg=exclude_spec[2]
                if exclude_type == "param":
                    exclude_idxs=self.get_scale_parameter(exclude_type_arg)
                elif exclude_type == "taxo_fibertree":
                    taxo_fibertree_val=self.get_attribute(exclude_type_arg)
                    exclude_idxs=list(range(len(taxo_fibertree_val)))

            final_idxs=[idx for idx in include_idxs if (idx not in exclude_idxs)]
            subcomponent_list=[sub_component.replace("$x",str(idx)) for idx in final_idxs]
            for subcomp in subcomponent_list:
                self.build_subaction_incremental_base(impl_=impl_, \
                                                    action_name_=action_name_, \
                                                    sub_component=subcomp, \
                                                    sub_action=sub_action, \
                                                    arg_map=arg_map, \
                                                    uri_prefix=uri_prefix)                

        return self

    def subaction(self,impl_,action_name_,sub_component,sub_action,arg_map={},foralls=[]):
        self.sub_action_list.append({"impl_":impl_, \
                                     "action_name_":action_name_, \
                                     "sub_component":sub_component, \
                                     "sub_action":sub_action, \
                                     "arg_map":arg_map, \
                                     "foralls":foralls})
        return self

    def arch_buffer_action_map(self,buffer_upstream_of_port,upstream_action, \
                               downstream_action,alias_dict=mo_.std_buffer_action_aliases):

        self.action_map_list.append({
            "buffer_upstream_of_port":buffer_upstream_of_port,
            "upstream_action":upstream_action,
            "downstream_action":downstream_action,
            "alias_dict":alias_dict
        })

        return self

    def build_subactions(self,uri_prefix=""):
        for sa_ in self.sub_action_list:
            self.build_subaction_incremental(sa_["impl_"], \
                                             sa_["action_name_"], \
                                             sa_["sub_component"], \
                                             sa_["sub_action"], \
                                             sa_["arg_map"], \
                                             sa_["foralls"], \
                                             uri_prefix)

        return self
    
    def get_subcomponent_list(self):
        return self.subcomponent_list
    
    def get_subaction_graph(self):
        return self.sub_actions_
    
    def get_buffer_action_graph(self):
        return self.action_map_list

    def build_symbols_constraints_objectives_attributes(self,uri_prefix=""):
        super().build_symbols_constraints_objectives_attributes(uri_prefix)
        self.build_subactions(uri_prefix)
        return self

'''
    def build_symbols_constraints_objectives_attributes(self,uri_prefix=""):
        if self.uri_prefix is not None:
            uri_prefix=self.uri_prefix

        uri_prefix_with_self=ab_.uri(uri_prefix,self.obj_id)
        self.symbol_list=[]
        self.final_constraint_list=[]
        #self.yield_symbol_dict
        self.build_symbols(uri_prefix_with_self)
        self.build_constraints(uri_prefix_with_self)
        self.build_objectives(uri_prefix_with_self)
        return self
'''

'''
    def subactions(self,impl_,action_name_,sub_actions_={}):

        Add a modeling action against this primitive component.\n\n

        Arguments:\n
        - impl_ -- The implementation which these sub-actions apply to.\n
        - action_name_ -- The action against which these sub-actions apply\n
        - sub_actions_ -- Sub-actions spec:\n\n

            {\n
                "<sub-component id>": {\n
                    "<sub-component-action>": {\n
                        "<activity-factor>":<float <= 1.0>,\n
                        "argmap":{\n
                            "<action-arg>":"<expression>",\n
                            ...\n
                        }
                    },\n
                    ...\n
                },\n
                ...\n
            }\n\n

            The expression should be in terms of the top-level action arg names.

        sub_act_dict=self.sub_actions_.setdefault(impl_,{}).setdefault(action_name_,{})
        for key_ in sub_actions_:
            sub_act_dict[key_]=sub_actions_[key_]
        return self
'''
        
class ArchitectureCategory(ComponentCategory):

    def __init__(self):
        super().__init__()
        self.topology_=None
        self.buffer_hierarchy=[]
        self.saf_list=[]
        self.name_="ArchitectureCategory" # Only one architecture category

    def attribute(self):
        error("ArchitectureCategory does not support attribute()")
        assert(False)

    def port_in(self,port_name,port_net_type,port_fmt):
        error("ArchitectureCategory does not support port_in()")
        assert(False)

    def port_out(self,port_name,port_net_type,port_fmt):
        error("ArchitectureCategory does not support port_out()")
        assert(False)

    def buffers(self,buffer_list):
        self.buffer_hierarchy=buffer_list
        return self

    def buffer(self,buffer):
        self.buffer_hierarchy.append(buffer)
        return self

    def SAF(self,id,saf_wrapper):
        self.saf_list.append((id,saf_wrapper))
        return self

    def SAFs(self,id_saf_wrapper_list):
        for id,saf_wrapper in id_saf_wrapper_list:
            self.saf_list.append((id,saf_wrapper))

        return self

    def buildSAFs(self):
        saf_list=[]
        idx=0
        for id,saf in self.saf_list:
            saf_list.append(saf.build(id))
            idx+=1
        return saf_list

    def build(self,id="TestArchitecture"):
        topology=self.topology_.build()
        saf_list=self.buildSAFs()
        arch=Architecture.fromIdSAFListTopologyBufferHierarchy(id,saf_list,topology,self.buffer_hierarchy)
        return arch
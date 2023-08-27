'''Fill gate microarchitecture (discard already-read data in-flight to next arch. level'''
from util.notation import microarchitecture as m_

'''Primitive definition'''
FillGate = m_.PrimitiveCategory().name("FillGate") \
                                     .attribute("strategy","string","pipeline_bubble") \
                                     .port_in("pos_in","pos","addr") \
                                     .generator(None)

'''Constructor'''
buildFillGate = \
    lambda strategy: FillGate.copy().set_attribute('strategy', \
                                                   strategy)

'''Supported instances'''
fill_gate_instances={ \
    "pipeline_bubble":["pipeline_bubble"], \
    "lut":["lut"]
}
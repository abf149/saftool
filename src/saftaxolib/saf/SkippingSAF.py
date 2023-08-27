import util.notation.microarchitecture as m_
import util.notation.generators.misc as mi_

SkippingSAF = m_.SAFCategory().name("skipping") \
                              .attribute("bindings",["string","int","string","int"],[None,-1,None,-1])

isSkipSAF=mi_.isCategoryLambda("format")
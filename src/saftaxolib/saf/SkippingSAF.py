import util.notation.microarchitecture as m_

SkippingSAF = m_.SAFCategory().name("skipping") \
                              .attribute("bindings",["string","int","string","int"],[None,-1,None,-1])
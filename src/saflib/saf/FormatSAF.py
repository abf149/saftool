import core.notation.microarchitecture as m_
import core.notation.generators.misc as mi_

FormatSAF = m_.SAFCategory().name("format") \
                            .attribute("fibertree",["fibertree"],[None])

isFMTSAF=mi_.isCategoryLambda("format")
from .microarchitecture import buildFormatUarch

isFMTSAF=lambda fs: fs.getCategory()=='format'

'''Format microarchitecture from SAF'''
FMTSAFtoUarch = \
    lambda fs:buildFormatUarch(fs.getTarget()+"_datatype_format_uarch",fs.getAttributes()[0])
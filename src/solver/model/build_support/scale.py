'''
Extract or synthesize key metrics for scale inference
'''
import numpy as np
from util.helper import info,warn,error

sym_suffixes=["rw","pr","cr","ww","pw","nc"]

def get_buff_md_storage_width(buffer,flat_arch):
    if 'metadata_storage_width' in flat_arch[buffer]['attributes']:
        return flat_arch[buffer]['attributes']['metadata_storage_width']
    else:
        return -1

def get_global_positional_throughput(flat_arch,buffer_hierarchy,buffer_kept_dataspace_by_buffer,buff_dags,dtype_list):
    buff_dags_T = {dtype:np.transpose(np.matrix(buff_dags[dtype])).tolist() for dtype in dtype_list}

    ll_buffers=[]
    for dtype in dtype_list:
        for jdx,val in enumerate(buff_dags_T[dtype][-1]):
            if val:
                ll_buffers.append(jdx)

    ll_buffers=[buffer_hierarchy[idx] for idx in list(set(ll_buffers))]

    def buff_thrpt(buffer,flat_arch,buffer_kept_dataspace_by_buffer):
        #datawidth
        flat_arch_buffer_attributes=flat_arch[buffer]['attributes']
        '''
        datawidth_keyword=None
        if 'data_storage_width' in flat_arch_buffer_attributes:
            datawidth_keyword='data_storage_width'
        elif 'datawidth' in flat_arch_buffer_attributes:
            datawidth_keyword='datawidth'
        else:
            error("Cannot find key for architectural buffer datawidth (tried \'datawidth\' and \'data_storage_width\')")
        '''
        datawidth=flat_arch_buffer_attributes['datawidth']
        data_storage_width=datawidth # Default data storage width is one data word
        if 'data_storage_width' in flat_arch_buffer_attributes:
            # override data storage width if available
            data_storage_width=flat_arch_buffer_attributes['data_storage_width']

        return data_storage_width/datawidth/len(buffer_kept_dataspace_by_buffer[buffer])

    gpthrpt=min([buff_thrpt(buffer,flat_arch,buffer_kept_dataspace_by_buffer) for buffer in ll_buffers])

    return gpthrpt


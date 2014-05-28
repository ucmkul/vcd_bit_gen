#!/usr/bin/env python
import re,sys
def gen_module(dict):
    output = []
    mark = 0
    fh = open('vcd_bit_gen.sv','w')
    output.append('module VCD_BIT_GEN (\n')
    output.append(');\n\ttimeunit %s;\n\ttimeprecision %s;\n\n\tinitial begin\n\t\tfork\n'%(dict['tmscale'],dict['tmscale']))
    del dict['tmscale']
    for k,v in dict.items():
        msb = int(v['size']) -1
        msb = ''if msb == 0 else '[%d : 0]'%msb
        if mark == 0:
            output.insert(1,'\toutput reg %-10s %-15s\n'%(msb,v['name']))
            mark = 1
        else:
            output.insert(1,'\toutput reg %-10s %-15s,\n'%(msb,v['name']))
		for i in v['tv']:
        if i == v['tv'][0]:
            output.append('\t\t\t//for %s/*{{{*/\n'%v['name'])
        output.append("\t\t\t#%-10s %s <= %s'b%s;\n"%(i[0],v['name'],v['size'],i[1]))
        if i == v['tv'][-1]:
            output.append('\t\t\t///*}}}*/\n')
    output.append('\t\tjoin\n\tend\nendmodule\n')
    for i in output:
        fh.write(i)
    fh.close()
def parse_file(vcd,cfg):
    sig_list = []
    data = {}
    hier = []
    time = 0
    re_time    = re.compile(r"^#(\d+)")
    re_1b_val  = re.compile(r"^([01zx])(.+)")
    re_Nb_val  = re.compile(r"^[br](\S+)\s+(.+)")
    for i in open(cfg,'r'):
        sig_list.append(i.strip())
    fh=open(vcd,'r')
    line = fh.readline()
    while line:
        line = line.strip()
        if "$timescale" in line:
            tmscale = line
            while "$end" not in line:
                line = fh.readline()
                tmscale += line
            data['tmscale'] = tmscale.split()[1]
        elif "$scope" in line:
            hier.append( line.split()[2])
        elif "$var" in line:
            type,size,code,name = line.split()[1:5]
            path = '.'.join(hier)
            if path == sig_list[0]:
                if name in sig_list or len(sig_list) == 1:
                    if code not in data.keys():
                        data[code] = {}
                    data[code]['type'] = type
                    data[code]['size'] = size
                    data[code]['path'] = path
                    data[code]['name'] = name
                    data[code]['tv'] = []
        elif  "$upscope" in line:
            hier.pop()
        elif line.startswith('#'):
            re_time_match   = re_time.match(line)
            time = int(re_time_match.group(1))
        elif line.startswith(('0', '1', 'x', 'z', 'b', 'r')):
            re_1b_val_match = re_1b_val.match(line)
            re_Nb_val_match = re_Nb_val.match(line)
            if re_Nb_val_match :
                value = re_Nb_val_match.group(1)
                code  = re_Nb_val_match.group(2)
            elif re_1b_val_match :
                value = re_1b_val_match.group(1)
                code  = re_1b_val_match.group(2)
            if data.get(code,0):
                data[code]['tv'].append((time,value))
        line = fh.readline()
    fh.close()
    return gen_module(data)
parse_file(sys.argv[1],sys.argv[2])

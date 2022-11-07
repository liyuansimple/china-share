import time
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class NokiaXml(object):
    def __init__(self, fpath=None):
        # self.filepath = fpath
        self.raml_node = ET.Element('raml')
        self.root_node = ET.SubElement(self.raml_node, 'cmData')

    def add_root(self):
        self.raml_node.attrib['version'] = '2.0'
        self.raml_node.attrib['xmlns'] = 'raml20.xsd'

        self.root_node.attrib['type'] = 'plan'
        self.root_node.attrib['scope'] = 'all'
        self.root_node.attrib['name'] = ''
        self.root_node.attrib['id'] = ''

        head_node = ET.SubElement(self.root_node, 'header')
        log_node = ET.SubElement(head_node, 'log')
        log_node.attrib['dateTime'] = get_time_string()
        log_node.attrib['action'] = 'created'
        log_node.attrib['appInfo'] = 'PlanExporter'
        log_node.text = 'UIValues are used'

    def add_comm_node(self, class_s, version_s, dist_s, opera_s='update', parameter_data=None):
        if parameter_data is None:
            parameter_data = [[], [], [], []]
        script_type = parameter_data[0]
        par_name = parameter_data[1]
        par_name2 = parameter_data[2]
        par_val = parameter_data[3]

        comm_node = ET.SubElement(self.root_node, 'managedObject')
        comm_node.attrib['class'] = class_s
        comm_node.attrib['version'] = version_s
        comm_node.attrib['distName'] = dist_s
        comm_node.attrib['operation'] = opera_s

        v1_count = len(par_val)
        if v1_count > 0:
            for i in range(v1_count):
                if script_type[i] == 1:
                    # Pkv格式
                    p = ET.SubElement(comm_node, 'p')
                    p.attrib['name'] = par_name[i]
                    #if par_val[i] != '':
                    p.text = par_val[i]
                else:
                    list_p = ET.SubElement(comm_node, 'list')
                    list_p.attrib['name'] = par_name[i]
                    val_count = len(par_val[i])
                    if script_type[i] == 2:
                        # LkPkv格式
                        for j in range(val_count):
                            p = ET.SubElement(list_p, 'p')
                            p.attrib['name'] = par_name2[i][j]
                            p.text = par_val[i][j]
                    elif script_type[i] == 3:
                        # LkPv格式
                        for j in range(val_count):
                            p = ET.SubElement(list_p, 'p')
                            p.text = par_val[i][j]
                    elif script_type[i] == 4:
                        # LkIPkv格式
                        item_p = ET.SubElement(list_p, 'item')
                        for j in range(val_count):
                            p = ET.SubElement(item_p, 'p')
                            p.attrib['name'] = par_name2[i][j]
                            p.text = par_val[i][j]
                    elif script_type[i] == 5:
                        # LkIPkvIPkv格式
                        for j in range(val_count):
                            val_count2 = len(par_val[i][j])
                            item_p = ET.SubElement(list_p, 'item')
                            for k in range(val_count2):
                                p = ET.SubElement(item_p, 'p')
                                p.attrib['name'] = par_name2[i][j][k]
                                p.text = par_val[i][j][k]

    def save_xml(self):
        first_line = "<!DOCTYPE raml SYSTEM 'raml20.dtd'>\n".encode(encoding='utf-8')
        # f = open(self.filepath, 'wb+')
        xml_write_indent(self.raml_node, symbol=' ')
        context_t = ET.tostring(self.raml_node).replace(r' />'.encode(encoding='utf-8'), r'/>'.encode(encoding='utf-8'))
        context = first_line + context_t
        # context = first_line + ET.tostring(self.raml_node, encoding='utf-8')
        # f.write(context)
        # f.close()
        return context


def get_time_string():
    time_str = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    return time_str


def xml_write_indent(elem, level=0, symbol='\t'):
    i = '\n' + level * symbol
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + symbol
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            xml_write_indent(elem, level + 1, symbol)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

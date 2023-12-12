import datetime
import time
import xml.etree.ElementTree as ET
import re
import urllib.request
from xml.sax.saxutils import escape

def removeNewLines(string):
    string = string.replace("\r", "\n")
    while "\n " in string:
        string = string.replace("\n ", "\n")
    while " \n" in string:
        string = string.replace(" \n", "\n")
    string = string.replace("\n", " ")
    if string[0:1] == " ":
        string = string[1:]
    if string[-1:] == " ":
        string = string[0:-1]
    return string

def createDatafield(tag, ind1, ind2):
    datafield = ET.Element('datafield')
    datafield.attrib['tag'] = tag
    datafield.attrib['ind1'] = ind1
    datafield.attrib['ind2'] = ind2
    return datafield

def createSubfield(code):
    subfield = ET.Element('subfield')
    subfield.attrib['code'] = code
    return subfield

def appendSubfields(datafield, subfield_list):
    for subfield in subfield_list:
        datafield.append(subfield)
    return datafield

def createLDR(sub_series):
    leader = ET.Element('leader')
    leader.text = '01435npda 2200229 i 4500'
    return leader

def create001(sub_series):
    control001 = ET.Element('controlfield')
    control001.attrib['tag'] = '001'
    try:
        unitid = sub_series.find('did').find('unitid')
        reference = unitid.attrib['identifier']
        control001.text = 'GB 3600 ' + reference
    except:
        print("No unitid found")
    return control001

def create003(sub_series):
    control003 = ET.Element('controlfield')
    control003.attrib['tag'] = '003'
    try:
        unitid = sub_series.find('did').find('unitid')
        reference = unitid.attrib['identifier']
        control003.text = 'Archival Reference Code'  
    except:
        print("No unitid found")
    return control003

def create008(sub_series):
    control008 = ET.Element('controlfield')
    control008.attrib['tag'] = '008'
    today = datetime.date.today().strftime("%y%m%d")
    date = "nuuuuuuuu"
    try:
        unitdate = sub_series.find('did').find('unitdate')
        normal = unitdate.attrib['normal']
        if "/" in normal:
            if len(normal) == 9:
                date = "i" + normal[0:4] + normal[5:9]
            else:
                pass
        else:
            if len(normal) == 4:
                date = "s" + normal + "    "
            else:
                pass
    except:
        pass
    control008.text = today + date + 'enk           0000||eng|d'
    return control008

def create024(sub_series):
    data024 = createDatafield('024', '7', ' ')
    sub_a = createSubfield('a')
    sub_2 = createSubfield('2')
    try:
        unitid = sub_series.find('did').find('unitid')
        reference = unitid.attrib['identifier']
        sub_a.text = 'GB 3600 ' + reference
        sub_2.text = 'Archival Reference Code'
        data024 = appendSubfields(data024, [sub_a, sub_2])
    except:
        print("No unitid found")
    return data024

def create040(sub_series):
    data040 = createDatafield('040', ' ',  ' ')
    sub_a = createSubfield('a')
    sub_b = createSubfield('b')
    sub_c = createSubfield('c')
    sub_a.text = 'UkSoSU'
    sub_b.text = 'eng'
    sub_c.text = 'UkSoSU'
    data040 = appendSubfields(data040, [sub_a, sub_b, sub_c])
    return data040

def create100(sub_series):
    data100 = createDatafield('100', '1', ' ')
    sub_a = createSubfield('a')
    sub_a.text = 'Russell, Ken,'
    sub_d = createSubfield('d')
    sub_d.text = '1927-2011'
    data100 = appendSubfields(data100, [sub_a, sub_d])
    return data100

def create245(sub_series):
    data245 = createDatafield('245', '1', '0')
    sub_a = createSubfield('a')
    try:
        title = sub_series.find('did').find('unittitle').text
        sub_a.text = title
        if title[0:4] in ["The ", "Une ", "Der ", "Das "]:
            sub_a.attrib['ind2'] = '4'
        elif title[0:3] in ["An ", "Le ", "La ", "Un ", "Il "]:
            sub_a.attrib['ind2'] = '3'
        elif title[0:2] in ["A "]:
            sub_a.attrib['ind2'] = '2'
    except:
        print("No title found")
    data245 = appendSubfields(data245, [sub_a])
    return data245

def create264(sub_series):
    data264 = createDatafield('264', ' ', '0')
    sub_c = createSubfield('c')
    try:
        date = sub_series.find('did').find('unitdate').text
        date = date[0:1].upper() + date[1:]
        sub_c.text = date
    except:
        pass
    data264 = appendSubfields(data264, [sub_c])
    return data264

def create300(sub_series):
    data300 = createDatafield('300', ' ', ' ')
    sub_a = createSubfield('a')
    try:
        extent = sub_series.find('did').find('physdesc').find('extent').text
        extent = extent[0:1].upper() + extent[1:]
        sub_a.text = extent
    except:
        pass
    data300 = appendSubfields(data300, [sub_a])
    return data300

def parseScopeContent(content):
    content = content.replace("\n", "")
    content = content.replace("\r", "")
    while " <" in content:
        content = content.replace(" <", "<")
    while "> " in content:
        content = content.replace("> ", ">")
    content = content.replace("</p><p>", " -- ")
    content = content.replace(":<lb />", ": ")
    content = content.replace("<lb />", " -- ")
    content = content.replace("<p>", "")
    content = content.replace("</p>", "")
    content = content.replace("<title>", " ")
    content = content.replace("</title>", " ")
    content = content.replace("<title />", "")
    content = content.replace("<li>", "")
    content = content.replace("</li>", "")
    content = content.replace(" ,", ",")
    content = content.replace(" .", ".")
    content = content.replace(" ;", ";")
    content = content.replace(" :", ":")
    content = content.replace(" ?", "?")
    content = content.replace(" !", "!")
    return content

def create505(sub_series):
    data505 = createDatafield('505', '8', ' ')
    sub_a = createSubfield('a')
    try:
        scopecontent = sub_series.find('scopecontent')
        p_list = scopecontent.findall('p')
        new_p_list = p_list[1:] ## Exclude the first paragraph. It goes in 520.
        text = ''
        for p in new_p_list:
            content = ET.tostring(p, encoding='unicode')
            content = parseScopeContent(content)
            text = text + " -- " + content
        # To remove separator from start of field
        if text[0:4] == " -- ":
            text = text[4:]
        # To remove separator from after "Detailed contents:" etc.
        while ": -- " in text:
            text = text.replace(": -- ", ": ")
        # To remove separators in the EAD xml:
        while " -- -- " in text:
            text = text.replace(" -- -- ", " -- ")
        while " -- -" in text:
            text = text.replace(" -- -", " -- ")
        while "  " in text:
            text = text.replace("  ", " ")
        sub_a.text = text
    except:
        print("Error 505")
        pass
    data505 = appendSubfields(data505, [sub_a])
    return data505

def create520(sub_series):
    data520 = createDatafield('520', '2', ' ')
    sub_a = createSubfield('a')
    try:
        scopecontent = sub_series.find('scopecontent')
        first_p = scopecontent.find('p')
        summary = ET.tostring(first_p, encoding='unicode')
        summary = parseScopeContent(summary)
        sub_a.text = summary
    except:
        print("Exception 520")
        pass
    data520 = appendSubfields(data520, [sub_a])
    return data520

def create541(sub_series):
    data541 = createDatafield('541', ' ', ' ')
    sub_c = createSubfield('c')
    sub_a = createSubfield('a')
    sub_c.text = 'Gift;'
    sub_a.text = "Ken Russell"
    data541 = appendSubfields(data541, [sub_c, sub_a])
    return data541

def create590imdb(sub_series):
    data590_list = []
    for extref in sub_series.iter('extref'):
        if "imdb.com" in extref.attrib['href']:
            data590 = createDatafield('590', ' ', ' ')
            sub_Q = createSubfield('Q')
            sub_2 = createSubfield('2')
            ## Amend extref and append
            extref.attrib["target"] = "_blank"
            extref.tag = 'a'
            extref_string = ET.tostring(extref, encoding='unicode')
            extref_string = removeNewLines(extref_string)
            sub_Q.text = extref_string
            sub_2.text = 'UkSoSU Primo VE display field'
            data590 = appendSubfields(data590, [sub_Q, sub_2])
            data590_list.append(data590)
    return data590_list

def create590hub(sub_series):
    data590 = createDatafield('590', ' ', ' ')
    sub_Q = createSubfield('Q')
    sub_2 = createSubfield('2')
    try:
        unitid = sub_series.find('did').find('unitid')
        reference = unitid.attrib['identifier']
        reference = reference.lower()
        path = "https://archiveshub.jisc.ac.uk/data/gb3600-" + reference[0:3] + "/" + reference
        link = ET.Element('a')
        link.attrib['href'] = path
        link.attrib['target'] = '_blank'
        link.text = 'Archives Hub record for this item'
        link_string = ET.tostring(link, encoding='unicode')
        sub_Q.text = link_string
        sub_2.text = 'UkSoSU Primo VE display field'
        data590 = appendSubfields(data590, [sub_Q, sub_2])
    except:
        pass
    return data590

def create590boxes(sub_series):
    data590 = createDatafield('590', ' ', ' ')
    sub_W = createSubfield('W')
    sub_2 = createSubfield('2')
    try:
        arrangement_string = ''
        arrangement = sub_series.find('arrangement')
        for p in arrangement:
            arrangement_string = ' ' + p.text
        arrangement_string = arrangement_string[1:]
        arrangement_string = removeNewLines(arrangement_string)
        sub_W.text = arrangement_string
        sub_2.text = 'UkSoSU Primo VE display field'
        data590 = appendSubfields(data590, [sub_W, sub_2])
    except:
        pass
    return data590

def getDataFromLC(lccn):
    datafield = None
    try:
        url = "https://id.loc.gov/authorities/names/" + lccn + ".marcxml.xml"
        lc = urllib.request.urlopen(url).read().decode('utf8')
        lc_root = ET.fromstring(lc)
        for el in lc_root:
            if el.tag == "{http://www.loc.gov/MARC21/slim}datafield":
                if el.attrib['tag'][0:1] == "1":
                    datafield = el
                    datafield.tag = 'datafield'
                    for subfield in datafield:
                        subfield.tag = 'subfield'
    except Exception as e:
        print(str(e))
        print(e.read())
    return datafield

def parseControlledNameViaf(viaf_link, controlled_name):
    viaf = urllib.request.urlopen(viaf_link).read().decode('utf8')
    viaf_root = ET.fromstring(viaf)
    viaf_sources = viaf_root.find('{http://viaf.org/viaf/terms#}sources')
    lccn = ''
    for source in viaf_sources:
        if source.text[0:3] == 'LC|':
            lccn = source.attrib['nsid']
            while " " in lccn:
                lccn = lccn.replace(" ", "")
    if lccn != '':
        datafield = getDataFromLC(lccn)
    else:
        datafield = parseControlledNameString(controlled_name)
    return datafield

def parseControlledNameString(controlled_name):
    # Take the string and turn it into a 100 or 110
    datafield = None # To return this if nothing of use found.
    if controlled_name.tag == "persname":
        surname = ''
        forename = ''
        dates = ''
        for el in controlled_name:
            if el.attrib['altrender'] == 'surname':
                surname = el.text
            elif el.attrib['altrender'] == 'forename':
                forename = el.text
            elif el.attrib['altrender'] == 'dates':
                dates = el.text
        if len(surname) > 0:
            if len(forename) > 0:
            ### Only create string if forename and surname exist, otherwise raise exception
                datafield = createDatafield('100', '1', ' ')
                sub_a = createSubfield('a')
                sub_a.text = surname + ', ' + forename
                if len(dates) > 0:
                    sub_a.text = sub_a.text + ","
                    sub_d = createSubfield('d')
                    sub_d.text = dates
                    datafield = appendSubfields(datafield, [sub_a, sub_d])
                else:
                    datafield = appendSubfields(datafield, [sub_a])
                    pass
            else:
                # Raise exception here
                pass
        else:
            # raise exception here
            pass
    elif controlled_name.tag == "corpname":
        for el in controlled_name:
            if el.attrib['altrender'] != 'name':
                # Raise exception here
                pass
            else:
                datafield = createDatafield('110', '2', ' ')
                sub_a = createSubfield('a')
                sub_a.text = el.text
                datafield = appendSubfields(datafield, [sub_a])
    else:
        #Raise exception here
        pass
    return datafield
               
def parseControlledName(controlled_name):
    ## Do a check if VIAF ID exists
    #print(ET.tostring(controlled_name).decode('utf8'))
    viaf_link = ''
    try:
        if 'viaf' in controlled_name.attrib['authfilenumber']:
            viaf_link = controlled_name.attrib['authfilenumber']
        else:
            pass
    except:
        pass
    ## Get string separately depending on VIAF ID existence
    if len(viaf_link) == 0:
        datafield = parseControlledNameString(controlled_name)
    else:
        datafield = parseControlledNameViaf(viaf_link, controlled_name)
        ## Check for failure of getting name string from VIAF.
        ## Get from string if so.
        if datafield is None:
            datafield = parseControlledNameString(controlled_name)
    return datafield

def create600s(sub_series):
    subject_element_list = []
    try:
        control = sub_series.find('controlaccess')
        subject_list = []
        for el in control:
            ## Only append to subject_list if not a creator.
            if 'role' in el.attrib:
                if el.attrib['role'] == 'creator':
                    pass
                else:
                    subject_list.append(el)
            else:
                subject_list.append(el)
    except:
        return subject_element_list
    for subject in subject_list:
        subject_element = parseControlledName(subject)
        if subject_element.attrib['tag'] == '100':
            subject_element.attrib['tag'] = '600'
        elif subject_element.attrib['tag'] == '110':
            subject_element.attrib['tag'] = '610'
        else:
            # Raise exception
            pass
        subject_element_list.append(subject_element)
    return subject_element_list

def create700s(sub_series):
    creators_element_list = []
    creators_list = []
    try:
        origination_list = sub_series.iter('origination')
        for origination in origination_list:
            for el in origination:
                creators_list.append(el)
        for creator in creators_list:
            creators_element = parseControlledName(creator)
            if creators_element.attrib['tag'] == '100':
                creators_element.attrib['tag'] = '700'
            elif creators_element.attrib['tag'] == '110':
                creators_element.attrib['tag'] = '710'
            else:
                # Raise exception
                pass
            creators_element_list.append(creators_element)
    except:
        # Raise exception
        pass
    return creators_element_list

def createAndAppendSubelement(record, function):
    ## Make everything into a list, even if it is already a list:
    subelement_list = []
    if isinstance(function, list):
        for el in function:
            subelement_list.append(el)
    else:
        subelement_list.append(function)
    for subelement in subelement_list:
        ## Check all elements and subelements for some text
        text = False
        for el in subelement.iter():
            if el.text != '':
                text = True
        if text:
            record.append(subelement)
    return record

def createBibXml(sub_series):
    record = ET.Element('record')
    record = createAndAppendSubelement(record, createLDR(sub_series))
    record = createAndAppendSubelement(record, create001(sub_series))
    record = createAndAppendSubelement(record, create003(sub_series))
    record = createAndAppendSubelement(record, create008(sub_series))
    record = createAndAppendSubelement(record, create024(sub_series))
    record = createAndAppendSubelement(record, create040(sub_series))
    record = createAndAppendSubelement(record, create100(sub_series))
    record = createAndAppendSubelement(record, create245(sub_series))
    record = createAndAppendSubelement(record, create264(sub_series))
    record = createAndAppendSubelement(record, create300(sub_series))
    record = createAndAppendSubelement(record, create505(sub_series))
    record = createAndAppendSubelement(record, create520(sub_series))
    record = createAndAppendSubelement(record, create541(sub_series))
    record = createAndAppendSubelement(record, create590imdb(sub_series))
    record = createAndAppendSubelement(record, create590hub(sub_series))
    record = createAndAppendSubelement(record, create590boxes(sub_series))
    record = createAndAppendSubelement(record, create600s(sub_series))
    record = createAndAppendSubelement(record, create700s(sub_series))
    return record


infile = open('gb3600-rus.xml', 'r', encoding='utf8', errors='ignore')
string = infile.read()
infile.close()
root = ET.fromstring(string)
count = 0
collection_element = ET.Element('collection')
collection_element.attrib['xmlns'] = 'http://www.loc.gov/MARC21/slim'
for series in root.iter('c01'):
    series_title = series.find('did').find('unittitle').text
    for sub_series in series.iter('c02'):
        count = count + 1
        print(count)
        bib_xml = createBibXml(sub_series)
        collection_element.append(bib_xml)
collection_tree = ET.ElementTree(collection_element)
collection_tree.write('russell-marcxml.xml', encoding='UTF-8', xml_declaration=True)
    




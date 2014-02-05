import os,sys
import urllib2
import libxml2

def get_data_node_list(host):
    rqst="http://%s/esg-search/search?facets=*&type=Dataset&limit=1&latest=true" % host
    try:
        url=urllib2.urlopen(rqst)
    except Exception, msg:
        print "unable to connect to %s"%rqst
    
    rawXML = url.read()
    formattedXML=rawXML.replace("\n","")
    doc=libxml2.parseDoc(formattedXML)
    data_node_list=[]
    for node in doc.xpathEval('/response/lst[@name="facet_counts"]/lst[@name="facet_fields"]/lst[@name="data_node"]/int'):
        data_node_list.append(node.get_properties().get_content())
    #filter out all pcmdi except for pcmdi9
    found_pcmdi9=False
    filtered_data_node_list=[]
    for data_node in data_node_list:
        if data_node=='pcmdi9.llnl.gov':
            found_pcmdi9=True
        filtered_data_node_list.append(data_node)
    if found_pcmdi9:
        for data_node in data_node_list:
            if data_node.startswith('pcmdi') and (data_node != 'pcmdi9.llnl.gov' and data_node != 'pcmdi11.llnl.gov'):
                filtered_data_node_list.remove(data_node)
    return filtered_data_node_list

def _extract_url(doc_node):
    opendap_url=None
    nodeset=doc_node.xpathEval('./arr[@name="url"]/str/text()')
    for node in nodeset:
        url = node.get_content()
        if url.endswith("OPENDAP"):
            opendap_url=url.split('|')[0]
            break
    return opendap_url

def _extract_fileID(doc_node):
    fileID=None
    nodeset=doc_node.xpathEval('./str[@name="id"]')
    if len(nodeset)==0:
        return fileID
    else:
        fileID=nodeset[0].get_content()
    return fileID 

def _make_query(query):
    return "query="+query

def query(host,query):
    filelist=[]
    try:
        rqst="http://%s/esg-search/search?type=File&latest=True&replica=False&limit=20&"%host
        rqst=rqst+_make_query(query)
        url = urllib2.urlopen(rqst)
    except Exception, msg:
        print "Unable to connect to %s"%rqst

    rawXML = url.read()
    formattedXML=rawXML.replace("\n","")
    doc=libxml2.parseDoc(formattedXML)
    for node in doc.xpathEval('/response/result/doc'):
        opendap_url=_extract_url(node)
        fileID=_extract_fileID(node)
        if fileID and opendap_url:
            filelist.append({"fileID":fileID,"url":opendap_url})
    return filelist

if __name__ == "__main__":
    print get_data_node_list("pcmdi9.llnl.gov")
    myfiles=query("pcmdi9.llnl.gov","temperature")
    print len(myfiles)
    for file in myfiles:
        print file

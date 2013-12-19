import os,sys
import urllib2
import libxml2

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
    myfiles=query("pcmdi9.llnl.gov","temperature&limit=2")
    print len(myfiles)
    for file in myfiles:
        print file, myfiles[file]

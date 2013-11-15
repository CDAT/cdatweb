import urllib2

def datasetId_to_html_list(datasetId):
    try:
        rqst="http://%s/esg-search/search?type=Aggregation&distrib=false&dataset_id=%s"
        host=datasetId.split('|')[-1]
        rqst=rqst%(host,datasetId)
        url=urllib2.urlopen(rqst)
        r=url.read()
        htmllist=[]
        lines=r.split('\n')
        for line in lines:
            if 'OPENDAP' in line:
                tokenline=line.split('OPENDAP')
                urltokens=tokenline[0].split('<str>')
                urltokens1=urltokens[1].split('|')
                html=urltokens1[0][:-5]
                htmllist.append(html)
        return ','.join(htmllist)
    except Exception, err:
        print err
        return None


if __name__=="__main__":
    datasetId="cmip5.output1.INM.inmcm4.1pctCO2.day.atmos.day.r1i1p1.v20110323|pcmdi9.llnl.gov"
    test=datasetId_to_html_list(datasetId)
    print test

import json
import requests
import argparse
import time
import math




def subscan_getter(total_contributors):
    pages =math.ceil(total_contributors/100)
    print(pages)
    #last_page_row = total_contributors%100
    headers = { 'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    contributes = []
    cur_len = 0
    for page in range(pages):
        print(page)
        datas = json.dumps({"page":page, "row":100, "fund_id":"2023-2"})
        r= requests.post(url="https://kusama.webapi.subscan.io/api/scan/parachain/contributes",data=datas, headers=headers)
        contributes.extend(json.loads(r.text)["data"]["contributes"])
        print(cur_len + len(contributes))
        #time.sleep(1)
    store_tojsonfile('subscan_response.json',contributes)



def load_jsonfile(filename):
    with open(filename) as f:
        data = json.load(f)
        return data
def store_tojsonfile(filename,data):
    with open(filename, 'w') as fw:
        json.dump(data,fw)

def compare(elem):
    return elem["block_timestamp"]



if __name__ == '__main__':

    
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', '-i', type=str, required=True )
    parser.add_argument('--total_contributors', '-tc',type=int, required=True )
    args = parser.parse_args()
    subscan_getter(args.total_contributors)
    data_from_polkadot = load_jsonfile(args.inputfile)
    data_with_memo_no_blocktime = data_from_polkadot["contributions"]
    total_raised= data_from_polkadot["total_raised"]
    paraid = data_from_polkadot["parachain_id"]
    data_with_time_no_memo = load_jsonfile('subscan_response.json')
    

    #accout2index =load_jsonfile('tmp.json')
    accout2index ={}
    for (index, obj) in enumerate(data_with_memo_no_blocktime):
         accout2index[list(obj.values())[0]]=index
    #store_tojsonfile('polkadot_tmp.json', accout2index)

    # not_polkadot =[]
    # for item in data_with_time_no_memo:
    #     if list(accout2index.keys()).count(item["who"])==0:
    #         not_polkadot.append(item["who"])
    # print(not_polkadot)

    
    # accout2index_subscan ={}
    # for (index, obj) in enumerate(data_with_time_no_memo):
    #     accout2index_subscan[list(obj.values())[2]]=index
    # store_tojsonfile('subscan_tmp.json',accout2index_subscan)

    # not_in_subscan=[]
    # for item in data_with_memo_no_blocktime:
    #     if list(accout2index_subscan.keys()).count(item["account"])==0:
    #         not_in_subscan.append(item["account"])
    # store_tojsonfile('not_in_subscan.json', not_in_subscan)
    # print(len(not_in_subscan))
    

    for item in data_with_time_no_memo:
        key = item["who"]
        extrinsicindex = item["extrinsic_index"].replace('-','')
        blocktimestamp = item["block_timestamp"]
        index =accout2index[key]
        data_with_memo_no_blocktime[index]["extrinsic_index"] = extrinsicindex
        data_with_memo_no_blocktime[index]["block_timestamp"] = blocktimestamp
    
    #print(data_with_memo_no_blocktime)
    sorted_data = sorted(data_with_memo_no_blocktime,key=lambda x: (x["block_timestamp"],x["extrinsic_index"]))
    result={"total_raised":total_raised,"contributions":sorted_data,"parachain_id": paraid}
    
    store_tojsonfile('data_with_memo_and_time.json', result)

    
   
    
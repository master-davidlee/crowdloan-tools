import json
import requests
import argparse
import time
import math
import decimal




def subscan_getter(total_contributors):
    pages =math.ceil(total_contributors/100)
    print(pages)
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

    decimal.getcontext().prec =50
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', '-i', type=str, required=True )
    parser.add_argument('--total_contributors', '-tc',type=int, required=True )
    parser.add_argument('--total_general_fund', '-tgf',type=str, required=True )
    parser.add_argument('--total_early_fund', '-tef',type=str, required=True )
    args = parser.parse_args()
    total_general_fund = args.total_general_fund
    total_earlybird_fund = args.total_early_fund
    subscan_getter(args.total_contributors)
    data_from_polkadot = load_jsonfile(args.inputfile)
    data_with_memo_no_blocktime = data_from_polkadot["contributions"]
    total_raised= data_from_polkadot["total_raised"]
    paraid = data_from_polkadot["parachain_id"]
    data_with_time_no_memo = load_jsonfile('subscan_response.json')
    

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

    sorted_data = sorted(data_with_memo_no_blocktime,key=lambda x: (x["block_timestamp"],x["extrinsic_index"]))
    
    #now calculate reward
    money_counter = 0
    early_thred = decimal.Decimal(total_raised)/decimal.Decimal(10)
    early_counter = 0
    early_distributed = 0
    general_distributed = 0
    money_distributed = decimal.Decimal(0)
    early_flag =1
    for item in sorted_data:
        general = decimal.Decimal(item["contribution"])*decimal.Decimal(total_general_fund)/decimal.Decimal(total_raised)
        early = decimal.Decimal(0)
        money_counter += int(item["contribution"])
        
        if (money_counter  > early_thred) and early_flag==1:
            early = decimal.Decimal((early_thred-money_counter+int(item["contribution"])))*decimal.Decimal(total_earlybird_fund)/early_thred
            early_counter +=1
            early_flag =0
            print("early end")
            #time.sleep(10)
        elif early_flag == 1:
            # print("not last one")
            early = decimal.Decimal(item["contribution"])*decimal.Decimal(total_earlybird_fund)/early_thred
            early_counter +=1
            # print(general,early,(general+early).quantize(decimal.Decimal('0')))
            #time.sleep(100)
        # early_distributed = early_distributed + early
        # general_distributed = general_distributed + general
        money_distributed = money_distributed + (early + general).quantize(decimal.Decimal('0'))

        #print(general,early,general+early)
        #print(general.quantize(decimal.Decimal('0')),early.quantize(decimal.Decimal('0')),(general+early).quantize(decimal.Decimal('0')))
        item["reward"]=str((general+early).quantize(decimal.Decimal('0')))
    
    # print(total_general_fund,total_earlybird_fund)
    # print(money_counter,early_thred, money_counter==int(total_raised))
    # print(early_distributed,general_distributed)
    print("distributed money",money_distributed)
    print("early bird amout ",early_counter)
    if (int(total_earlybird_fund) + int(total_general_fund)) - money_distributed  > len(sorted_data):
        print("The dust is bigger than total contributor")
    
    #build json structur and save to file
    result={"total_raised":total_raised,"contributions":sorted_data,"parachain_id": paraid}
    store_tojsonfile('data_with_memo_and_time.json', result)

    
   
    
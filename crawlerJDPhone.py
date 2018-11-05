#!/usr/bin/python
# _*_ coding: utf-8 _*_
#@author: aLuren
#Copyright(C)2018 SZ-MB-QTC

# 获取手机单品的价格
def get_price(skuid):
    url = "https://c0.3.cn/stock?skuId=" + str(skuid) + "&area=1_72_4137_0&venderId=1000004123&cat=9987,653,655&buyNum=1&choseSuitSkuIds=&extraParam={%22originid%22:%221%22}&ch=1&fqsp=0&pduid=15379228074621272760279&pdpin=&detailedAdd=null&callback=jQuery3285040"
    r = requests.get(url, verify=False)
    content = r.content.decode('GBK')
    matched = re.search(r'jQueryd+((.*))', content, re.M)
    if matched:
        data = json.loads(matched.group(1))
        price = float(data["stock"]["jdPrice"]["p"])
        return price
    return 0

# 获取手机的配置信息
def get_item(skuid, url):
    price = get_price(skuid)
    r = requests.get(url, verify=False)
    content = r.content
    root = etree.HTML(content)
    nodes = root.xpath('.//div[@class="Ptable"]/div[@class="Ptable-item"]')
    params = {"price": price, "skuid": skuid}
    for node in nodes:
        text_nodes = node.xpath('./dl')[0]
        k = ""
        v = ""
        for text_node in text_nodes:
            if text_node.tag == "dt":
                k = text_node.text
            elif text_node.tag == "dd" and "class" not in text_node.attrib:
                v = text_node.text
                params[k] = v
    return params

# 获取一个页面中的所有手机信息
def get_cellphone(page):
    url = "https://list.jd.com/list.html?cat=9987,653,655&page={}&sort=sort_rank_asc&trans=1&JL=6_0_0&ms=4#J_main".format(page)
    r = requests.get(url, verify=False)
    content = r.content.decode("utf-8")
    root = etree.HTML(content)
    cell_nodes = root.xpath('.//div[@class="p-img"]/a')
    client = pymongo.MongoClient()
    db = client[DB]
    for node in cell_nodes:
        item_url = fix_url(node.attrib["href"])
        matched = re.search('item.jd.com/(d+).html', item_url)
        skuid = int(matched.group(1))
        saved = db.items.find({"skuid": skuid}).count()
        if saved > 0:
            print(saved)
            continue
        item = get_item(skuid, item_url)
        # 结果存入MongoDB
        db.items.insert(item)

'''
client = pymongo.MongoClient()
db = client[DB]
items = db.items.find({})
result = preprocess(items)
df = pd.DataFrame(result)
df_res = df[df.cpu_brand=="骁龙（Snapdragon)"][df.battery_cap >= 3000][df.rom >= 64][df.ram >= 6][df.dual_sim == True][df.price<=1500]
print(df_res[["brand", "model", "color", "cpu_brand", "cpu_freq", "cpu_core", "cpu_model", "rom", "ram", "battery_cap", "price"]].sort_values(by="price"))
'''

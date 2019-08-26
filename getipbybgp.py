from sys import argv
import requests
from bs4 import BeautifulSoup
from IPy import IP

ip_style = 1
total_list_v4 = []
total_index_v4 = []
total_list_int_v4 = [] # just for quick sort
total_list_v6 = []
merge_list_v4 = []
total_index_v6 = []
total_list_as= []
total_num_v4 = 0
total_num_v6 = 0
total_num_as = 0


def request(url, params):
    session = requests.Session()
    proxy = {"http":"127.0.0.1:8080",
             "https":"127.0.0.1:8080"}
    proxy={}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13;",
        "Cookie" : "c=BAgiEjIyMy4xMjkuNzguNTM=--88fd68af50f69ec2d0d5c7f5eccf186273f49d06"
    }
    return session.get(url = url, params=params, headers=headers, proxies=proxy, verify=False).content


def sort_check(a,b):
    global total_list_int_v4
    if total_list_int_v4[a][0]< total_list_int_v4[b][0]:
        return True
    if total_list_int_v4[a][0]> total_list_int_v4[b][0]:
        return False
    if total_list_int_v4[a][1]< total_list_int_v4[b][1]:
        return True
    if total_list_int_v4[a][1]> total_list_int_v4[b][1]:
        return False
    return False


def quick_sort_index(b):
    """快速排序"""
    if len(b) < 2:
        return b
    # 选取基准，随便选哪个都可以，选中间的便于理解
    mid = b[len(b) // 2]
    # 定义基准值左右两个数列
    left, right = [], []
    # 从原始数组中移除基准值
    b.remove(mid)
    for item in b:
        # 大于基准值放右边
        if sort_check(item, mid):
            left.append(item)
        else:
            # 小于基准值放左边
            right.append(item)
    # 使用迭代进行比较
    return quick_sort_index(left) + [mid] + quick_sort_index(right)


def parse_content(content):
    global total_list_v4
    global total_index_v4
    global total_list_v6
    global total_index_v6
    global total_list_as
    global total_num_v4
    global total_num_v6
    global total_num_as
    global total_list_int_v4
    print(content)
    soup = BeautifulSoup(content, 'html')
    data_list = []
    table = soup.find('table')
    tbody = table.find('tbody')

    for idx, tr in enumerate(tbody.find_all('tr')):
        td_list = tr.find_all('td')
        result = td_list[0].string
        description = td_list[1].get_text()
        img = td_list[1].find("img")

        if img:
            country = img.get("title")
        else:
            continue

        if result[:2] == "AS":
            info = (result, description, country)
            total_num_as = total_num_as+1
            total_list_as.append(info)
        else:
            if IP(result).version()==4:
                area = IP(result).strNormal(3).split("-")
                result = (area[0],area[1])
                info = (result, description, country)
                total_num_v4 = total_num_v4 + 1
                total_list_v4.append(info)
                total_index_v4.append(total_num_v4 - 1)
                ip2int = lambda x: sum([256 ** j * int(i) for j, i in enumerate(x.split('.')[::-1])])
                ipint_tuple = (ip2int(area[0]),ip2int(area[1]))
                total_list_int_v4.append(ipint_tuple)
                continue
            if IP(result).version()==6:
                area = IP(result).strNormal(3).split("-")
                result = (area[0],area[1])
                info = (result, description, country)
                total_num_v6 = total_num_v6 + 1
                total_list_v6.append(info)
                total_index_v6.append(total_num_v6 - 1)


def bgp_search(keyword):
    ROOT = "https://bgp.he.net"
    SEARCH = "/search"
    params = {"search[search]":keyword,
              "commit":"Search"}

    content = request(ROOT+SEARCH,params)
    parse_content(content)


def find_ips(keywords):
    for keyword in keywords:
        bgp_search(keyword)


def merge_intervals():
    global total_list_int_v4
    global merge_list_v4
    global total_index_v4
    merge_number = 0
    i = 1

    merge_list_v4.append(total_list_int_v4[total_index_v4[i]])
    while (i < total_num_v4):
        current_index = total_index_v4[i]
        if total_list_int_v4[current_index][0]>merge_list_v4[merge_number][1]:
            merge_list_v4.append(total_list_int_v4[current_index])
            merge_number += 1
            # print(merge_list_v4)

        if total_list_int_v4[current_index][0]<=merge_list_v4[merge_number][1]:
            if total_list_int_v4[current_index][1] > merge_list_v4[merge_number][1]:
                # print("merge")
                # print(merge_list_v4[merge_number])
                # print(total_list_int_v4[current_index])
                new_tuple = (merge_list_v4[merge_number][0],total_list_int_v4[current_index][1])
                merge_list_v4.pop()
                merge_list_v4.append(new_tuple)
                # print("merge over")
                # print(merge_list_v4)
                # print("="*20)
        i += 1


def output():
    global total_list_v4
    global total_index_v4
    global total_list_v6
    global total_index_v6
    global total_list_as
    global total_num_v4
    global total_num_v6
    global total_num_as

    print("Find AS:")
    print(total_num_as)
    print(total_list_as)
    print("="*20)
    print("Find v4 ips(input style{}):".format(ip_style))
    print("Sort index:",total_num_v4)
    print(total_index_v4)
    for _ in total_index_v4:
        format_string = "{}-{}".format(total_list_v4[_][0][0],total_list_v4[_][0][1])
        print("{:20}\t{:20}\t{}".format(IP(format_string).strNormal(ip_style),total_list_v4[_][2],total_list_v4[_][1]))
    print("="*20)

    print("After merge:")
    print(len(merge_list_v4))
    for _ in merge_list_v4:
        int2ip = lambda x: '.'.join([str(x//(256**i)%256) for i in range(3,-1,-1)])
        format_string = "{}-{}".format(int2ip(_[0]),int2ip(_[1]))
        print(IP(format_string).strNormal(ip_style))
    print("Find v6 ips:")
    print(total_num_v6)
    print(total_index_v6)
    for _ in total_index_v6:
        print(total_list_v6[_])


def main():
    global total_index_v4
    if len(argv)<2:
        print("Usage: %s <keyword1,keyword2...>" % argv[0])
    else:
        keywords = argv[1]
        keywords = keywords.strip()
        keywords = keywords.split(",")
        find_ips(keywords)
        new_index = quick_sort_index(total_index_v4)
        total_index_v4 = new_index
        merge_intervals()
        output()


if __name__ =="__main__":
    main()
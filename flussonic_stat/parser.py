import json
from itertools import groupby
import requests


def canonicalize_dict(x):
    return sorted(x.items(), key=lambda x: hash(x[0]))


def unique_and_count(lst):
    grouper = groupby(sorted(map(canonicalize_dict, lst)))
    return [dict(k + [("count", len(list(g)))]) for k, g in grouper]


def stat():
    try:
        list_ip = ['50.7.136.26', '51.195.4.225', '51.195.7.141', '145.239.140.7']
        dict_for_count = []
        headers = {'Content-Type': 'application/json'}

        for ip in list_ip:
            res = requests.get(f'http://admin:qwertystream@{ip}:89/flussonic/api/sessions').json()

            for i in res['sessions']:
                i.setdefault('source', f'{ip}')
                i.setdefault('token', '')
                i.setdefault('user_agent', '')
                i.setdefault('referer', '')
                i.setdefault('current_time', '')
                i.setdefault('user_id', '')
                del i['duration'], i['session_id'], i['country'], i['id'], i['bytes_sent'], i['created_at'], i[
                    'user_agent'], i[
                    'referer'], i['type'], i['current_time']
                if i.get('token').find('=') > 0:
                    i.update({'token': i.get('token').partition('?utc=')[0]})
                if i.get('user_id').find(':') > 0:
                    i.update({'user_id': i.get('user_id').partition(':')[2]})

                dict_for_count.append(i)

        data = json.dumps(unique_and_count(dict_for_count))
        for d in unique_and_count(dict_for_count):
            print(d)
        # requests.post('http://127.0.0.1:8000/stat/', data=data, headers=headers)

    except Exception as err:
        print(err)


if __name__ == "__main__":
    stat()

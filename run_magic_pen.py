import sounddevice as sd
import soundfile as sf
import requests
import queue
import sys
import os
import re
import urllib.request
import time
import urllib
import json
import hashlib
import base64
import IdentificationServiceHttpClientHelper

filePath = './data/tmp.wav'
fs = 16000

try:
    os.remove(filePath)
except OSError:
    pass

try:
    q = queue.Queue()

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(indata.copy())

    # Make sure the file is opened before recording anything:
    with sf.SoundFile(filePath, mode='x', samplerate=fs, channels=1) as file:
        with sd.InputStream(samplerate=fs, channels=1, callback=callback):
            print('请开始讲话，Ctrl+C结束说话...')
            while True:
                file.write(q.get())

except KeyboardInterrupt:
    print('\n录制结束: ' + repr(filePath)+'，正在进行语音识别...')
    t0 = time.time()

    # 1, 语音识别------------------------------------
    f = open(filePath, 'rb')
    file_content = f.read()
    base64_audio = base64.b64encode(file_content)
    body = urllib.parse.urlencode({'audio': base64_audio}).encode("utf-8")

    url = 'http://api.xfyun.cn/v1/service/v1/iat'
    api_key = 'e3462997d9c9e0ab0bdb02929ba1756a'
    param = {"engine_type": "sms16k", "aue": "raw"}
    x_appid = '5b9f8564'
    x_param = base64.b64encode(bytes(json.dumps(param).replace(' ', ''), "utf-8"))
    x_time = int(int(round(time.time() * 1000)) / 1000)

    a = api_key + str(x_time) + x_param.decode('utf-8')
    b = a.encode('utf-8')
    x_checksum = hashlib.md5(b)
    x_checksum = x_checksum.hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib.request.Request(url, body, x_header)
    result = urllib.request.urlopen(req)
    result = result.read().decode("utf-8")
    # print('result:', result)
    result = re.findall(u'[\u4e00-\u9fff]+', result)
    article_cn = '，'.join(result)

    print('语音识别结果:', article_cn)
    # print('语音识别耗时:', time.time() - t0, 's')
    t0 = time.time()

    # 2，摘要提取------------------------------------
    payload = {'article': article_cn}
    # print('开始摘要预测...')
    title_cn = requests.get('http://35.229.131.169:8008', params=payload)
    if 'unk' in title_cn.text:
        print('摘要预测结果:', title_cn.text.rstrip().replace('<unk>', '')+'*')
        # print('摘要预测耗时:', time.time() - t0, 's')
    if 'UNK' in title_cn.text:
        print('摘要预测结果:', title_cn.text.rstrip().replace('<UNK>', '')+'*')
        # print('摘要预测耗时:', time.time() - t0, 's')
    else:
        print('摘要预测结果:', title_cn.text.rstrip())
        # print('摘要预测耗时:', time.time() - t0, 's')

    # 3，声纹识别------------------------------------
    profile_ids = ['aabd9804-3c66-46d1-b8d3-4598b8aca4d8', '7874fb49-1c07-493c-b948-a496d6b1d1a9']
    profile_nms = ['kai', 'kun']

    helper = IdentificationServiceHttpClientHelper.IdentificationServiceHttpClientHelper('ccc2411ed1bb496fbc3aaf42540e81ac')
    identification_response = helper.identify_file(filePath, profile_ids, 'true')
    id = identification_response.get_identified_profile_id()
    name = profile_nms[profile_ids.index(id)] if id in profile_ids else '此人不在数据库，需先手动注册'
    print('声纹鉴定结果:', name)
    print('鉴定confidence：', identification_response.get_confidence())


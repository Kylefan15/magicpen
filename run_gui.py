import sounddevice as sd
import soundfile as sf
import requests
import os
import re
import urllib.request
import time
import urllib
import json
import hashlib
import base64
import IdentificationServiceHttpClientHelper
import datetime
from aip import AipSpeech

try:
        import Tkinter, ttk
except:
        import tkinter as Tkinter
        import tkinter.ttk as ttk
filePath = './data/tmp.wav'
fs = 16000
try:
    os.remove(filePath)
except OSError:
    pass


class Pen(Tkinter.Tk):
    def __init__(self, *args, **kwargs):

        Tkinter.Tk.__init__(self, *args, **kwargs)
        self.resizable(0, 0)
        self.create_additional_widgets()
        self.rec_status = 'start'
        self.profile_ids = ['aabd9804-3c66-46d1-b8d3-4598b8aca4d8',
                            '7874fb49-1c07-493c-b948-a496d6b1d1a9',
                            'cce7883d-51b8-45aa-8474-1e6b987e5dbf',
                            'cb86bd34-55fb-41b2-8995-02c6f170672a',
                            'cc4c4bee-adab-47f1-91f3-d45b961f09c5']
        self.profile_nms = ['kai', 'kun', 'wenpeng', 'gongjing', 'zhengwei']

        # read profiles from server and update self.profile_ids

    def create_additional_widgets(self):
        self.create_panel_for_widget()
        self.create_panel_for_chat_history()
        self.create_panel_for_sending_text()

    def start_stop_record(self):
        if self.rec_status == 'start':
            try:
                os.remove(filePath)
            except OSError:
                pass
            # start record
            self.rec_status = 'recording'
            self.Sending_Button['text'] = 'recording'

            duration = 5  # seconds
            myrecording = sd.rec(duration * fs, samplerate=fs, channels=1)  # array(fs)
            print("Recording Audio")
            sd.wait()
            sf.write(filePath, myrecording, fs)

            # def rec_audio():
            #     q = queue.Queue()
            #     def callback(indata, frames, time, status):
            #         """This is called (from a separate thread) for each audio block."""
            #         if status:
            #             print(status, file=sys.stderr)
            #         q.put(indata.copy())
            #
            #     # Make sure the file is opened before recording anything:
            #     with sf.SoundFile(filePath, mode='x', samplerate=fs, channels=1) as file:
            #         with sd.InputStream(samplerate=fs, channels=1, callback=callback):
            #             print('请开始讲话，Ctrl+C结束说话...')
            #             while self.rec_status == 'recording':
            #                 print('recording...')
            #                 file.write(q.get())
            #
            # p = multiprocessing.Process(target=rec_audio)
            # p.start()

        # elif self.rec_status == 'recording':
            # end record
            self.rec_status = 'start'
            self.Sending_Button['text'] = 'start'

            print('\n录制结束: ' + repr(filePath) + '，正在进行语音识别...')
            t0 = time.time()

            # 1.1, 首选讯飞语音识别------------------------------------
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
            print('result_responce:', result)
            result = re.findall(u'[\u4e00-\u9fff]+', result)
            article_cn = '，'.join(result)

            # 1.2, 备用语音识别------------------------------------
            if article_cn == '':
                print('connect xunfei error, change to baidu')
                APP_ID = '14130716'
                API_KEY = '39xGD77Aaq3kTYlefYq8u61X'
                SECRET_KEY = 'AUluhww4RhuLbZXZf66OANyc0OkuiDZz'
                client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

                def get_file_content(filePath):
                    with open(filePath, 'rb') as fp:
                        return fp.read()

                result = client.asr(get_file_content(filePath), 'wav', 16000, {'dev_pid': 1536, })
                print('result0:', result)
                article_cn = result['result'][0] if 'result' in result.keys() else 'connect baidu error'
                print('Recognition result:', article_cn)

            article_cn = article_cn + '。'
            print('语音识别结果:', article_cn)
            # print('语音识别耗时:', time.time() - t0, 's')

            # 2，摘要提取------------------------------------
            payload = {'article': article_cn}
            # print('开始摘要预测...')
            title_cn = requests.get('http://35.229.131.169:8008', params=payload)
            # title_cn = requests.get('http://127.0.0.1:8008', params=payload)
            print('摘要预测结果:', title_cn.text.rstrip().replace('<unk>', '').replace('<UNK>', '') + '*')

            # 3，声纹识别------------------------------------
            print('current self.profile_ids:', self.profile_ids)

            helper = IdentificationServiceHttpClientHelper.IdentificationServiceHttpClientHelper('ccc2411ed1bb496fbc3aaf42540e81ac')
            identification_response = helper.identify_file(filePath, self.profile_ids, 'true')
            id = identification_response.get_identified_profile_id()
            print('current profile_id:', id)
            name = self.profile_nms[self.profile_ids.index(id)] if id in self.profile_ids else 'stranger'
            print('声纹鉴定结果:', name)
            print('鉴定confidence：', identification_response.get_confidence())

            one_title = name + ': ' + title_cn.text.rstrip().replace('<unk>', '').replace('<UNK>', '') + '\n'
            # self.history.insert("end", one_title)

            start = self.history.index('end') + "-1l"
            self.history.insert("end", str(datetime.datetime.now()).split('.')[0]+'\n')
            self.history.insert("end", one_title)
            self.history.insert("end", '\n')
            end = self.history.index('end') + "-1l"
            self.history.tag_add("SENDBYME", start, end)
            self.history.tag_config("SENDBYME", foreground='Blue')

            start = self.history_article.index('end') + "-1l"
            self.history_article.insert("end", str(datetime.datetime.now()).split('.')[0] + '\n')
            self.history_article.insert("end", name + ': ' + article_cn)
            self.history_article.insert("end", '\n')
            end = self.history_article.index('end') + "-1l"
            self.history_article.tag_add("SENDBYME", start, end)
            self.history_article.tag_config("SENDBYME", foreground='Blue')

    def enroll_new_profile(self):
        subscription_key = 'ccc2411ed1bb496fbc3aaf42540e81ac'

        enroll_file = './data/enroll_tmp.wav'
        try:
            os.remove(enroll_file)
        except OSError:
            pass
        # enroll_name = self.Sending_data.get('1.0', 'end')[:-1]
        enroll_name = 'temp~'
        locale = 'en-us'
        # locale = enroll_name
        # 1, record audio to ./data/enroll_tmp.wav
        duration = 10  # seconds
        myrecording = sd.rec(duration * fs, samplerate=fs, channels=1)  # array(fs)
        print("正在采集声纹信息，请说话...")
        sd.wait()
        sf.write(enroll_file, myrecording, fs)
        print("采集完毕，正在加入数据库...")

        # 2, create_profile
        helper = IdentificationServiceHttpClientHelper.IdentificationServiceHttpClientHelper(
            subscription_key)

        creation_response = helper.create_profile(locale)
        profile_id = creation_response.get_profile_id()
        print('profile_id:', profile_id)

        # 3, Enroll user profiles with provided wav files
        helper = IdentificationServiceHttpClientHelper.IdentificationServiceHttpClientHelper(
            subscription_key)

        enrollment_response = helper.enroll_profile(profile_id, enroll_file, "true")
        print('status:', enrollment_response.get_enrollment_status())
        if enrollment_response.get_enrollment_status() == 'Enrolled':
            self.profile_ids.append(profile_id)
            self.profile_nms.append(enroll_name)
            print('enroll ok:', enroll_name)
        else:
            print('enroll fail:', enroll_name)

        helper = IdentificationServiceHttpClientHelper.IdentificationServiceHttpClientHelper(
            subscription_key)

        profiles = helper.get_all_profiles()
        print('Profile ID, Locale, Enrollment Speech Time, Remaining Enrollment Speech Time,'
              ' Created Date Time, Last Action Date Time, Enrollment Status')
        for profile in profiles:
            name = self.profile_nms[self.profile_ids.index(profile.get_profile_id())]
            print('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'.format(
                profile.get_profile_id(),
                profile.get_locale(),
                profile.get_enrollment_speech_time(),
                profile.get_remaining_enrollment_time(),
                profile.get_created_date_time(),
                profile.get_last_action_date_time(),
                profile.get_enrollment_status(),
                name))
    def print_all(self):
        subscription_key = 'ccc2411ed1bb496fbc3aaf42540e81ac'
        helper = IdentificationServiceHttpClientHelper.IdentificationServiceHttpClientHelper(
            subscription_key)

        profiles = helper.get_all_profiles()
        print('===============================================')
        print('Profile ID, Locale, Enrollment Speech Time, Remaining Enrollment Speech Time,'
              ' Created Date Time, Last Action Date Time, Enrollment Status')
        for profile in profiles:
            name = self.profile_nms[self.profile_ids.index(profile.get_profile_id())] if profile.get_profile_id() in self.profile_ids else 'stranger'
            print('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'.format(
                profile.get_profile_id(),
                profile.get_locale(),
                profile.get_enrollment_speech_time(),
                profile.get_remaining_enrollment_time(),
                profile.get_created_date_time(),
                profile.get_last_action_date_time(),
                profile.get_enrollment_status(),
                name))

    def create_panel_for_sending_text(self):
        # Here Creating Sending Panel
        # self.Sending_data = Tkinter.Text(self.Sending_panel, font=('arial 12 italic'), width=35, height=5)
        #
        # self.Sending_data.pack(side='left')

        self.Enroll_Button = Tkinter.Button(self.Sending_panel, text='enroll', width=15, height=1, bg='orange',
                                            command=self.enroll_new_profile, activebackground='lightgreen')
        self.Enroll_Button.pack(side='left')

        self.Sending_Button = Tkinter.Button(self.Sending_panel, text='start', width=15, height=1, bg='orange',
                                             command=self.start_stop_record, activebackground='lightgreen')
        self.Sending_Button.pack(side='left')

        self.Print_Button = Tkinter.Button(self.Sending_panel, text='print_all', width=15, height=1, bg='orange',
                                             command=self.print_all, activebackground='lightgreen')
        self.Print_Button.pack(side='left')


        return

    def create_panel_for_chat_history(self):

        self.history = Tkinter.Text(self.history_frame, font=('arial 12 bold italic'), width=80, height=20)
        self.history.pack()

        self.history_article = Tkinter.Text(self.history_frame_article, font=('arial 12 bold italic'), width=80, height=20)
        self.history_article.pack()

        return

    def create_panel_for_widget(self):
        self.history_frame = Tkinter.LabelFrame(self, text='history_frame ', fg='green', bg='powderblue')
        self.history_frame.pack(side='top')

        self.history_frame_article = Tkinter.LabelFrame(self, text='history_frame_article ', fg='green', bg='powderblue')
        self.history_frame_article.pack(side='top')

        self.Sending_panel = Tkinter.LabelFrame(self, text='Sending_panel', fg='green', bg='powderblue')
        self.Sending_panel.pack(side='top')
        return


if __name__ == '__main__':
    Pen(className='Magic pen client').mainloop()

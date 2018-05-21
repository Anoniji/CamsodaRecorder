import sys, datetime, time, os, threading
import requests, json, random
from livestreamer import Livestreamer

#specify path to save to ie "/Users/Joe/camsoda"
save_directory = "/Users/Joe/camsoda"
#specify the path to the wishlist file ie "/Users/Joe/camsoda/wanted.txt"
wishlist = "/Users/Joe/camsoda/wanted.txt"
#specify quality 188p or 480p
quality = "480p" 

headers={
    'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'referer':'https://www.camsoda.com/'
}
r = requests.session()
r.get('http://www.camsoda.com')
def getOnlineModels():
    num = random.randint(1000, 30000)
    wanted = []
    with open(wishlist) as f:
        for line in f:
            models = line.split()
            for theModel in models:
                wanted.append(theModel.lower())
    f.close()
    url = "https://www.camsoda.com/api/v1/browse/online"
    with r.get(url, headers=headers) as url:
        data = url.json()
        for line in data['results']:
            if line['username'].lower() not in recording and (line['display_name'].lower() in wanted or line['username'].lower() in wanted):
                if line['connections'] >= 10:
                    thread = threading.Thread(target=startRecording, args=(line, num))
                    thread.start()

def startRecording(modelData, num):
    global quality
    try:
        recording.append(modelData['username'].lower())
        videoapi = requests.get(
                "https://www.camsoda.com/api/v1/video/vtoken/{model}?username=guest_{num}".format(model=modelData['username'], num=num), headers=headers)
        data2 = json.loads(videoapi.text)

        if int(data2['status']) == 1:
            server = data2['edge_servers'][0]
            link = "hlsvariant://https://{server}/{app}/mp4:{stream_name}_h264_aac_{quality}/playlist.m3u8?token={token}".format(quality=quality, server=server, app=data2['app'], stream_name=data2['stream_name'], token=data2['token'])

        if not os.path.exists("{path}\\{model}".format(path=save_directory, model=modelData['username'])): os.makedirs("{path}\\{model}".format(path=save_directory, model=modelData['username']))

        session = Livestreamer()
        streams = session.streams(link)
        stream = streams["best"]
        fd = stream.open()
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime("%Y.%m.%d_%H.%M.%S")
        with open("{path}\\{model}\\{st}_{model}.mp4".format(path=save_directory, model=modelData['username'], st=st), 'wb') as f:
            while True:
                try:
                    data = fd.read(1024)
                    f.write(data)
                except:
                    recording.remove(modelData['username'].lower())
                    print("{} stream has ended".format(modelData['username']))
                    f.close()
                    return()
        recording.remove(modelData['username'].lower())
        print("{} stream has ended".format(modelData['username']))

    except:
        recording.remove(modelData['username'].lower())
        print("{} stream has ended".format(modelData['username']))

if __name__ == '__main__':
    recording = []
    while True:
        getOnlineModels()
        for i in range(30, 0, -1):
            print("{} model(s) are being recorded. Next check in {} seconds".format(len(recording), i))
            print("the following models are being recorded: {}".format(recording), end="\r")
            time.sleep(1)
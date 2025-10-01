import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Lark Alert')

def sender(msg, url=None, title='', del_blank_row=True):
    """
    # 文本格式化官方文档
    https://open.larksuite.com/document/ukTMukTMukTM/uMDMxEjLzATMx4yMwETM?lang=zh-CN
    # 关于加粗：用Card中的Fields来实现
    加粗（文档最底部）：https://open.larksuite.com/document/common-capabilities/message-card/message-cards-content/content-module
    https://open.larksuite.com/document/common-capabilities/message-card/message-cards-content/card-structure
    https://open.larksuite.com/document/common-capabilities/message-card/message-cards-content/using-markdown-tags
    加粗：（文档最底部）：https://open.larksuite.com/document/common-capabilities/message-card/message-cards-content/embedded-non-interactive-elements/field
    :param url: webhook地址
    :param msg: 需要发送的消息
    """
    if not url:
        url = 'https://open.larksuite.com/open-apis/bot/v2/hook/7bbfc97b-adc9c'
    msg_list = []
    for i in msg.strip().split('\n'):
        i = i.strip()
        if del_blank_row:
            if not i:
                continue
        if i:
            i_list = i.split(' ')
            msg_row = []
            for i_word in i_list:
                if '&url&' in i_word:
                    href =  i_word.split('&url&')[-1].strip()
                    link_name = i_word.split('&url&')[0].strip()
                    item_json = {
                        "tag": "a",
                        "href": href,
                        "text": link_name
                    }
                else:
                    item_json = {
                        "tag": "text",
                        "text": i_word + ' '
                    }
                msg_row.append(item_json)
        else:
            msg_row = [{"tag": "text","text": "\n"}]
        msg_list.append(msg_row)

    data = {
        "email": "drake.shi@bitget.com",
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": msg_list
                }
            }
        }
    }
    headers = {'Content-Type': 'application/json'}
    num = 0
    while True:
        try:
            res = requests.request("POST", url, headers=headers, data=json.dumps(data))
            print(res.text)
            return res.text
        except requests.exceptions.RequestException:
            num += 1
        if num > 3:
            break



def sender_colourful(url, content, title=''):
    """

    https://open.larksuite.com/document/common-capabilities/message-card/message-cards-content/using-markdown-tags
    """
    message = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                },
                "template": "red"
            },
            "elements": [{
                "tag": "markdown",
                "content": content,
            }]
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=json.dumps(message))
    logger.info(f'lark 告警调用成功：{response.text}')

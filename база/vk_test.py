import vk
import random

session = vk.Session()
api = vk.API(session, v=5.63)
try:
    r = api.messages.isMessagesFromGroupAllowed(access_token='c16521dbd31c34b3f0c9f6536546965b72507a482ba99e1922904f303f799d2c3b0c5a99f6c395b84a8f7', user_id=str('14567'), group_id=str('145476861'))
    print(r)
except:
    pass

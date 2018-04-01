# -*-coding=utf-8 -*-
#图片的验证码和短信的验证码
from  . import  api
from ihome.utils.captcha.captcha import captcha
@api.route('/image_code')
def get_image_code():


    #生成验证码:text是验证码的文职信息
    name,text,image=captcha.generate_captcha()

    return image
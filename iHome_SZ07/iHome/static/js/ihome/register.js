function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}
var uuid = "";
var last_uuid = '';
// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    // 1.需要生成UUID
    uuid = generateUUID();

    // last_uuid = uuid;

    // 2.拼接请求地址 ： url = /api/1.0/image_code?uuid=uuid
    var url = '/api/1.0/image_code?uuid=' + uuid + '&last_uuid=' + last_uuid;

    // 3.将url赋值给<img>标签的src属性
    // $('.image-code>img') : 表示从image-code标识的标签中直接找到子集<img>
    // $('.image-code img') : 表示从image-code标识的标签中找子集，如果子集没有，就去子集的子集中找
    $('.image-code>img').attr('src', url);

    // 当前的uuid使用完成后，立即记录，下次再进入时，之前保存到last_uuid里面就是上次的uuid
    last_uuid = uuid;
    
}

function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    // 避免暴力的获取短信验证码，一旦点击就移除点击事件
    $(".phonecode-a").removeAttr("onclick");
    // 获取手机号
    var mobile = $("#mobile").val();
    if (!mobile) {
        // 提示错误信息
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        // 如果有错，再次添加点击事件,让用户可以再次点击获取验证码
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    // TODO: 通过ajax方式向后端接口发送请求，让后端发送短信验证码
    // 要发送给服务端的数据
    var params = {
      'mobile':mobile,
      'imagecode':imageCode,
      'uuid':uuid
    };

    $.ajax({
        url:'/api/1.0/sms_code',        // 请求地址
        type:'post',                    // 请求方法
        data:JSON.stringify(params),    // 发送给服务器的数据
        contentType:'application/json', // 告诉服务器发送的数据时json
        headers:{'X-CSRFToken':getCookie('csrf_token')}, // 读取的当前页面终端额csrf_token信息发给服务器
        success:function (response) {   // 请求完成后的回调
            if (response.errno == '0') {
                // 发送短信验证码成功
                // 发送成功后，进行倒计时
                var num = 30;
                var t = setInterval(function ()  {
                    if (num == 0) {
                        // 倒计时完成,清除定时器
                        clearInterval(t);
                        // 重置内容
                        $(".phonecode-a").html('获取验证码');
                        // 重新添加点击事件
                        $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    } else {
                        // 正在倒计时，显示秒数
                        $(".phonecode-a").html(num + '秒');
                    }

                    num = num - 1;
                }, 1000);
            } else {
                // 发送短信验证码失败
                // 重新添加点击事件
                $(".phonecode-a").attr("onclick", "sendSMSCode();");
                // 重新生成验证码
                generateImageCode();
                // 弹出错误消息
                alert(response.errmsg);
            }
        }
    });
}

$(document).ready(function() {
    generateImageCode();  // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });

    // TODO: 注册的提交(判断参数是否为空)
    $('.form-register').submit(function (event) {
        // 阻止form表单自己的提交时间
        event.preventDefault();

        // 读取要发送给服务器的变量：手机号，短信验证码，密码，确认密码
        var mobile = $('#mobile').val();
        var phonecode = $('#phonecode').val();
        var password = $('#password').val();
        var password2 = $('#password2').val();

        // 校验变量是否存在
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if (!phonecode) {
            $('#phone-code-err span').html('请填写短信验证码');
            $('#phone-code-err').show();
            return;
        }
        if (!password) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (password != password2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }

        // 准备参宿
        var params = {
            'mobile':mobile,
            'sms_code':phonecode,
            'password':password
        };

        // 发送注册请求给服务器
        $.ajax({
            url:'/api/1.0/users',
            type:'post',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                if (response.errno == '0') {
                    // 如果注册成功，进入到主页
                    location.href = '/'
                } else {
                    alert(response.errmsg);
                }
            }
        });
    });
});

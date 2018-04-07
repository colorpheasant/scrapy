function hrefBack() {
    history.go(-1);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function showErrorMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

$(document).ready(function(){
    // TODO: 判断用户是否登录
    $.get('/api/1.0/sessions', function (response) {
        if (!(response.data.user_id && response.data.name)) {
           location.href = '/login.html'
        }
    });


    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    $(".input-daterange").on("changeDate", function(){
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();

        if (startDate && endDate && startDate > endDate) {
            showErrorMsg("日期有误，请重新选择!");
        } else {
            var sd = new Date(startDate);
            var ed = new Date(endDate);
            // days = (ed - sd)/(1000*3600*24) + 1;
            days = (ed - sd)/(1000*3600*24);
            var price = $(".house-text>p>span").html();
            var amount = days * parseFloat(price);
            $(".order-amount>span").html(amount.toFixed(2) + "(共"+ days +"晚)");
        }
    });
    var queryData = decodeQuery();
    var houseId = queryData["hid"];

    // TODO: 获取房屋的基本信息
   $.get('/api/1.0/houses/detail/'+houseId, function (response) {
       if (response.errno == '0') {
           // 渲染界面
           $('.house-info>img').attr('src', response.data.house.img_urls[0]);
           $('.house-text>h3').html(response.data.house.title);
           $('.house-text span').html((response.data.house.price/100).toFixed(2));

       } else {
           alert(response.errmsg);
       }
   });

    // TODO: 订单提交
});

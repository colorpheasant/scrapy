//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //修正原先已经有的30个像素
    });
}

function setStartDate() {
    var startDate = $("#start-date-input").val();
    if (startDate) {
        $(".search-btn").attr("start-date", startDate);
        $("#start-date-btn").html(startDate);
        $("#end-date").datepicker("destroy");
        $("#end-date-btn").html("离开日期");
        $("#end-date-input").val("");
        $(".search-btn").attr("end-date", "");
        $("#end-date").datepicker({
            language: "zh-CN",
            keyboardNavigation: false,
            startDate: startDate,
            format: "yyyy-mm-dd" // 2018-04-07
        });
        $("#end-date").on("changeDate", function() {
            $("#end-date-input").val(
                $(this).datepicker("getFormattedDate")
            );
        });
        $(".end-date").show();
    }
    $("#start-date-modal").modal("hide");
}

function setEndDate() {
    var endDate = $("#end-date-input").val();
    if (endDate) {
        $(".search-btn").attr("end-date", endDate);
        $("#end-date-btn").html(endDate);
    }
    $("#end-date-modal").modal("hide");
}

// 主页界面上搜索标签的点击事件，将自己传入到其中， th ：表示外界传入的搜索标签
function goToSearchPage(th) {
    // http://127.0.0.1:5000/search.html?aid=1&aname=%E4%B8%9C%E5%9F%8E%E5%8C%BA&sd=2018-04-07&ed=2018-04-08
    var url = "/search.html?";
    url += ("aid=" + $(th).attr("area-id"));
    url += "&";
    var areaName = $(th).attr("area-name");
    if (undefined == areaName) areaName="";
    url += ("aname=" + areaName);
    url += "&";
    url += ("sd=" + $(th).attr("start-date"));
    url += "&";
    url += ("ed=" + $(th).attr("end-date"));
    location.href = url;
}


function swiper() {
    // TODO: 数据设置完毕后,需要设置幻灯片对象，开启幻灯片滚动
    var mySwiper = new Swiper ('.swiper-container', {
        loop: true,
        autoplay: 2000,
        autoplayDisableOnInteraction: false,
        pagination: '.swiper-pagination',
        paginationClickable: true
    });
}

$(document).ready(function(){
    // TODO: 检查用户的登录状态
    $.get('/api/1.0/sessions', function (response) {
        if (response.errno == '0') {

            if (response.data.user_id && response.data.name) {
                // 登录：展示用户名
                $(".top-bar>.user-info").show();
                $(".top-bar>.user-info>a").html(response.data.name);
            } else {
                // 未登录：展示注册和登录
                $(".top-bar>.register-login").show();
            }

        } else {
            alert(response.errmsg);
        }
    });


    // TODO: 获取幻灯片要展示的房屋基本信息
    $.get('/api/1.0/houses/index', function (response) {
        if (response.errno == '0') {
            var html = template('swiper-houses-tmpl', {'houses':response.data});
            $('.swiper-wrapper').html(html);
            swiper();
        } else {
            alert(response.errmsg);
        }
    });


    // TODO: 获取城区信息,获取完毕之后需要设置城区按钮点击之后相关操作
    $.get('/api/1.0/areas', function (response) {
        if (response.errno == '0') {

            var html = template('area-list-tmpl', {'areas':response.data});
            $('.area-list').html(html);

            // TODO: 城区按钮点击之后相关操作
            $(".area-list a").click(function(e){
                $("#area-btn").html($(this).html());
                $(".search-btn").attr("area-id", $(this).attr("area-id"));
                $(".search-btn").attr("area-name", $(this).html());
                $("#area-modal").modal("hide");
            });

        } else {
            alert(response.errmsg);
        }
    });


    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);               //当窗口大小变化的时候
    $("#start-date").datepicker({
        language: "zh-CN",
        keyboardNavigation: false,
        startDate: "today",
        format: "yyyy-mm-dd"
    });
    $("#start-date").on("changeDate", function() {
        var date = $(this).datepicker("getFormattedDate");
        $("#start-date-input").val(date);
    });
})

var cur_page = 1; // 当前页
var next_page = 1; // 下一页
var total_page = 1;  // 总页数
var house_data_querying = true;   // 是否正在向后台获取数据

// 解析url中的查询字符串
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

// 更新用户点选的筛选条件
function updateFilterDateDisplay() {
    var startDate = $("#start-date").val();
    var endDate = $("#end-date").val();
    var $filterDateTitle = $(".filter-title-bar>.filter-title").eq(0).children("span").eq(0);
    if (startDate) {
        var text = startDate.substr(5) + "/" + endDate.substr(5);
        $filterDateTitle.html(text);
    } else {
        $filterDateTitle.html("入住日期");
    }
}


// 更新房源列表信息
// action表示从后端请求的数据在前端的展示方式
// 默认采用追加方式
// action=renew 代表页面数据清空从新展示
function updateHouseData(action) {
    var areaId = $(".filter-area>li.active").attr("area-id");
    if (undefined == areaId) areaId = "";
    var startDate = $("#start-date").val();
    var endDate = $("#end-date").val();
    var sortKey = $(".filter-sort>li.active").attr("sort-key");
    var params = {
        aid:areaId,
        sd:startDate,
        ed:endDate,
        sk:sortKey,
        p:next_page
    };

    // TODO: 获取房屋列表信息
    // 参数1 ： 请求地址；参数2：请求参数(可选的，如果有就传入，没有就省略)；参数3：请求完成后的回调
    // params : 存储的是要通过GET请求发送给服务器的字符串信息
    // http://127.0.0.1:5000/search.html?aid=2&aname=&sd=&ed=
    $.get('/api/1.0/houses/search', params, function (response) {

        // 能够进入到该回调，说明上次的请求结束，需要将house_data_querying = false
        house_data_querying = false;

        if (response.errno == '0') {

            // 后端需要将总页数返回给前端并保存 total_page
            total_page = response.data.total_page;

            // 使用art-template模板引擎，生成需要渲染的html内容
            var html = template('house-list-tmpl', {'houses':response.data.houses});

            // 区分是上拉刷新，还是加载新的数据，要区分用户是直接加载的数据还是上拉刷新 action == renew 表示重新加载新的数据
            if (action == 'renew') {
                // 加载新的数据，将html渲染到界面
                $('.house-list').html(html);
            } else {
                // 每次上拉刷新成功后，需要对 cur_page 累加 1
                cur_page = next_page;

                // 上拉刷新，上拉刷新得到新的数据时，不要覆盖上一页的数据，需要拼接到上一页的下面
                $('.house-list').append(html);
            }

        } else {
            alert(response.errmsg);
        }
    });
}

$(document).ready(function(){
    var queryData = decodeQuery();
    var startDate = queryData["sd"];
    var endDate = queryData["ed"];
    $("#start-date").val(startDate); 
    $("#end-date").val(endDate); 
    updateFilterDateDisplay();
    var areaName = queryData["aname"];
    if (!areaName) areaName = "位置区域";
    $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html(areaName);


    // 获取筛选条件中的城市区域信息
    $.get("/api/1.0/areas", function(data){
        if ("0" == data.errno) {
            var areaId = queryData["aid"];
            if (areaId) {
                for (var i=0; i<data.data.length; i++) {
                    areaId = parseInt(areaId);
                    if (data.data[i].aid == areaId) {
                        $(".filter-area").append('<li area-id="'+ data.data[i].aid+'" class="active">'+ data.data[i].aname+'</li>');
                    } else {
                        $(".filter-area").append('<li area-id="'+ data.data[i].aid+'">'+ data.data[i].aname+'</li>');
                    }
                }
            } else {
                for (var i=0; i<data.data.length; i++) {
                    $(".filter-area").append('<li area-id="'+ data.data[i].aid+'">'+ data.data[i].aname+'</li>');
                }
            }


            // 在页面添加好城区选项信息后，更新展示房屋列表信息
            updateHouseData("renew");


            var windowHeight = $(window).height()
            // 为窗口的滚动添加事件函数
            window.onscroll=function(){
                // var a = document.documentElement.scrollTop==0? document.body.clientHeight : document.documentElement.clientHeight;
                var b = document.documentElement.scrollTop==0? document.body.scrollTop : document.documentElement.scrollTop;
                var c = document.documentElement.scrollTop==0? document.body.scrollHeight : document.documentElement.scrollHeight;
                // 如果滚动到接近窗口底部
                if(c-b<windowHeight+50){
                    // 如果没有正在向后端发送查询房屋列表信息的请求
                    if (!house_data_querying) {
                        // 将正在向后端查询房屋列表信息的标志设置为真
                        house_data_querying = true;
                        // 如果当前页面数还没到达总页数
                        if(cur_page < total_page) {
                            // 将要查询的页数设置为当前页数加1
                            next_page = cur_page + 1;
                            // 向后端发送请求，查询下一页房屋数据// 向后端发送请求，查询下一页房屋数据
                            updateHouseData();
                        } else {
                            house_data_querying = false;
                        }
                    }
                }
            }
        }
    });

    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    var $filterItem = $(".filter-item-bar>.filter-item");
    $(".filter-title-bar").on("click", ".filter-title", function(e){
        var index = $(this).index();
        if (!$filterItem.eq(index).hasClass("active")) {
            $(this).children("span").children("i").removeClass("fa-angle-down").addClass("fa-angle-up");
            $(this).siblings(".filter-title").children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).addClass("active").siblings(".filter-item").removeClass("active");
            $(".display-mask").show();
        } else {
            $(this).children("span").children("i").removeClass("fa-angle-up").addClass("fa-angle-down");
            $filterItem.eq(index).removeClass('active');
            $(".display-mask").hide();
            updateFilterDateDisplay();
        }
    });
    $(".display-mask").on("click", function(e) {
        $(this).hide();
        $filterItem.removeClass('active');
        updateFilterDateDisplay();
        cur_page = 1;
        next_page = 1;
        total_page = 1;
        updateHouseData("renew");

    });
    $(".filter-item-bar>.filter-area").on("click", "li", function(e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html($(this).html());
        } else {
            $(this).removeClass("active");
            $(".filter-title-bar>.filter-title").eq(1).children("span").eq(0).html("位置区域");
        }
    });
    $(".filter-item-bar>.filter-sort").on("click", "li", function(e) {
        if (!$(this).hasClass("active")) {
            $(this).addClass("active");
            $(this).siblings("li").removeClass("active");
            $(".filter-title-bar>.filter-title").eq(2).children("span").eq(0).html($(this).html());
        }
    })
})

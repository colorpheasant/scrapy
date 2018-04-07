function hrefBack() {
    history.go(-1);
}

// 解析提取url中的查询字符串参数
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}


function swiper() {
    // TODO: 数据加载完毕后,需要设置幻灯片对象，开启幻灯片滚动
    var mySwiper = new Swiper ('.swiper-container', {
        loop: true,
        autoplay: 2000,
        autoplayDisableOnInteraction: false,
        pagination: '.swiper-pagination',
        paginationType: 'fraction'
    });
}

$(document).ready(function(){
    // 获取详情页面要展示的房屋编号
    var queryData = decodeQuery();
    var houseId = queryData["id"];

    // TODO: 获取该房屋的详细信息
    $.get('/api/1.0/houses/detail/' + houseId, function (response) {
        if (response.errno == '0') {

            var html_swiper = template('house-image-tmpl', {'img_urls':response.data.house.img_urls, 'price':response.data.house.price});
            $('.swiper-container').html(html_swiper);

            swiper();

            var html_detail = template('house-detail-tmpl', {'house':response.data.house});
            $('.detail-con').html(html_detail);

            // 实现即可预定按钮的显示逻辑
            // response.data.house.user_id : 获取当前正在看的房屋信息的发布者是谁
            if (response.data.house.user_id != response.data.login_user_id) {
                // 当前查看详情的用户不是登录用户 展示即可预定按钮
                $('.book-house').show();
                // 添加即可预定的点击跳转的逻辑
                // $('.book-house').attr('href', 'booking.html?hid+' + response.data.house.hid);
                $('.book-house').attr('href', 'booking.html?hid=' + response.data.house.hid);
            } else {
                // 当前查看详情的用户就是登录用户 ： 隐藏即可预定按钮
                $('.book-house').hide();
            }

        } else {
            alert(response.errmsg);
        }
    });
});
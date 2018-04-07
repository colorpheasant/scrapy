function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');

    // TODO: 在页面加载完毕之后获取区域信息
    $.get('/api/1.0/areas', function (response) {
        if (response.errno == '0') {
            // 渲染城区信息 <option value="1">东城区</option>
            // $.each(response.data, function (i, area) {
            //     $('#area-id').append('<option value="'+area.aid+'">'+area.aname+'</option>');
            // });

            // art-template模板引擎渲染界面
            // 生成要渲染的html数据
            var html = template('areas-tmpl', {'areas':response.data});
            // 使用生成的html数据，渲染目标标签
            $('#area-id').html(html);

        } else {
            alert(response.errmsg);
        }
    });


    // TODO: 处理房屋基本信息提交的表单数据
    $('#form-house-info').submit(function (event) {
        event.preventDefault();

        // 准备参数
        var params = {};

        // var title = $('#house-title').val();
        // params['title'] = title;

        // 收集form表单中需要提交的input标签,放在一个数组对象中
        // map 遍历对象，比如说数组对象
        // obj == {name: "title", value: "1"}
        $(this).serializeArray().map(function (obj) {
            // console.log(obj);
            params[obj.name] = obj.value;

        });

        // 收集房屋设施信息
        //  $(':checkbox:checked[name=facility]') == 收集界面上被选中的name为facility的checkbox
        // each 遍历界面上收集到的标签
        // elem == <input type="checkbox" name="facility" value="2">热水淋浴
        facilities = [];
        $(':checkbox:checked[name=facility]').each(function (i, elem) {
            // console.log(elem);
            facilities[i] = elem.value;
        });
        params['facility'] = facilities;

        // console.log(params);

        $.ajax({
            url:'/api/1.0/houses',
            type:'post',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                if (response.errno == '0') {
                    // 需求:发布房屋基本信息成功。需要展示发布房屋图片的界面
                    // 隐藏发布基本信息表单。展示发布房屋图片的表单
                    $('#form-house-info').hide();
                    $('#form-house-image').show();

                    // 将后端生成的house_id传入到上传图片的<input>
                    $('#house-id').val(response.data.house_id);

                } else if (response.errno == '4101')  {
                    location.href = '/';
                } else {
                    alert(response.errmsg);
                }
            }
        });
    });

    // TODO: 处理图片表单的数据
    $('#form-house-image').submit(function (event) {
        event.preventDefault();

        $(this).ajaxSubmit({
            url:'/api/1.0/houses/image',
            type:'post',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                if (response.errno == '0') {
                    $('.house-image-cons').append('<img src="'+response.data.image_url+'">');
                } else if (response.errno == '4101')  {
                    location.href = '/';
                } else {
                    alert(response.errmsg);
                }
            }
        });
    });
});
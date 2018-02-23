var build ='<button type="button" class="btn btn-primary btn-xs build">构建</button>' +
           ' <button type="button" class="btn btn-primary btn-xs build_log">日志</button>';
var deploybutton='<button type="button" class="btn btn-primary btn-xs deploy">发布</button>' +
           ' <button type="button" class="btn btn-primary btn-xs deploy_log" disabled="disabled">日志</button>';
var deploy_history = '<button type="button" class="btn btn-primary btn-xs deploy_history">发布历史</button>'
function addnewRow(response)
{
    $.each(response,function(index,value){
            var value=JSON.parse(value);
            var newRow = "<tr><td>" + value['appname'] + "</td><td>" + value['deploytime'] + "</td><td>"
            + value['deployer'] + "</td><td>" + value['deploy_status'] + "</td><td>" + value['tag_version'] + "</td><td>";
            $("#history_list_table tr:last").after(newRow);
           })
}

function env(){
        return $(".envselect option:selected").text();
    }

var dataTable_init_setting =  {
    retrieve: true,
    //"processing": true,
};



var res_datatable_setting = {
        columns: [
            {data: "appname"}, {data: "tag_version"}, {data:"status"}, {data: "deployer"},
            {
                "data": null,
                "defaultContent": build
            },
            {
                "data": null,
                "defaultContent": deploybutton
            },
            {
                "data": null,
                "defaultContent": deploy_history
            },
        ],
        deploy_history_show: function () {
            $('#deploy_history_modal').modal('show');
            },
        external_links_show: function () {
            $('#external_links').modal('show');
            },
        log_console_show: function() {
            $('#log_output').modal('show');
            $('#build_conf').modal('hide');
        },
        build_conf_show: function(){
            $('#build_conf').modal('show');
        },
        deploy_conf_show: function(){
            $('#deploy_conf').modal('show');
        },
        deploy_console_show: function(){
            $('#deploy_log_console').modal('show');
        },
    }






$(document).ready(function(){

    function setting_datatable_paras(){
        dataTable_init_setting.ajax = {
            url: '/autodeploy/index/env?env=' + env(),
            dataSrc: "",
        };



        dataTable_init_setting.columns = res_datatable_setting.columns
        // 当表格初始化完毕时 执行以下动作
        dataTable_init_setting.initComplete = function(settings,json){
        window.DT
                .on('click', '.deploy_history', function(){
                 build_appname=window.DT.row($(this).parents('td')).data()['appname'];
                $('#deploy_history_modal').modal('show')
                .on('shown.bs.modal',function(){
                      $.ajax({
                            url: '/autodeploy/index/historylist?env=' + env() + '&appname=' + build_appname,
                            dataType: 'json',
                            success: function(response,status){
                                addnewRow(response);
                            }
                            });
                            $('#deploy_history_modal').off('shown.bs.modal');

                        })
                .on('hidden.bs.modal',function () {
                                // 在完全隐藏之后
                                $('#history_list_table tr:gt(0)').empty();
                            })

                     })


                .on('click', '.build', function(){
                res_datatable_setting.build_conf_show();
                build_appname=window.DT.row($(this).parents('td')).data()['appname'];
                cell_tag_version=window.DT.cell($(this).parents('tr').children().eq(1));
                cell_deployer=window.DT.cell($(this).parents('tr').children().eq(3));
                })

                .on('click', '.deploy', function(){
                build_appname=window.DT.row($(this).parents('td')).data()['appname'];
                cell_tag_version=window.DT.cell($(this).parents('tr').children().eq(1));
                cell_deployer=window.DT.cell($(this).parents('tr').children().eq(3));
                $('#deploy_conf').modal('show')
                .on('shown.bs.modal',function(){
                            var loading = layer.load();
                            $.ajax({
                            url: '/autodeploy/index/getexistexternallist?env=' + env() + '&appname=' + build_appname,
                            dataType: 'json',
                            success: function(response,status){
                                $.each(response['external_list'],function(index,value){
                                    $("#groups_right").append("<option value=" + value + ">" + value + "</option>");
                                })
                                layer.close(loading);
                            }
                            });
                            $('#deploy_conf').off('shown.bs.modal');
                    })
                .on('hidden.bs.modal',function () {
                                // 在完全隐藏之后
                                $('#groups_right').empty();
                                $('#groups_left').empty();
                                $("#external_link_check").prop("checked",false);
                            })
                })

                .on('click', '.build_log', function(){
                    window.start_offset = 0;
                    build_appname=window.DT.row($(this).parents('td')).data()['appname'];
                    var outputInterval = null;
                    $('#log_output').modal('show').off('shown.bs.modal hide.bs.modal hidden.bs.modal')
                    .on('shown.bs.modal', function () {
                        $('#output-container').append('请等待5s...\n');
                            outputInterval = setInterval(function () {
                                $.ajax({
                                    url: '/autodeploy/index/getConsoleOutPut?start_offset='
                                    + window.start_offset + '&env=' + env() + '&appname=' + build_appname,
                                    dataType: 'json',
                                    success: function(response,status){
                                        $('#output-container').append(response['output']);
                                        if(!response['more_data']){
                                            clearInterval(outputInterval)
                                        } else {
                                            if(response.hasOwnProperty('next_start_offset')){
                                                window.start_offset = response['next_start_offset'];
                                            } else {
                                                clearInterval(outputInterval)
                                            }
                                        }
                                    }

                                    });

                                }, 5000)

                            })
                            .on('hide.bs.modal', function () {
                                clearInterval(outputInterval)
                            })
                            .on('hidden.bs.modal',function () {
                                // 在完全隐藏之后
                                $('#output-container').empty();
                            })
                })
                .on('click','.deploy_log',function(){
                    res_datatable_setting.deploy_console_show();
                })
                .on( 'init.dt', function () {
                    $(".envselect").prop("disabled", false);
                })

            };

        }



    function initDataTable(){
        setting_datatable_paras();
        return $('#myTable').DataTable(dataTable_init_setting);
    }

    window.DT = initDataTable();



    $('#add').click(function(){
            $("#groups_left").find("option:selected").each(function(){
                $("#groups_right").append("<option value=" + $(this).val() + ">" + $(this).text() + "</option>");
                $(this).remove();
            });
        });
    $('#remove').click(function(){
            $("#groups_right").find("option:selected").each(function(){
                $("#groups_left").append("<option value=" + $(this).val() + ">" + $(this).text() + "</option>");
                $(this).remove();
            });
        });
    $('#upload_file_check').click(function(){
                     if (this.checked) {
                        $("#confirm_upload").removeAttr("disabled");
                        $("#upload").removeAttr("disabled");
                     } else {
                        $("#confirm_upload").attr("disabled", true);
                        $("#upload").attr("disabled", true);
                     };
                });
    $('#external_link_check').click(function(){
                     if (this.checked) {
                        $("#add").removeAttr("disabled");
                        $("#remove").removeAttr("disabled");
                        if ($('#groups_left option').length  == 0)
                        {
                        var loading = layer.load();
                        $.ajax({
                            type:'GET',
                            url:'/autodeploy/index/get_external_link/?env=' + env() + '&appname=' + build_appname,
                            dataType:'json',
                            success:function(response,status){
                                $.each(response['locallist'],function(i,val){
                                    $('#groups_left').append('<option value=' + val + '>' + val + '</option>');
                                });
                            layer.close(loading);
                            }
                });
                        }


                     } else {
                        $("#add").attr("disabled", true);
                        $("#remove").attr("disabled", true);

                     };


                });
    $('#confirm_upload').click(function(){
                if  ($("#upload").val() == "")
                    {
                        layer.msg("请上传文件", {
                           time: 2000, //2s后自动关闭
                     })
                        return false;
                    };
                alert(env());
                alert(build_appname);
                var formData = new FormData();
                var file_info = $('#upload')[0].files[0];
                formData.append('file',file_info);
                formData.append('env',env());
                formData.append('appname',build_appname);
                    $.ajax({
                            type:'POST',
                            url: '/autodeploy/index/uploadconfile/',
                            data: formData,
                            processData: false,
                            contentType: false,
                            success: function(response,status){
                                layer.msg("上传成功", {
                                time: 2000, //2s后自动关闭
                                })
                            },
                            error: function(event,errorText,errorType){
                                layer.msg("上传失败", {
                                time: 2000, //2s后自动关闭
                                })
                            }
                        });
                });
    $('#check_tag_version').click(function(){
                     if (this.checked) {
                        $("#tag_version").removeAttr("disabled");
                     } else {
                        $("#tag_version").attr("disabled", true);
                     };
                });
    $('#confirm_build').click(function(){
                    if ($("#branch_name").val() == "")
                    {
                         layer.msg("请输入分支名称", {
                           time: 2000, //2s后自动关闭
                     })
                        return false;
                    };
                    if($("#check_tag_version").prop( "checked" ) && $("#tag_version").val() == "")
                    {
                        layer.msg("请输入tag版本号", {
                           time: 2000, //2s后自动关闭
                     })
                        return false;
                    }
                    data=$('#build_form').serialize() + '&env=' + $('.envselect').val() + '&appname=' + build_appname;

                    var loading = layer.load();
                    var outputInterval = null;
                    layer.msg("开始构建", { time: 2000,});
                    $.ajax({
                            type:'POST',
                            url: '/autodeploy/index/startbuild/',
                            data: data,
                            dataType: 'json',
                            success: function(response,status){
                                if(response['result'] === 'SUCCESS'){
                                    layer.msg(response['message'], {
                                        time: 2000, //2s后自动关闭
                                    });
                                    $('#build_conf').modal('hide');
                                    $('.build_log').trigger('click');
                                    $('#log_output').on('hide.bs.modal', function () {
                                    clearInterval(outputInterval)
                                    })
                                    .on('hidden.bs.modal',function () {
                                    // 在完全隐藏之后
                                    $('#output-container').empty();
                                    })

                                }
                                else {
                                    layer.msg(response['message'], {
                                        time: 3000, //2s后自动关闭
                                    });
                                    $('#build_conf').modal('hide');
                                    $('.build_log').trigger('click');
                                    $('#log_output').on('hide.bs.modal', function () {
                                    clearInterval(outputInterval)
                                    })
                                    .on('hidden.bs.modal',function () {
                                    // 在完全隐藏之后
                                    $('#output-container').empty();
                                    })
                                    }
                                layer.close(loading);
                            },
                            error: function(event,errorText,errorType){
                                alert('down');
                            }
                        });



                 });
    $('#confirm_deploy').click(function(){
                    //if($("#upload_file_check").prop( "checked" ) &&
                    if ($("#upload").val() == "")
                    {
                        layer.msg("请上传文件", {
                           time: 2000, //2s后自动关闭
                     })
                        return false;
                    };


                    var array = new Array();  //定义数组
                    $("#groups_right option").each(function(){  //遍历所有option
                        var txt = $(this).val();   //获取option值
                        array.push(txt);  //添加到数组中
                    });
                    if($("#external_link_check").prop( "checked" ) && array == "")
                    {
                        layer.msg("请选择所需外部域名链接", {
                           time: 2000, //2s后自动关闭
                     })
                        return false;
                    };
                    var array=JSON.stringify(array);
                    $.ajax({
                            type:'POST',
                            url: '/autodeploy/index/startdeploy/',
                            data: {select:array,env:env(),appname:build_appname},
                            success: function(response,status){
                                $('#deploy_conf').modal('hide');
                                $('.deploy_log').trigger('click');
                                if (response['message'] == "yes")
                                {
                                    layer.msg("提交发布成功", {
                                    time: 2000,
                                    });
                                    deployer=response['deployer'];
                                    tag_version=response['tag_version'];
                                    cell_tag_version.data(tag_version);
                                    cell_deployer.data(deployer);
                                }else if(response['message'] == "deploy_again") {
                                    layer.msg("已有该次发布记录，请重新构建新的发布", {
                                    time: 5000,
                                    })
                                }else{
                                    layer.msg("提交发布失败，请检查配置是否正确或联系运维", {
                                    time: 4000,
                                    })
                                };
                            },
                            error: function(event,errorText,errorType){
                                layer.msg("提交发布失败，请检查配置是否正确或联系运维", {
                                    time: 4000, //2s后自动关闭
                                    })
                            }
                        });
                });

    $(".envselect").on('change',function(){
         var loading = layer.load();
         layer.msg("请稍等", {
                   time: 2000, //2s后自动关闭
                   });
        //window.DT.clear().draw();
        window.DT.ajax.url('/autodeploy/index/env?env=' + env()).load(function(){
            layer.close(loading);
        });
    });
});
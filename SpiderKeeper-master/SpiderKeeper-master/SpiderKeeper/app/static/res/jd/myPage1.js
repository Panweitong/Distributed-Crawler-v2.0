function exeData(num, type) {
    loadData(num);
    loadpage();
}

function exeData1(num,id, type) {
    loadData1(num,id);
    mm();
}

function loadpage() {
    var myPageCount = parseInt($("#PageCount").val());
    var myPageSize = parseInt($("#PageSize").val());
    var countindex = myPageCount % myPageSize > 0 ? (myPageCount / myPageSize) + 1 : (myPageCount / myPageSize);
    $("#countindex").val(countindex);

    $.jqPaginator('#pagination', {
        totalPages: parseInt($("#countindex").val()),
        visiblePages: parseInt($("#visiblePages").val()),
        currentPage: parseInt($("#CurrentPage").val()),

        first: '<li class="first"><a href="/jd/info?page=1">首页</a></li>',
        prev: '<li class="prev"><a href="/jd/info?page={{page}}"><i class="arrow arrow2"></i>上一页</a></li>',
        next: '<li class="next"><a href="/jd/info?page={{page}}">下一页<i class="arrow arrow3"></i></a></li>',
        last: '<li class="last"><a href="/jd/info?page={{totalPages}}">末页</a></li>',
        page: '<li class="page"><a href="/jd/info?page={{page}}">{{page}}</a></li>',
        onPageChange: function (num, type) {
            if (type == "change") {
                exeData(num, type);
            }
        }
    });
}

function mm() {
   var myPageCount = parseInt($("#PageCount1").val());
    var myPageSize = parseInt($("#PageSize1").val());
    var countindex = myPageCount % myPageSize > 0 ? (myPageCount / myPageSize) + 1 : (myPageCount / myPageSize);
    $("#countindex1").val(countindex);

    $.jqPaginator('#pagination1', {
        totalPages: parseInt($("#countindex1").val()),
        visiblePages: parseInt($("#visiblePages1").val()),
        currentPage: parseInt($("#CurrentPage1").val()),

        first: '<li class="first"><a onclick="dd(1)">首页</a></li>',
        prev: '<li class="prev"><a onclick="dd({{page}})"><i class="arrow arrow2"></i>上一页</a></li>',
        next: '<li class="next"><a onclick="dd({{page}})">下一页<i class="arrow arrow3"></i></a></li>',
        last: '<li class="last"><a onclick="dd({{totalPages}})">末页</a></li>',
        page: '<li class="page"><a onclick="dd({{page}})">{{page}}</a></li>',
        onPageChange: function (num,id, type) {
            if (type == "change") {
                exeData1(num,id, type);
            }
        }
    });
}

function dd(num){
         $("#myModal").modal('show');
         document.getElementById("number6").innerHTML=num;
         $("#CurrentPage1").val(num);
         $.ajax({
             type: "GET",
             url: "/jd/comment",
             data:{
                 id: $("#id").val(),
                 page:num.toString()
             },
             dataType:"json",
             success: function (result) {
                 document.getElementById("number4").innerText=result.count.toString();
                 document.getElementById("number5").innerText=result.num_pages.toString();
                 $("#content").html("");
                 var str = "";
                 for (var i = 0; i < 5; i++) {
                     if (i == 1 || i == 3) {
                         str += "<div style='background-color: #f9f9f9;border-top:1px solid black;border-bottom:1px solid black;'>" +
                             "<div class='row' style='text-align:center;padding: 15px;'>" +
                             "<div class='col-xs-4'><b>" + result.result[i].username.toString() + "</b>(" + result.result[i].leverName.toString() + ")</div>" +
                             "<div class='col-xs-4'>" + result.result[i].type.toString() + "&nbsp;&nbsp" + result.result[i].date.toString() + "</div>" +
                             "<div class='col-xs-4'>" + result.result[i].score.toString() + "星</div>" +
                             "</div><br>" +
                             "<div class='row' style='width: 850px;margin-left: 0px;'>" +
                             "<div style='padding-left:25px;padding-right:25px;'>" + result.result[i].content.toString() + "</div>" +
                             "</div><br>" +
                             "<div class='row' style='width: 850px;margin-left: 0px;'>" +
                             "<div class='col-xs-3'></div>" +
                             "<div class='col-xs-3'></div>" +
                             "<div class='col-xs-3'></div>" +
                             "<div class='col-xs-3'style='height: 35px;'>" + result.result[i].source.toString() + "</div>" +
                             "</div></div>"
                     }
                     else {
                         str += "<div>" +
                             "<div class='row' style='text-align:center;padding: 15px;'>" +
                             "<div class='col-xs-4'><b>" + result.result[i].username.toString() + "</b>(" + result.result[i].leverName.toString() + ")</div>" +
                             "<div class='col-xs-4'>" + result.result[i].type.toString() + "&nbsp;&nbsp" + result.result[i].date.toString() + "</div>" +
                             "<div class='col-xs-4'>" + result.result[i].score.toString() + "星</div>" +
                             "</div><br>" +
                             "<div class='row' style='width: 850px;margin-left: 0px;'>" +
                             "<div style='padding-left:25px;padding-right:25px;'>" + result.result[i].content.toString() + "</div>" +
                             "</div><br>" +
                             "<div class='row' style='width: 850px;margin-left: 0px;'>" +
                             "<div class='col-xs-3'></div>" +
                             "<div class='col-xs-3'></div>" +
                             "<div class='col-xs-3'></div>" +
                             "<div class='col-xs-3'style='height: 35px;'>" + result.result[i].source.toString() + "</div>" +
                             "</div></div>"
                     }
                 }
                    $("#content").append(str);
             }
         });
     }

window.onload = function () {
    $('#preloader_4').hide();
    loadData(1);
    loadpage();
};

var tTD; //用来存储当前更改宽度的Table Cell,避免快速移动鼠标的问题
var table = document.getElementById("tb_1");
for (j = 0; j < table.rows[0].cells.length; j++) {
     table.rows[0].cells[j].onmousedown = function () {
         //记录单元格
         tTD = this;
         if (event.offsetX > tTD.offsetWidth - 10) {
         tTD.mouseDown = true;
         tTD.oldX = event.x;
         tTD.oldWidth = tTD.offsetWidth;
     }
    //记录Table宽度
   //table = tTD; while (table.tagName != ‘TABLE') table = table.parentElement;
   //tTD.tableWidth = table.offsetWidth;
};
   table.rows[0].cells[j].onmouseup = function () {
       //结束宽度调整
       if (tTD == undefined) tTD = this;
            tTD.mouseDown = false;
            tTD.style.cursor = 'default';
   };
   table.rows[0].cells[j].onmousemove = function () {
       //更改鼠标样式
       if (event.offsetX > this.offsetWidth - 10)
            this.style.cursor = 'col-resize';
       else
            this.style.cursor = 'default';
       //取出暂存的Table Cell
       if (tTD == undefined) tTD = this;
       //调整宽度
       if (tTD.mouseDown != null && tTD.mouseDown == true) {
              tTD.style.cursor = 'default';
              if (tTD.oldWidth + (event.x - tTD.oldX)>0)
                 tTD.width = tTD.oldWidth + (event.x - tTD.oldX);
             //调整列宽
             tTD.style.width = tTD.width;
             tTD.style.cursor = 'col-resize';
       //调整该列中的每个Cell
      table = tTD; while (table.tagName != 'TABLE') table = table.parentElement;
      for (j = 0; j < table.rows.length; j++) {
          table.rows[j].cells[tTD.cellIndex].width = tTD.width;
      }
//调整整个表
//table.width = tTD.tableWidth + (tTD.offsetWidth – tTD.oldWidth);
//table.style.width = table.width;
}
};
}
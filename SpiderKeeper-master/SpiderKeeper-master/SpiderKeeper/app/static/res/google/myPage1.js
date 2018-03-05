function exeData(num, type) {
    loadData(num);
    loadpage();
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

        first: '<li class="first"><a href="/google/google?page=1">首页</a></li>',
        prev: '<li class="prev"><a href="/google/google?page={{page}}"><i class="arrow arrow2"></i>上一页</a></li>',
        next: '<li class="next"><a href="/google/google?page={{page}}">下一页<i class="arrow arrow3"></i></a></li>',
        last: '<li class="last"><a href="/google/google?page={{totalPages}}">末页</a></li>',
        page: '<li class="page"><a href="/google/google?page={{page}}">{{page}}</a></li>',
        onPageChange: function (num, type) {
            if (type == "change") {
                exeData(num, type);
            }
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
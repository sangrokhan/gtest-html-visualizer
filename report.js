// $(function() {
//     $(".fold-table tr.view").on("click", function () { 
//         $(this).toggleClass("open").next(".fold").toggleClass("open");
//     });
// });


function addRowHandlers() {
    var table = document.getElementById("main-table");
    var rows = table.getElementsByClassName("view");
    for (i = 0; i < rows.length; i++) {
        var currentRow = rows[i];
        var createClickHandler = function(row) {
            return function() {
                var cell = row.getElementsByTagName("td")[0];
                var id = cell.innerHTML;
                alert("id:" + id);
                console.log("clicked")
            };
        };
        currentRow.onClick = createClickHandler(currentRow);
    }
}

addRowHandlers();

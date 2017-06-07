
    function updateInputTable() {
        // if (loadFromTables)
        //     getDataFromTables();

        newRows = document.getElementById("inputRows").value
        newCols = document.getElementById("inputCols").value

        curRows = inputHandsonTable.countRows()
        curCols = inputHandsonTable.countCols()

        if(newRows > curRows){
           inputHandsonTable.alter('insert_row',curRows ,newRows - curRows); 
       }
       else if (newRows < curRows){
        inputHandsonTable.alter('remove_row', curRows,curRows - newRows );
    }
    if(newCols > curCols){
       inputHandsonTable.alter('insert_col',curCols, newCols - curCols); 
   }
   else if (newCols < curCols){
    inputHandsonTable.alter('remove_col',curCols, curCols - newCols);
}

}


function updateOutputTable() {
    newRows = document.getElementById("outputRows").value
    newCols = document.getElementById("outputCols").value

    curRows = outputHandsonTable.countRows()
    curCols = outputHandsonTable.countCols()

    if(newRows > curRows){
       outputHandsonTable.alter('insert_row',curRows ,newRows - curRows); 
   }
   else if (newRows < curRows){
    outputHandsonTable.alter('remove_row', curRows,curRows - newRows );
}
if(newCols > curCols){
   outputHandsonTable.alter('insert_col',curCols, newCols - curCols); 
}
else if (newCols < curCols){
    outputHandsonTable.alter('remove_col',curCols, curCols - newCols);
}
}

        // firstRow = handsontable.rowOffset()
        // firstCol = handsontable.colOffset()

        // renderedRowCount = handsontable.countRenderedRows()
        // renderedColCount = handsontable.countRenderedCols()
        
        // for(var i = firstRow +renderedRowCount; i >= firstRow ;i--){
        //     if(handsontable.isEmptyRow(i)){
        //         // handsontable.alter('remove_row', i);
        //         alert("empty_row"+i)
        //     }
        // }

        // firstRow = handsontable.rowOffset()
        // firstCol = handsontable.colOffset()
        // renderedRowCount = handsontable.countRenderedRows()
        // renderedColCount = handsontable.countRenderedCols()

        // for(var i = firstCol + renderedColCount; i >= firstCol ;i--){
        //     if(handsontable.isEmptyCol(i)){
        //         // handsontable.alter('remove_col', i);
        //         alert("empty_col"+i)
        //     }
        // }

        function getDataFromTables(handsontable) {


            firstCol = 0
            lastCol = 30
            firstRow = 0
            lastRow = 50

            while(firstCol <= lastCol && handsontable.isEmptyCol(firstCol)){
                firstCol = firstCol + 1
            }

            while(firstCol <= lastCol && handsontable.isEmptyCol(lastCol)){
                lastCol = lastCol - 1
            }


            while(firstRow <= lastRow && handsontable.isEmptyRow(firstRow)){
                firstRow = firstRow + 1
            }

            while(firstRow <= lastRow && handsontable.isEmptyRow(lastRow)){
                lastRow = lastRow - 1
            }


            tempTable = handsontable.getData(firstRow,firstCol,lastRow,lastCol)

        // Data Cleaning
        for(var a=0; a < tempTable.length;a++){
            for(var b = 0; b<tempTable[0].length;b++){
                if(tempTable[a][b] == null){
                    tempTable[a][b] = ""
                }
                else{
                    tempTable[a][b] = tempTable[a][b].trim()
                }
            }
        }

        return tempTable

    }



    function makeStatesTable(states) {
        html = '<table border=1 cellpadding=3>';
        for (var i = 0; i < states.length; i++) {
            html += '<tr>'
            for (var j = 0; j < states[i].length; j++) {
                html += '<td>' + states[i][j] + '</td>'
            }
            html += '</tr>'
        }
        html += '</table>'
        return html;
    }

var serialized_program;

    function submitData() {
        toggleButton();
        if($('#result').css('display') != 'none'){
            toggleResult();
            $("#result_btn").addClass('hidden');
        }
        if($('#verify').css('display') != 'none'){
            toggleVerify();
            $("#verify_btn").addClass('hidden');
        }


        $("#success-alert").addClass('hidden');
        $("#warning-alert").addClass('hidden');
        $("#failure-alert").addClass('hidden');
        lastTimeStamp = new Date();

        var inputData = getDataFromTables(inputHandsonTable);
        var outputData = getDataFromTables(outputHandsonTable);

        var jsonData = {'InputTable': inputData, 'OutputTable': outputData, 'RawData': rawData, "Username": "anonymous", "TestCase": testCaseName}

        $.ajax({ // ajax call starts
            url: '/astar',
            type: 'POST',
            data: JSON.stringify(jsonData),
            dataType: 'json',
            contentType: "application/json",
            timeout:'60000'
        })
        .done(function(data) {

            var ops = data.ops;
            var h = data.h_steps;
            var states = data.states;
            var opDiv = document.getElementById('operations');
            var statDiv = document.getElementById('stats');
            var html = '';
            var stathtml = '';
            var transformed = data.transformedTable;
            var transformedDiv = document.getElementById('transformedTable');

            serialized_program = data.serialized_program;

            // jsonData['program'] = ""

            var program = data.program;

            if(program==''){
                $("#failure-alert").removeClass('hidden');
                toggleButton();

            }
            else{

                toggleResult();
                toggleVerify();


                $("#result_btn").removeClass('hidden');
                $("#verify_btn").removeClass('hidden');

                $('#code').html(program);
                hljs.initHighlighting.called = false;
                hljs.initHighlighting();
          
                $("#success-alert").removeClass('hidden');
                var stat = {
                    // 'num_mouse_clicks':clickCount,
                // "num_keyboard_strokes":keyCount,
                // "latency":(lastTimeStamp - firstTimeStamp)/1000,
                "branch_factor":data.branch_factor,
                'num_visited':data.num_visited,
                'total_time':data.time,
                'program':program,
                'InputTable':jsonData['InputTable'],
                'OutputTable':jsonData['OutputTable'],
                'Username': data.username,
                'RawData': rawData,
                'Transformed':transformed,
                'TestCase':testCaseName}
                // jsonData['num_mouse_clicks'] = clickCount
                // jsonData['num_keyboard_strokes'] = keyCount
                // jsonData['latency'] = (lastTimeStamp - firstTimeStamp)/1000
                // jsonData['branch_factor'] = data.branch_factor
                // jsonData['num_visited'] = data.num_visited
                // jsonData['total_time'] = data.time


                console.log(stat)

                // opDiv.innerHTML = html;
                // statDiv.innerHTML = stathtml;
                // transformedDiv.innerHTML = "<p>Applying the Synthesized Program to Raw Data</p>" + transformed;



                // Cache

                $.ajax({ // ajax call starts
                    url: '/cache',
                    type: 'POST',
                    data: JSON.stringify(stat),
                    dataType: 'json',
                    contentType: "application/json",
                }).done(function(data) {
                }).fail(function(jqXHR, textStatus) {
                });


                // reset
                // clickCount = 0;
                // keyCount = 0;
                // firstTimeStamp = 0;
                // lastTimeStamp = 0;
                toggleButton()
        }
    })
        .fail(function(jqXHR, textStatus) {
            // alert("Request failed: " + textStatus);
            $("#warning-alert").removeClass('hidden');
            toggleButton();
        });

        return false;
    }

    // function doOnLoad() {
    //     updateInputTable();
    //     updateOutputTable();
    //     return false;
    // }

    var rawData = [[""]]

    var testCaseName = ""

    function loadExample(ex) {
        $("#success-alert").addClass('hidden')
        $("#warning-alert").addClass('hidden')
        $("#failure-alert").addClass('hidden')




        if (ex != '') {
            $.getJSON("/static/data/"+encodeURIComponent(ex), function(json) {
                inputData = json.InputTable;
                outputData = json.OutputTable;
                testCaseName = ex;
                rawData = json.RawData
                introData = json.Intro

                // alert(inputData.length)
                // alert(inputData[0].length)

                inputHandsonTable.clear()
                outputHandsonTable.clear()


                var changesInput = []
                for (var i = 0; i < inputData.length; i++) {
                    for (var j = 0; j < inputData[0].length; j++) {

                        changesInput.push([i,j,inputData[i][j]])
                    }
                }
                inputHandsonTable.clear()


                // Reshape
                var curRows = inputHandsonTable.countRows()
                var curCols = inputHandsonTable.countCols()
                var newRows = inputData.length + 1
                var newCols = inputData[0].length + 1


                if(newRows > curRows){
                   inputHandsonTable.alter('insert_row',curRows ,newRows - curRows); 
                }
                else if (newRows < curRows){
                    inputHandsonTable.alter('remove_row', curRows,curRows - newRows );
                }
                if(newCols > curCols){
                   inputHandsonTable.alter('insert_col',curCols, newCols - curCols); 
                }
                else if (newCols < curCols){
                    inputHandsonTable.alter('remove_col',curCols, curCols - newCols);
                }
                

                inputHandsonTable.setDataAtCell(changesInput)

                var changesOutput = []
                for (var i = 0; i < outputData.length; i++) {
                    for (var j = 0; j < outputData[0].length; j++) {

                        changesOutput.push([i,j,outputData[i][j]])
                    }
                }

                
                outputHandsonTable.clear() 


                // Reshape
                var curRows = outputHandsonTable.countRows()
                var curCols = outputHandsonTable.countCols()
                var newRows = outputData.length + 1
                var newCols = outputData[0].length + 1


                if(newRows > curRows){
                   outputHandsonTable.alter('insert_row',curRows ,newRows - curRows); 
                }
                else if (newRows < curRows){
                    outputHandsonTable.alter('remove_row', curRows,curRows - newRows );
                }
                if(newCols > curCols){
                   outputHandsonTable.alter('insert_col',curCols, newCols - curCols); 
                }
                else if (newCols < curCols){
                    outputHandsonTable.alter('remove_col',curCols, curCols - newCols);
                }
                

                outputHandsonTable.setDataAtCell(changesOutput)



            });       
        }
    }


    // window.onload = doOnLoad


function findSelectedData(){
    // var ht = inputHandsonTable.handsontable('getInstance');
    var sel = inputHandsonTable.getSelected();
    return sel;
}

function toggleButton() {
      $('#submitButton').toggle()
      $('#processingLabel').toggle()

    }


function toggleResult() {
    $('#result').toggle()
}

function toggleVerify() {
    $('#verify').toggle()
}



/* When the user clicks on the button, 
toggle between hiding and showing the dropdown content */
function dropDownloadExample() {
    // document.getElementById("myDropdown").classList.toggle("show");
    $("#myDropdown").removeClass('hidden');
}

// Close the dropdown if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {
    $("#myDropdown").addClass('hidden');
   
  }
}



function verifyProgram() {

    lastTimeStamp = new Date();

    var inputData = getDataFromTables(verifyInputHandsonTable);

    var jsonData = {'test_table': inputData,"serialized_program":serialized_program}

    $.ajax({ // ajax call starts
        url: '/execute',
        type: 'POST',
        data: JSON.stringify(jsonData),
        dataType: 'json',
        contentType: "application/json",
        timeout:'60000'
    })
    .done(function(data) {


        var transformed = data.transformed_table;

        verifyOutputHandsonTable.clear()


        var changesInput = []
        for (var i = 0; i < transformed.length; i++) {
            for (var j = 0; j < transformed[0].length; j++) {

                changesInput.push([i,j,transformed[i][j]])
            }
        }


        // Reshape
        var curRows = verifyOutputHandsonTable.countRows()
        var curCols = verifyOutputHandsonTable.countCols()
        var newRows = transformed.length + 1
        var newCols = transformed[0].length + 1


        if(newRows > curRows){
           verifyOutputHandsonTable.alter('insert_row',curRows ,newRows - curRows); 
        }
        else if (newRows < curRows){
            verifyOutputHandsonTable.alter('remove_row', curRows,curRows - newRows );
        }
        if(newCols > curCols){
           verifyOutputHandsonTable.alter('insert_col',curCols, newCols - curCols); 
        }
        else if (newCols < curCols){
            verifyOutputHandsonTable.alter('remove_col',curCols, curCols - newCols);
        }
        

        verifyOutputHandsonTable.setDataAtCell(changesInput)




})
    .fail(function(jqXHR, textStatus) {
        alert("system error")
    });

    return false;
}



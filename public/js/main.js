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
function submitData() {
    toggleButton()
    var inputData = getDataFromTables(inputHandsonTable);
    var outputData = getDataFromTables(outputHandsonTable);

    var jsonData = {'InputTable': inputData, 'OutputTable': outputData}

$.ajax({ // ajax call starts
    url: '/astar',
    type: 'POST',
    data: JSON.stringify(jsonData),
    dataType: 'json',
    contentType: "application/json",
})
.done(function(data) {

    var ops = data.ops
    var h = data.h_steps
    var states = data.states
    var opDiv = document.getElementById('operations');
    var statDiv = document.getElementById('stats');
    var html = '';
    var stathtml = '';

// jsonData['program'] = ""

var program = ""

if (ops.length == 0) {
    html += "Search timed out after " + data.time + " seconds."
}
else {
// html += 'Search time: ' + data.time + " seconds"
// html += '<table border="1" cellpadding="3" cellspacing="0">';
// html += '<tr><td>#</td><td>Operation</td><td>Column</td><td>H</td><td>State</td></tr>';
// html += '<tr><td>0.</td><td>'+ops[0][0]+'</td><td>'+ ops[0][1]+'</td><td>--</td><td>' + makeStatesTable(states[0]) + '</td></tr>';
// for (var i = 1; i < ops.length; i++) {
//     html += '<tr><td>'+i+'.</td><td>'+ops[i][0]+'</td><td>'+ ops[i][1]+'</td><td>' + h[i] + '</td><td>' + makeStatesTable(states[i]) + '</td></tr>';
// }
// html += '</table>'

html += '<table>';
html += '<tr><td><b>Step #</b></td><td><b>Data Transformation Operation</b></td></tr>';
// html += '<tr><td>0.</td><td>'+ops[0][0]+'</td><td>'+ ops[0][1]+'</td><td>--</td><td>' + makeStatesTable(states[0]) + '</td></tr>';
for (var i = 1; i < ops.length; i++) {
    html += '<tr><td>'+i+'.</td><td>'+ops[i][0]+' on column <b>'+ ops[i][1]+'</b></td></tr>';
    program += ops[i][0]+' on column'+ops[i][1] + "#";
}
html += '</table>';



stathtml += '<table>';
stathtml += '<tr><td><b>Stat Name</b></td><td><b>Result</b></td></tr>';

if(data.time <= 30){
    stathtml += '<tr><td>Search time</td><td><font color="green">' + data.time + "</font> seconds</td></tr>";
}
else{
    stathtml += '<tr><td>Search time</td><td><font color="red">' + data.time + "</font> seconds</td></tr>";
}
stathtml += '<tr><td>Branch Factor</td><td>' + data.branch_factor + "</td></tr>";
stathtml += '<tr><td>Nodes Created</td><td>' + data.nodes_created + "</td></tr>";
stathtml += '<tr><td>Nodes Visited</td><td>' + data.num_visited + "</td></tr>";
stathtml += '<tr><td>Mouse Clicks</td><td>' + clickCount + "</td></tr>";
stathtml += '<tr><td>Key Strokes</td><td>' + keyCount + "</td></tr>";
stathtml += '<tr><td>User Effort (Mouse Clicks + Key Strokes)</td><td>' + (keyCount+clickCount) + "</td></tr>";
stathtml += '<tr><td>Interaction Time</td><td>' + (lastTimeStamp - firstTimeStamp)/1000 + " seconds</td></tr>";
stathtml += '</table>';

}


var stat = {'num_mouse_clicks':clickCount,
"num_keyboard_strokes":keyCount,
"latency":(lastTimeStamp - firstTimeStamp)/1000,
"branch_factor":data.branch_factor,
'num_visited':data.num_visited,
'total_time':data.time,
'program':program,
'InputTable':jsonData['InputTable'],
'OutputTable':jsonData['OutputTable'] }
// jsonData['num_mouse_clicks'] = clickCount
// jsonData['num_keyboard_strokes'] = keyCount
// jsonData['latency'] = (lastTimeStamp - firstTimeStamp)/1000
// jsonData['branch_factor'] = data.branch_factor
// jsonData['num_visited'] = data.num_visited
// jsonData['total_time'] = data.time


console.log(stat)

opDiv.innerHTML = html;
statDiv.innerHTML = stathtml;


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
clickCount = 0;
keyCount = 0;
firstTimeStamp = 0;
lastTimeStamp = 0;
toggleButton()
})
.fail(function(jqXHR, textStatus) {
    alert("Request failed: " + textStatus);
    toggleButton()
});

return false;
}



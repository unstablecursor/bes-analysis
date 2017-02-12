var counter = 1;

function addInput(divName){
    var newdiv = document.createElement('div');
    newdiv.innerHTML = "Name " + (counter + 1) + " <br><input type='text' name='name[]'><br>" + 
    "Type " + (counter + 1) +" <br><input type='checkbox' name='type[]' value='BUY'>BUY"  +
    "<input type = 'checkbox' name='type[]' value='SELL'> SELL <br>" +
    "Number " + (counter + 1) + "<br><input type='text' name='number[]'><br>" +
    "Date " + (counter + 1) + "<br><input type='text' name='date[]'><sbr>" ; 
    document.getElementById(divName).appendChild(newdiv);
    counter++;
}
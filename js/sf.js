$(document).ready(function() {
  document.getElementById("calcButton").addEventListener ("click", function() { analyze()});

  function analyze() {

    var form_data = $("form").serializeArray();
    var lat = form_data[0].value;
    var long = form_data[1].value;
    var time = form_data[2].value;

    services = ['ENGINE', 'MEDIC']

    var table = document.getElementById("results");
    var row = table.insertRow();
    var latitude = row.insertCell(0);
    latitude.innerHTML = lat
    var longitude = row.insertCell(1);
    longitude.innerHTML = long
    var date = row.insertCell(2);
    date.innerHTML = time
    var service = row.insertCell(3);

    if(time.length != 30 || parseFloat(lat) != parseInt(lat, 10) || parseFloat(long) != parseInt(long, 10))
      service.innerHTML = "Cannot predict a dispatch service for the given data values"
    else
      service.innerHTML = services[Math.floor(Math.random()*2)]
 }
});

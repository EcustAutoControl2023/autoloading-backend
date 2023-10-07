function start()
{
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/start");
  xhr.send();
}
function stop()
{
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/stop");
  xhr.send();
}

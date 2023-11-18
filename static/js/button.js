var socket = io('http://localhost:5000');

document.getElementById('loader_1').addEventListener("click",Function1);
document.getElementById('loader_2').addEventListener("click",Function2);
document.getElementById('loader_3').addEventListener("click",Function3);
document.getElementById('loader_4').addEventListener("click",Function4);
document.getElementById('loader_5').addEventListener("click",Function5);
document.getElementById('loader_6').addEventListener("click",Function6);
document.getElementById('loader_7').addEventListener("click",Function7);
document.getElementById('loader_8').addEventListener("click",Function8);
document.getElementById('loader_9').addEventListener("click",Function9);
document.getElementById('loader_10').addEventListener("click",Function10);
document.getElementById('loader_11').addEventListener("click",Function11);
document.getElementById('loader_12').addEventListener("click",Function12);
document.getElementById('loader_13').addEventListener("click",Function13);
document.getElementById('loader_14').addEventListener("click",Function14);
document.getElementById('loader_15').addEventListener("click",Function15);
document.getElementById('loader_16').addEventListener("click",Function16);
document.getElementById('loader_17').addEventListener("click",Function17);
document.getElementById('loader_18').addEventListener("click",Function18);
document.getElementById('loader_19').addEventListener("click",Function19);
document.getElementById('loader_20').addEventListener("click",Function20);


function Function1(){

  socket.emit('traffic_data_request', {loader: loader_1},
              'xxxxxx', {sensor: sensor1});              
}

function Function2(){

  socket.emit('traffic_data_request', {loader: loader_2},
              'xxxxxx', {sensor: sensor2});  
}

function Function3(){

  socket.emit('traffic_data_request', {loader: loader_3},
              'xxxxxx', {sensor: sensor3});  
}

function Function4(){

  socket.emit('traffic_data_request', {loader: loader_4},
              'xxxxxx', {sensor: sensor4});  
}

function Function5(){

  socket.emit('traffic_data_request', {loader: loader_5},
              'xxxxxx', {sensor: sensor5});  
}

function Function6(){

  socket.emit('traffic_data_request', {loader: loader_6},
              'xxxxxx', {sensor: sensor6});  
}

function Function7(){

  socket.emit('traffic_data_request', {loader: loader_7},
              'xxxxxx', {sensor: sensor7});  
}

function Function8(){

  socket.emit('traffic_data_request', {loader: loader_8},
              'xxxxxx', {sensor: sensor8});  
}

function Function9(){

  socket.emit('traffic_data_request', {loader: loader_9},
              'xxxxxx', {sensor: sensor9});  
}

function Function10(){

  socket.emit('traffic_data_request', {loader: loader_10},
              'xxxxxx', {sensor: sensor10});  
}

function Function11(){

  socket.emit('traffic_data_request', {loader: loader_11},
              'xxxxxx', {sensor: sensor11});  
}

function Function12(){

  socket.emit('traffic_data_request', {loader: loader_12},
              'xxxxxx', {sensor: sensor12});  
}

function Function13(){

  socket.emit('traffic_data_request', {loader: loader_13},
              'xxxxxx', {sensor: sensor13});  
}

function Function14(){

  socket.emit('traffic_data_request', {loader: loader_14},
              'xxxxxx', {sensor: sensor14});  
}

function Function15(){

  socket.emit('traffic_data_request', {loader: loader_15},
              'xxxxxx', {sensor: sensor15});  
}

function Function16(){

  socket.emit('traffic_data_request', {loader: loader_16},
              'xxxxxx', {sensor: sensor16});  
}

function Function17(){

  socket.emit('traffic_data_request', {loader: loader_17},
              'xxxxxx', {sensor: sensor17});  
}

function Function18(){

  socket.emit('traffic_data_request', {loader: loader_18},
              'xxxxxx', {sensor: sensor18});  
}

function Function19(){

  socket.emit('traffic_data_request', {loader: loader_19},
              'xxxxxx', {sensor: sensor19});  
}

function Function20(){

  socket.emit('traffic_data_request', {loader: loader_20},
              'xxxxxx', {sensor: sensor20});  
}

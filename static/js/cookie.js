/*   Function for getting in and out of the cookie   */

function userinfo(){
  dookie = getinfo();
  $('#akunausername').val(dookie['aun']);
  $('#akunapassword').val(dookie['apw']);
  $('#esgfopenid').val(dookie['eoi']);
  $('#esgfpassword').val(dookie['epw']);

  $('#userinfo').toggle();
}

function saveinfo(option){
  if(option == 'clear'){
    localStorage.acme = "";
    localStorage.aun  = "";
    localStorage.apw  = "";
    localStorage.eoi  = "";
    localStorage.epw  = "";
    $('#akunausername').val('');
    $('#akunapassword').val('');
    $('#esgfopenid').val('');
    $('#esgfpassword').val('');
  }
  else{
    localStorage.acme = "true";
    localStorage.aun  = $('#akunausername').val();
    localStorage.apw  = $('#akunapassword').val();
    localStorage.eoi  = $('#esgfopenid').val();
    localStorage.epw  = $('#esgfpassword').val();
  }
  //userinfo();
  location.reload();
}

function getinfo(){
  cookie = [];
  cookie['acme'] = "true";
  cookie['aun'] = "";
  cookie['apw'] = "";
  cookie['eoi'] = "";
  cookie['epw'] = "";

  if (localStorage.acme == "true"){
    cookie['acme'] = localStorage.acme ;
    cookie['aun'] = localStorage.aun ;
    cookie['apw'] = localStorage.apw ;
    cookie['eoi'] = localStorage.eoi ;
    cookie['epw'] = localStorage.epw ;
  }
  else {
    localStorage.acme = cookie['acme'];
    localStorage.aun  = cookie['aun'];
    localStorage.apw  = cookie['apw'];
    localStorage.eoi  = cookie['eoi'];
    localStorage.epw  = cookie['epw'];
  }
  return cookie
}

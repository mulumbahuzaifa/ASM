let g_port_counter = 2;
let g_volume_counter = 2;
let exposed_p_counter = 2;

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');
$(document).ready(function(){

  $.ajaxSetup({
      error: function(x, e) {
          if (x.status == 0) {
              $('#div-right-pane').html('Unable to reach docker server. Check that it is started and you can reach it on your network.');
          }
             else if (x.status == 404) {
          $('#div-right-pane').html('Requested URL not found.');

          } else if (x.status == 500) {
              $('#div-right-pane').html('Internal Server Error.');
          }  else {
              $('#div-right-pane').html('Unknow Error.\n' + x.responseText);
          }
      }
  });



  $.get('docker/dashboard', function(response) {
  $('#div-right-pane').html('Wait..');
  $('#div-right-pane').html(response);
  $('#cont-data-table').DataTable();
  $('#cont-running-data-table').DataTable();
  });
});
function showDashboard()
{
  $.get('docker/dashboard', function(response) {
  $('#div-right-pane').html(response);
  if ($('#cont-data-table').length)
  {
    $('#cont-data-table').DataTable();
  }
  if ($('#cont-running-data-table').length)
  {
    $('#cont-running-data-table').DataTable();
  }
  });
}

function containerDashboard(cont_id)
{
  $.get('docker/container_dashboard', {cont_id:cont_id},function(response) {
  $('#div-right-pane').html(response);
    });
}




function refreshImage()
{
  $.get('docker/disp_images', function(response) {
  $('#div-right-pane').html(response);
  if ($('#img-display-data-table').length)
  {
    var str = $('#img-display-data-table').html();
var res = str.replace(/\[\'/g,"");
var res2 = res.replace(/\'\]/g, "");
$('#img-display-data-table').html(res2);
    $('#img-display-data-table').DataTable();
  }
  });
}

function generateVolume()
{
  $('#volume_container').append('<div class="div_volume_binding"><div>  <input type="text" id="txt_volume_' + g_volume_counter + '"   size="12"></div><div>  <input type="text"  id="txt_cont_path_' + g_volume_counter + '" size="12"></div><div>  <select name="volume_type_' + g_volume_counter + '" id="volume_type_' + g_volume_counter + '">    <option value="volume">Volume</option><option value="bind">Bind</option>   </select></div><div>  <select  name="volume_perm_' + g_volume_counter + '"  id="volume_perm_' + g_volume_counter + '">    <option value="true">Read Only</option> <option value="false">Read Write</option>  </select>  <a  title="Generate Volume" href="#" onclick="generateVolume();return false;"><span style="font-size: 20px;left-margin:5px;">&#43;</span></a><a  title="Delete Volume" href="#" onclick="deleteVolume();return false;"><span style="font-size: 20px;left-margin:5px;">&#8722;</span></a></div></div>');
  g_volume_counter++;
}

function generatePort()
{
  $('#ports_container').append('<div class="div_port_binding"><div>  <input type="number" id="txt_host_port' + g_port_counter + '"  min="0" size="12"></div><div>  <input type="number"  id="txt_cont_port' + g_port_counter + '" min="0" size="12"></div><div><a  title="Generate Port" href="#" onclick="generatePort();return false;"><span style="font-size: 20px;left-margin:5px;">&#43;</span></a><a  title="Delete Port" href="#" onclick="deletePort();return false;"><span style="font-size: 20px;left-margin:5px;">&#8722;</span></a></div></div>');
  g_port_counter++;
}

function deletePort()
{
  $('#ports_container .div_port_binding').last().remove();
}

function deleteVolume()
{
  $('#volume_container .div_volume_binding').last().remove();
}





function generateExposePort()
{
  $('#div_port_mapping').append('<div class="div_exposed_port"><input type="number" id="exposed_ports_' + exposed_p_counter + '"     min="0"></input> <a  title="New port" href="#" onclick="generateExposePort();return false;"><span style="font-size: 20px;left-margin:5px;">&#43;</span></a><a  title="Delete Port" href="#" onclick="deleteExposedPort();return false;"><span style="font-size: 20px;left-margin:5px;">&#8722;</span></a></div>');
  exposed_p_counter++;
}



function deleteExposedPort()
{
$('#div_port_mapping .div_exposed_port').last().remove();
}


function containerOperations(op_type,par_id){

if (op_type == 'delete_image' || op_type == 'delete_container' || op_type == 'delete_unused' || op_type == 'delete_unused_networks')
{
  if (confirm('Are you sure?')) {
    //continue execution
} else {
throw new Error('Deletion aborted on user request');
}
}

  $('#div_dashboard').html('');
  $('#chart_div').html('');
  refreshdivDisp = false;
  let xhr = new XMLHttpRequest();
 xhr.open('POST', '/cont_operations',true);
 xhr.setRequestHeader("X-CSRFToken", csrftoken);
 xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');


 xhr.onload = function() {
 let divDisp=document.getElementById("div-right-pane");
 if (xhr.status === 200) {
 divDisp.innerHTML=xhr.responseText;

if (op_type=='list_networks')
{
  if ($('#contdata-network').length)
  {
    var str = $('#contdata-network').html();
var res = str.replace(/\[\'\//g,"");
var res2 = res.replace(/\'\]/g, "");
$('#contdata-network').html(res2);
    $('#contdata-network').DataTable();
  }
}

if (op_type=='connect_container_network')
{
  if ($('#contdata-contnetwork').length)
  {
var str = $('#contdata-contnetwork').html();
var res = str.replace(/\[\'\//g,"");
var res2 = res.replace(/\'\]/g, "");
$('#contdata-contnetwork').html(res2);
$('#contdata-contnetwork').DataTable();
  }
}

if (op_type=='create_container_form' || op_type=='update_container_form')
{

// When the user clicks on <span> (x), close the modal
var modal = document.getElementById("docker_create_modal");
var span = document.getElementsByClassName("close")[0];
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

}


if (op_type=='list_nodes')
{

 //Modal code

 // Get the modal

 modnum = document.getElementById("dict_len_txt").value;
 var i=1;
 for (i=1;i<=modnum;i++)
 {

 var modal = document.getElementById('myModal'+i.toString());
var modalspec = document.getElementById('myModalSpec'+i.toString());
var modalstatus = document.getElementById('myModalStatus'+i.toString());
var modalmanagerstatus = document.getElementById('myModalManagerStatus'+i.toString());
var modalversion = document.getElementById('myModalVersion'+i.toString());



 // Get the button that opens the modal
 var btn = document.getElementById('myBtn'+i.toString());
var btnspec = document.getElementById('myBtnSpec'+i.toString());
var btnstatus = document.getElementById('myBtnStatus'+i.toString());
var btnmanagerstatus = document.getElementById('myBtnManagerStatus'+i.toString());
var btnversion = document.getElementById('myBtnVersion'+i.toString());



 // Get the <span> element that closes the modal
 var span = document.getElementsByClassName("close")[0];
 var span1 = document.getElementsByClassName("close")[1];
 var span2 = document.getElementsByClassName("close")[2];
 var span3 = document.getElementsByClassName("close")[3];
 var span4 = document.getElementsByClassName("close")[4];
 // When the user clicks on the button, open the modal
//console.log(btn);
 btn.onclick = function() {
 modal.style.display = "block";
 }
 btnspec.onclick = function() {
 modalspec.style.display = "block";
 }
 btnstatus.onclick = function() {
 modalstatus.style.display = "block";
 }
 btnmanagerstatus.onclick = function() {
 modalmanagerstatus.style.display = "block";
 }
 btnversion.onclick = function() {
 modalversion.style.display = "block";
 }
 // When the user clicks on <span> (x), close the modal
  span.onclick = function() {
   modalversion.style.display = "none";
 }

 span1.onclick = function() {
  //modal.style.display = "none";
  modalspec.style.display = "none";
}

span2.onclick = function() {
 modal.style.display = "none";
}
span3.onclick = function() {
modalstatus.style.display = "none";
}
span4.onclick = function() {
modalmanagerstatus.style.display = "none";
}
 // When the user clicks anywhere outside of the modal, close it
 window.onclick = function(event) {
   if (event.target == modal) {
     modal.style.display = "none";
   }
   if (event.target == modalspec) {
     modalspec.style.display = "none";
   }
   if (event.target == modalstatus) {
     modalstatus.style.display = "none";
   }
   if (event.target == modalmanagerstatus) {
     modalmanagerstatus.style.display = "none";
   }
   if (event.target == modalversion) {
     modalversion.style.display = "none";
   }
 }

}
}

  if (op_type=='delete_image')
 {
   //console.log($('#full_response').html());
 if ($('#full_response').html() != null){
    var jsonStr = $('#full_response').text();
    //console.log(jsonStr);
    var jsonObj = JSON.parse(jsonStr);
    var jsonPretty = JSON.stringify(jsonObj, null, '\t');
    //console.log(jsonPretty);
    $('#full_response').text(jsonPretty);
 }
}

 if (op_type=='inspect_container')
 {
     getTableFromJson();
 }

 if (op_type=='update_container')
 {

     getTableFromJson();
 }

 if (op_type=='disconnect_container_network' || op_type=='connect_container_network' || op_type=='container_stats' ||  op_type=='filesystem_changes' || op_type=='list_logs' || op_type=='list_all' || op_type=='restart_container' || op_type=='stop_container' || op_type=='kill_container' || op_type == "list_processes" || op_type == "start_container" || op_type == "update_name"  || op_type == "pause_container" || op_type == "unpause_container" || op_type == "create_container_from_image")
 {
       if ($('#contdata').html() != null){
       var str = $('#contdata').html();
     var res = str.replace(/\[\'\//g,"");
     var res2 = res.replace(/\'\]/g, "");
     $('#contdata').html(res2);
   }

   if ($('#contdata-start').html() != null){
   var str = $('#contdata-start').html();
 var res = str.replace(/\[\'\//g,"");
 var res2 = res.replace(/\'\]/g, "");
 $('#contdata-start').html(res2);
}


   if ($('#contdata-contnetwork').length){
   var str = $('#contdata-contnetwork').html();
   var res = str.replace(/\[\'\//g,"");
   var res2 = res.replace(/\'\]/g, "");
   $('#contdata-contnetwork').html(res2);
    $('#contdata-contnetwork').DataTable();
   }

if ($('#contdata').length)
{
  $('#contdata').DataTable();
}

 }

 if (op_type=='inspect_task' ||op_type=='inspect_service' ||op_type=='delete_unused_networks' ||op_type=='delete_network' ||op_type=='inspect_network' || op_type=='delete_volume' || op_type=='delete_unused' || op_type=='inspect_volume' || op_type=='create_volume' || op_type=='list_volumes' || op_type=='history_image' || op_type=='inspect_image' || op_type=='container_stats' || op_type=='filesystem_changes' || op_type == "list_processes" || op_type == "start_container" || op_type == "restart_container" || op_type == "stop_container" || op_type == "kill_container" || op_type == "update_name"  || op_type == "pause_container" || op_type == "unpause_container")
 {
   if ($('#pre_inspect_version').html() != null && $('#pre_inspect_version').text().length >0){
   var jsonObj = JSON.parse($('#pre_inspect_version').text());
   var jsonPretty = JSON.stringify(jsonObj, null, '\t');
   $('#pre_inspect_version').text(jsonPretty);
   //console.log(jsonPretty);
 }

if ($('#contdata-volumes').length && $('#contdata-volumes').html().length>0)
{
  $('#contdata-volumes').DataTable();
}

     if ($('#pre_inspect_task').html() != null && $('#pre_inspect_task').text().length >0){
   var jsonObj = JSON.parse($('#pre_inspect_task').text());
   var jsonPretty = JSON.stringify(jsonObj, null, '\t');
   $('#pre_inspect_task').text(jsonPretty);
  // console.log(jsonPretty);
 }


     if ($('#pre_inspect_volumes').html() != null && $('#pre_inspect_volumes').text().length >0){
     var jsonObj = JSON.parse($('#pre_inspect_volumes').text());
     var jsonPretty = JSON.stringify(jsonObj, null, '\t');
     $('#pre_inspect_volumes').text(jsonPretty);

   }




   if ($('#pre_inspect_network').html() != null && $('#pre_inspect_network').text().length >0){
   var jsonObj = JSON.parse($('#pre_inspect_network').text());
   var jsonPretty = JSON.stringify(jsonObj, null, '\t');
   $('#pre_inspect_network').text(jsonPretty);

 }

   if ($('#pre_volumes_response').html() != null && $('#pre_volumes_response').text().length >0){
   var jsonObj = JSON.parse($('#pre_volumes_response').text());
   var jsonPretty = JSON.stringify(jsonObj, null, '\t');
   $('#pre_volumes_response').text(jsonPretty);

 }



   if ($('#pre_list_volumes').html() != null && $('#pre_list_volumes').text().length >0){
   var jsonObj = JSON.parse($('#pre_list_volumes').text());
   var jsonPretty = JSON.stringify(jsonObj, null, '\t');
   $('#pre_list_volumes').text(jsonPretty);

 }

   if ($('#pre_processes').html() != null && $('#pre_inspect_image').text().length >0){
   var str = $('#pre_processes').html();
   var res = str.replace(/b\'/g,"");
   var res2 = res.replace(/\\n\'/g, "");
   $('#pre_processes').html(res2);
   var jsonObj = JSON.parse($('#pre_processes').html());
   var jsonPretty = JSON.stringify(jsonObj, null, '\t');
   $('#pre_processes').text(jsonPretty);

   }

   if ($('#pre_processes').html() != null){
   var str = $('#pre_processes').html();
   var res = str.replace(/b\'/g,"");
   var res2 = res.replace(/\\n\'/g, "");
   $('#pre_processes').html(res2);
   var jsonObj = JSON.parse($('#pre_processes').html());
   var jsonPretty = JSON.stringify(jsonObj, null, '\t');
   $('#pre_processes').text(jsonPretty);

   }



if ($('#pre_inspect_image').text() != null && $('#pre_inspect_image').text().length >0){
 var jsonObj = JSON.parse($('#pre_inspect_image').text());
 var jsonPretty = JSON.stringify(jsonObj, null, '\t');
 $('#pre_inspect_image').text(jsonPretty);

}

if ($('#pre_create_volumes').text() != null && $('#pre_create_volumes').text().length >0){
 var jsonObj = JSON.parse($('#pre_create_volumes').text());
 var jsonPretty = JSON.stringify(jsonObj, null, '\t');
 $('#pre_create_volumes').text(jsonPretty);
}

if ($('#pre_create_network').text() != null && $('#pre_create_network').text().length >0){
 var jsonObj = JSON.parse($('#pre_create_network').text());
 var jsonPretty = JSON.stringify(jsonObj, null, '\t');
 $('#pre_create_network').text(jsonPretty);
}

if ($('.pre_created').text() != null){

 var len_time = $('#len_resp_dict_obj').text();
 //var len_time = 1;
 for (i=1;i<=len_time;i++)
 {

   let unix_timestamp = $('#pre_created'+i).text();
   //console.log(unix_timestamp);
   var date = new Date(unix_timestamp * 1000);
   $('#pre_created'+i).text(date);

 }

}

 }
   }
 else if (xhr.status !== 200) {
 divDisp.innerHTML='Request failed.  Returned status of ' + xhr.status;     } };
 if (op_type=='create_container_from_image')
 {
   //Validate container name
   containername = document.getElementById("containername").value;
   if (containername.length==1)
   {
     alert("The container name must start with alphanumeric character and cannot be one character long. The following can be used together with alphanumeric characters -, . or -");
     throw new Error("Bad container name");
   } else if (containername.length>1)
   {
     var code = containername.charCodeAt(0);
     if (!(code > 47 && code < 58) && // numeric (0-9)
         !(code > 64 && code < 91) && // upper alpha (A-Z)
         !(code > 96 && code < 123)) { // lower alpha (a-z)
           alert("The container name must start with alphanumeric character.");
           throw new Error("Bad container name");
     }
   }


let jsonStr='';
let port_bindings='';


/*
txt_host_port1 = document.getElementById("txt_host_port1").value;
txt_cont_port1 = document.getElementById("txt_cont_port1").value;
txt_host_port2 = document.getElementById("txt_host_port2").value;
txt_cont_port2 = document.getElementById("txt_cont_port2").value;



txt_volume_1 = document.getElementById("txt_volume_1").value;
txt_cont_path_1 = document.getElementById("txt_cont_path_1").value;
volume_perm_1 = document.getElementById("volume_perm_1").value;

txt_volume_2 = document.getElementById("txt_volume_2").value;
txt_cont_path_2 = document.getElementById("txt_cont_path_2").value;
volume_perm_2 = document.getElementById("volume_perm_2").value;




var line1_available = false;
var line1;

var line2_available = false;
var line2;



if (txt_host_port1.length>1 && txt_cont_port1.length>1)
{
       line1 = '"'+txt_cont_port1+'/tcp": [{"HostIp": "","HostPort": "'+txt_host_port1+'"}]';
       line1_available = true;
}


if (txt_host_port2.length>1 && txt_cont_port2.length>1)
{
       line2 = '"'+txt_cont_port2+'/tcp": [{"HostIp": "","HostPort": "'+txt_host_port2+'"}]';
       line2_available = true;
}

if (line1_available == true && line2_available == false)
{
 port_bindings = '"PortBindings": {'+ line1  +'}';
}else if (line1_available == false && line2_available == true)
{
 port_bindings = '"PortBindings": {'+ line2  +'}';
}

else if (line1_available == true && line2_available == true)
{
 port_bindings = '"PortBindings": {'+ line1 + ',' + line2 +'}';
}

else
{
 port_bindings = '';
}
*/

//console.log(port_bindings);
let port_line = '';
let i = 1;

for (i=1;i<g_port_counter;i++)
{
let host_port='txt_host_port'+i;
let cont_port='txt_cont_port'+i;
if($('#'+host_port).length > 0 && $('#'+cont_port).length > 0){
if($('#'+host_port).val().length > 0 && $('#'+cont_port).val().length > 0){

if (port_line.length > 0)
{
  port_line = port_line + ',' + '"'+$('#'+cont_port).val()+'/tcp": [{"HostIp": "","HostPort": "'+$('#'+host_port).val()+'"}]';
}
else {
  port_line = '"'+$('#'+cont_port).val()+'/tcp": [{"HostIp": "","HostPort": "'+$('#'+host_port).val()+'"}]';

}

}
}

}

if (port_line.length > 0)
{
  port_bindings = '"PortBindings": {'+ port_line +'}';
}
else
{
 port_bindings = '';
}



//var vol_str =    '"Mounts": [{"Target":   "'+ txt_cont_path_1 +'","Source":   "'+ txt_volume_1 +'","Type":     "volume","ReadOnly": '+ volume_perm_1 +'}]';


let vol_str = '';
//let vol_str_2 = '';
let vol_full_str = '';


let j = 1;
for (j=1;j<g_volume_counter;j++)
{
let txt_volume='txt_volume_'+j;
let txt_cont_path='txt_cont_path_'+j;
let volume_perm='volume_perm_'+j;
let volume_type='volume_type_'+j;

if($('#'+txt_volume).length > 0 && $('#'+txt_cont_path).length > 0 && $('#'+volume_perm).length > 0){
if($('#'+txt_volume).val().length > 0 && $('#'+txt_cont_path).val().length > 0 && $('#'+volume_perm).val().length > 0){

if (vol_str.length > 0)
{
  vol_str =  vol_str + ',' + '{"Target":   "'+ $('#'+txt_cont_path).val() +'","Source":   "'+ $('#'+txt_volume).val() +'","Type":     "'+ $('#'+volume_type).val() +'","ReadOnly": '+ $('#'+volume_perm).val() +'}';
}
else {
  vol_str =    '{"Target":   "'+ $('#'+txt_cont_path).val() +'","Source":   "'+ $('#'+txt_volume).val() +'","Type":     "'+ $('#'+volume_type).val() +'","ReadOnly": '+ $('#'+volume_perm).val() +'}';
}

}
}

}

if (vol_str.length > 0)
{
  vol_full_str = '"Mounts": ['+ vol_str +']';
}
else
{
 vol_full_str = '';
}


if (port_bindings.length > 1 && vol_full_str.length > 1)
{
 jsonStr = '{' + vol_full_str + ',' + port_bindings + '}';
}

if (port_bindings.length > 1 && vol_full_str.length == 0 )
{
 jsonStr = '{' + port_bindings + '}';
}

if (port_bindings.length == 0 && vol_full_str.length > 1 )
{
 jsonStr = '{' + vol_full_str + '}';
}


let exposedports_str = '';
let exposedports_json = '';

let e = 1;
for (e=1;e<exposed_p_counter;e++)
{
let exposed_ports = 'exposed_ports_'+e;
if($('#'+exposed_ports).length > 0 && $('#'+exposed_ports).val().length > 0){

if (exposedports_str.length > 0)
{
  exposedports_str = exposedports_str + ',' + '"'+ $('#'+exposed_ports).val() + '/tcp": {}';
}
else {
  exposedports_str = '"'+ $('#'+exposed_ports).val() + '/tcp": {}';
}

}
}

if (exposedports_str.length > 0)
{
  exposedports_json = '{' + exposedports_str + '}'
}


//console.log(exposedports_json);

let volumes_phdr='';
   xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&c_parentid='+document.getElementById("parentid").value+'&c_containername='+document.getElementById("containername").value+'&c_tty='+getRadioValue("Tty")+'&'+'c_containername='+document.getElementById("containername").value+'&'+'c_hostname='+document.getElementById("hostname").value+'&'+'c_domainname='+document.getElementById("domainname").value+'&'+'c_fusername='+document.getElementById("fusername").value+'&'+'c_attachstdin='+getRadioValue("AttachStdin")+'&'+'c_attachstdout='+getRadioValue("AttachStdout")+'&'+'c_attachstder='+getRadioValue("AttachStderr")+'&'+'c_exposedports='+exposedports_json+'&'+'c_tty='+getRadioValue("Tty")+'&'+'c_openstdin='+getRadioValue("OpenStdin")+'&'+'c_stdinonce='+getRadioValue("StdinOnce")+'&'+'c_env='+document.getElementById("Env").value+'&'+'c_cmd='+document.getElementById("Cmd").value+'&'+'c_healthcheck='+document.getElementById("Healthcheck").value+'&'+'c_argsescaped='+getRadioValue("ArgsEscaped")+'&'+'c_volumes='+volumes_phdr+'&'+'c_workingdir='+document.getElementById("WorkingDir").value+'&'+'c_entrypoint='+document.getElementById("Entrypoint").value+'&'+'c_networkdisabled='+getRadioValue("NetworkDisabled")+'&'+'c_macaddress='+document.getElementById("MacAddress").value+'&'+'c_onbuild='+document.getElementById("OnBuild").value+'&'+'c_labels='+document.getElementById("Labels").value+'&'+'c_stopsignal='+document.getElementById("StopSignal").value+'&'+'c_stoptimeout='+document.getElementById("StopTimeout").value+'&'+'c_shell='+document.getElementById("Shell").value+'&'+'c_hostconfig='+jsonStr+'&'+'c_networkingconfig='+document.getElementById("NetworkingConfig").value));
   //xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&c_parentid='+document.getElementById("parentid").value+'&c_containername='+document.getElementById("containername").value+'&c_tty='+getRadioValue("Tty")));
 }else if (op_type=='create_container_form')
 {
   xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id));
 }else if (op_type=='kill_container')
 {
   xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id));
 }

 else if (op_type=='view_log_task_form' ||op_type=='inspect_task' ||op_type=='list_tasks' ||op_type=='view_log_swarm_service_form' || op_type=='delete_swarm_service' ||op_type=='inspect_service' ||op_type=='create_service_form' ||op_type=='list_services' ||op_type=='inspect_node' ||op_type=='list_nodes' ||op_type=='unlock_manager_form' ||op_type=='get_the_unlock_key' ||  op_type=='initialize_new_swarm_form' ||  op_type=='inspect_swarm' ||op_type=='delete_unused_networks' || op_type=='create_network_form' || op_type=='delete_network' ||op_type=='list_networks' || op_type=='delete_unused' ||op_type=='list_volumes' || op_type=='history_image' || op_type=='inspect_image' ||op_type=='delete_image' ||  op_type=='export_container' || op_type=='container_stats' || op_type=='filesystem_changes' || op_type=='pause_container' || op_type=='unpause_container' || op_type=='list_processes' || op_type=='list_logs')
 {
      xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id));
 }

 else if (op_type=='update_swarm_node_form')
 {
   txt_swarm_node_id = document.getElementById("txt_swarm_node_id").value;
   txt_swarm_node_version = document.getElementById("txt_swarm_node_version").value;
   xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&txt_swarm_node_id='+txt_swarm_node_id+'&txt_swarm_node_version='+txt_swarm_node_version));
 }

 else if (op_type=='update_swarm_service_form')
 {
   txt_swarm_service_id = document.getElementById("txt_swarm_service_id").value;
   txt_swarm_service_version = document.getElementById("txt_swarm_service_version").value;
   xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&txt_swarm_service_id='+txt_swarm_service_id+'&txt_swarm_service_version='+txt_swarm_service_version));
 }

 else if (op_type=='update_swarm_node')
 {
   txt_swarm_node_idno = document.getElementById("txt_swarm_node_idno").value;
   txt_swarm_node_ver = document.getElementById("txt_swarm_node_ver").value;
   txt_swarm_node_name = document.getElementById("txt_swarm_node_name").value;
   txt_node_label = document.getElementById("txt_node_label").value;
   swarm_node_roles = document.getElementById("swarm_node_roles").value;
   swarm_node_availability = document.getElementById("swarm_node_availability").value;

   if (txt_node_label.length>1)
   {
     checkValidJson(txt_node_label,'Label');
   }
   xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&txt_swarm_node_idno='+txt_swarm_node_idno+'&txt_swarm_node_ver='+txt_swarm_node_ver+'&txt_swarm_node_name='+txt_swarm_node_name+'&txt_node_label='+txt_node_label+'&swarm_node_roles='+swarm_node_roles+'&swarm_node_availability='+swarm_node_availability));
 }

else if (op_type=='delete_node_form')
{
 xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id));
}
else if (op_type=='create_volume_form')
{
 xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id));
}

else if (op_type=='view_log_swarm_service')
{
details = getRadioValue('details');
follow = getRadioValue('follow');
stdout = getRadioValue('stdout');
stderr = getRadioValue('stderr');
timestamps = getRadioValue('timestamps');
txt_tail = document.getElementById("txt_tail").value;
xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&details='+details+'&follow='+follow+'&stdout='+stdout+'&stderr='+stderr+'&timestamps='+timestamps+'&txt_tail='+txt_tail));
}

else if (op_type=='view_log_task')
{
details = getRadioValue('details');
follow = getRadioValue('follow');
stdout = getRadioValue('stdout');
stderr = getRadioValue('stderr');
timestamps = getRadioValue('timestamps');
txt_tail = document.getElementById("txt_tail").value;
xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&details='+details+'&follow='+follow+'&stdout='+stdout+'&stderr='+stderr+'&timestamps='+timestamps+'&txt_tail='+txt_tail));
}
else if (op_type=='leave_swarm')
{
force_leave_swarm = getRadioValue('ForceLeaveSwarm');
xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&force_leave_swarm='+force_leave_swarm));
}
else if (op_type=='delete_swarm_node')
{
force_delete_swarm_node = getRadioValue('ForceNodeDelete');
xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&force_delete_swarm_node='+force_delete_swarm_node));
}
else if (op_type=='unlock_manager')
{
txt_unlock_key = document.getElementById('txt_unlock_key').value;
if (txt_unlock_key.length<1)
{
 alert("Unlock key cannot be blank.");
 throw new Error("Unlock key cannot be blank.");
}
xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&txt_unlock_key='+txt_unlock_key));
}


else if (op_type=='join_existing_swarm')
{
 txt_listen_address = document.getElementById('txt_listen_address').value;
 txt_advertise_address = document.getElementById('txt_advertise_address').value;
 txt_data_path_address = document.getElementById('txt_data_path_address').value;
 txt_remote_address = document.getElementById('txt_remote_address').value;
 txt_join_token = document.getElementById('txt_join_token').value;

if (txt_advertise_address.length<1)
{
 alert("Advertise address cannot be blank.");
 throw new Error("Advertise address cannot be blank.");
}

if (txt_join_token.length<1)
{
 alert("join token field cannot be blank.");
 throw new Error("join token field cannot be blank.");
}

 xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&txt_listen_address='+txt_listen_address+'&txt_advertise_address='+txt_advertise_address+'&txt_data_path_address='+txt_data_path_address+'&txt_remote_address='+txt_remote_address+'&txt_join_token='+txt_join_token));
}

else if (op_type=='update_swarm')
{
 txt_swarm_version = document.getElementById('txt_swarm_version').value;
 txt_rotate_worker_token = getRadioValue('rotateWorkerToken');
 txt_rotate_manager_token = getRadioValue('rotateManagerToken');
 txt_rotate_manager_key = getRadioValue('rotateManagerUnlockKey');
 txt_swarm_name = document.getElementById('txt_swarm_name').value;
 txt_swarm_labels = document.getElementById('txt_swarm_labels').value;
 txt_swarm_orchestration = document.getElementById('txt_swarm_orchestration').value;
 txt_swarm_raft_configuration = document.getElementById('txt_swarm_raft_configuration').value;
 txt_swarm_dispatcher = document.getElementById('txt_swarm_dispatcher').value;
 txt_swarm_caconfig = document.getElementById('txt_swarm_caconfig').value;
 txt_swarm_encryption_config = document.getElementById('txt_swarm_encryption_config').value;
 txt_swarm_task_defaults = document.getElementById('txt_swarm_task_defaults').value;

if (txt_swarm_version.length<1)
{
 alert("Swarm version cannot be blank.");
 throw new Error("Swarm version cannot be blank.");
}

 if (txt_swarm_labels.length>1)
 {
   checkValidJson(document.getElementById('txt_swarm_labels').value,'Labels');
 }
 if (txt_swarm_orchestration.length>1)
 {
   checkValidJson(document.getElementById('txt_swarm_orchestration').value,'Orchestration');
 }
 if (txt_swarm_raft_configuration.length>1)
 {
   checkValidJson(document.getElementById('txt_swarm_raft_configuration').value,'Raft configuration');
 }

 if (txt_swarm_dispatcher.length>1)
 {
   checkValidJson(document.getElementById('txt_swarm_dispatcher').value,'Swarm dispatcher');
 }

 if (txt_swarm_caconfig.length>1)
 {
   checkValidJson(document.getElementById('txt_swarm_caconfig').value,'CA config');
 }

 if (txt_swarm_encryption_config.length>1)
 {
   checkValidJson(document.getElementById('txt_swarm_encryption_config').value,'Encryption config');
 }

 if (txt_swarm_task_defaults.length>1)
 {
   checkValidJson(document.getElementById('txt_swarm_task_defaults').value,'Task defaults');
 }

 xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&txt_swarm_version='+txt_swarm_version+'&txt_rotate_worker_token='+txt_rotate_worker_token+'&txt_rotate_manager_token='+txt_rotate_manager_token+'&txt_rotate_manager_key='+txt_rotate_manager_key+'&txt_swarm_name='+txt_swarm_name+'&txt_swarm_labels='+txt_swarm_labels+'&txt_swarm_orchestration='+txt_swarm_orchestration+'&txt_swarm_raft_configuration='+txt_swarm_raft_configuration+'&txt_swarm_dispatcher='+txt_swarm_dispatcher+'&txt_swarm_caconfig='+txt_swarm_caconfig+'&txt_swarm_encryption_config='+txt_swarm_encryption_config+'&txt_swarm_task_defaults='+txt_swarm_task_defaults));
}


else if (op_type=='create_new_service')
{
 txt_service_name = document.getElementById('txt_service_name').value;
 txt_service_labels = document.getElementById('txt_service_labels').value;
 txt_task_template = document.getElementById('txt_task_template').value;
 txt_scheduling_mode = document.getElementById('txt_scheduling_mode').value;
 txt_update_config = document.getElementById('txt_update_config').value;
 txt_rollback_config = document.getElementById('txt_rollback_config').value;
 txt_service_network = document.getElementById('txt_service_network').value;
 txt_endpoint_specification = document.getElementById('txt_endpoint_specification').value;




if (txt_task_template.length<1)
{
 alert("Task template cannot be blank.");
 throw new Error("Task template cannot be blank.");
}


 if (txt_service_labels.length>1)
 {
   checkValidJson(document.getElementById('txt_service_labels').value,'Labels');
 }

 if (txt_task_template.length>1)
 {
   checkValidJson(document.getElementById('txt_task_template').value,'Task Template');
 }

 if (txt_scheduling_mode.length>1)
 {
   checkValidJson(document.getElementById('txt_scheduling_mode').value,'Scheduling mode');
 }

 if (txt_update_config.length>1)
 {
   checkValidJson(document.getElementById('txt_update_config').value,'Update Config ');
 }

 if (txt_rollback_config.length>1)
 {
   checkValidJson(document.getElementById('txt_rollback_config').value,'Rollback Config ');
 }

 if (txt_service_network.length>1)
 {
   checkValidJson(document.getElementById('txt_service_network').value,'Networks');
 }

 if (txt_endpoint_specification.length>1)
 {
   checkValidJson(document.getElementById('txt_endpoint_specification').value,'Endpoint Spec');
 }
 xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&txt_service_name='+txt_service_name+'&txt_service_labels='+txt_service_labels+'&txt_task_template='+txt_task_template+'&txt_scheduling_mode='+txt_scheduling_mode+'&txt_update_config='+txt_update_config+'&txt_rollback_config='+txt_rollback_config+'&txt_service_network='+txt_service_network+'&txt_endpoint_specification='+txt_endpoint_specification));
}



else if (op_type=='update_swarm_service')
{
 txt_service_id = document.getElementById('txt_service_id').value;
 txt_service_version = document.getElementById('txt_service_version').value;
 registry_auth_from = document.getElementById('registry_auth_from').value;
 id_rollback = document.getElementById('id_rollback').value;
 txt_service_name = document.getElementById('txt_service_name').value;
 txt_service_labels = document.getElementById('txt_service_labels').value;
 txt_task_template = document.getElementById('txt_task_template').value;
 txt_scheduling_mode = document.getElementById('txt_scheduling_mode').value;
 txt_update_config = document.getElementById('txt_update_config').value;
 txt_rollback_config = document.getElementById('txt_rollback_config').value;
 txt_service_network = document.getElementById('txt_service_network').value;
 txt_endpoint_specification = document.getElementById('txt_endpoint_specification').value;
if (txt_task_template.length<1)
{
 alert("Task template cannot be blank.");
 throw new Error("Task template cannot be blank.");
}


 if (txt_service_labels.length>1)
 {
   checkValidJson(document.getElementById('txt_service_labels').value,'Labels');
 }

 if (txt_task_template.length>1)
 {
   checkValidJson(document.getElementById('txt_task_template').value,'Task Template');
 }

 if (txt_scheduling_mode.length>1)
 {
   checkValidJson(document.getElementById('txt_scheduling_mode').value,'Scheduling mode');
 }

 if (txt_update_config.length>1)
 {
   checkValidJson(document.getElementById('txt_update_config').value,'Update Config ');
 }

 if (txt_rollback_config.length>1)
 {
   checkValidJson(document.getElementById('txt_rollback_config').value,'Rollback Config ');
 }

 if (txt_service_network.length>1)
 {
   checkValidJson(document.getElementById('txt_service_network').value,'Networks');
 }

 if (txt_endpoint_specification.length>1)
 {
   checkValidJson(document.getElementById('txt_endpoint_specification').value,'Endpoint Spec');
 }
 xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&txt_service_name='+txt_service_name+'&txt_service_labels='+txt_service_labels+'&txt_task_template='+txt_task_template+'&txt_scheduling_mode='+txt_scheduling_mode+'&txt_update_config='+txt_update_config+'&txt_rollback_config='+txt_rollback_config+'&txt_service_network='+txt_service_network+'&txt_endpoint_specification='+txt_endpoint_specification+'&registry_auth_from='+registry_auth_from+'&id_rollback='+id_rollback+'&txt_service_id='+txt_service_id+'&txt_service_version='+txt_service_version));
}


else if (op_type=='initialize_new_swarm')
{
 txt_listen_address = document.getElementById('txt_listen_address').value;
 txt_advertise_address = document.getElementById('txt_advertise_address').value;
 txt_data_path_address = document.getElementById('txt_data_path_address').value;
 txt_data_path_port = document.getElementById('txt_data_path_port').value;
 txt_subnet_pools = document.getElementById('txt_subnet_pools').value;
 force_new_cluster = getRadioValue('ForceNewCluster');
 txt_subnet_size = document.getElementById('txt_subnet_size').value;
 txt_swarm_spec = document.getElementById('txt_swarm_spec').value;



if (txt_advertise_address.length<1)
{
 alert("Advertise address cannot be blank.");
 throw new Error("Advertise address cannot be blank.");
}

 if (!Number.isInteger(txt_data_path_port) && txt_data_path_port.length>1)
 {
   alert("Data path port should be a number or leave field blank.");
   throw new Error("Data path port should be a number or leave field blank.");
 }

 if (!Number.isInteger(txt_subnet_size) && txt_subnet_size.length>1)
 {
   alert("Subnet size should be a number or leave field blank.");
   throw new Error("Subnet size should be a number or leave field blank.");
 }

 if (txt_swarm_spec.length>1)
 {
   checkValidJson(document.getElementById('txt_swarm_spec').value,'Spec');
 }

 xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&txt_listen_address='+txt_listen_address+'&txt_advertise_address='+txt_advertise_address+'&txt_data_path_address='+txt_data_path_address+'&txt_data_path_port='+txt_data_path_port+'&txt_subnet_pools='+txt_subnet_pools+'&force_new_cluster='+force_new_cluster+'&txt_subnet_size='+txt_subnet_size+'&txt_swarm_spec='+txt_swarm_spec));
}

else if (op_type=='create_network')
{
 var networkname = document.getElementById("txt_network_name").value;
 var check_duplicate = getRadioValue('CheckDuplicate');
 var txt_driver_network = document.getElementById("txt_driver_network").value;
 var var_internal = getRadioValue('Internal');
 var var_attachable = getRadioValue('Attachable');
 var var_ingress = getRadioValue('Ingress');
 var txt_ipam = document.getElementById("txt_ipam").value;
 var var_enable_ipv6 = getRadioValue('EnableIPv6');
 var txt_options = document.getElementById("txt_options").value;
 var txt_label_opts = document.getElementById("txt_label_opts").value;


 if (txt_ipam.length>1)
 {
   checkValidJson(document.getElementById('txt_ipam').value,'IPAM');
 }

 if (txt_options.length>1)
 {
   checkValidJson(document.getElementById('txt_options').value,'Options');
 }

 if (txt_label_opts.length>1)
 {
   checkValidJson(document.getElementById('txt_label_opts').value,'Labels');
 }

 if (networkname.length==1)
 {
   alert("The network name must start with alphanumeric character and cannot be one character long. The following can be used together with alphanumeric characters -, . or -");
   throw new Error("Bad network name");
 }
 if (networkname.length<1)
 {
   alert("Enter a network name. The following can be used together with alphanumeric characters -, . or -");
   throw new Error("Bad network name");
 }
 xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&networkname='+networkname+'&check_duplicate='+check_duplicate+'&txt_driver_network='+txt_driver_network+'&var_internal='+var_internal+'&var_attachable='+var_attachable+'&var_ingress='+var_ingress+'&txt_ipam='+txt_ipam+'&var_enable_ipv6='+var_enable_ipv6+'&txt_options='+txt_options+'&txt_label_opts='+txt_label_opts));
 document.getElementById("btn_create_network").value="Wait...";
 document.getElementById("btn_create_network").disabled=true;
}





else if (op_type=='create_volume')
{
 volumename = document.getElementById("txt_volume_name").value;
 drivername = document.getElementById("txt_driver_name").value;
 driveropts = document.getElementById("txt_driver_opts").value;
 volumelabels = document.getElementById("txt_label_opts").value;


 if (driveropts.length>1)
 {
   checkValidJson(document.getElementById('txt_driver_opts').value,'DriverOpts');
 }

 if (volumelabels.length>1)
 {
   checkValidJson(document.getElementById('txt_label_opts').value,'DriverOpts');
 }

 if (volumename.length==1)
 {
   alert("The volume name must start with alphanumeric character and cannot be one character long. The following can be used together with alphanumeric characters -, . or -");
   throw new Error("Bad volume name");
 }
 if (volumename.length<1)
 {
   alert("Enter a volume name. The following can be used together with alphanumeric characters -, . or -");
   throw new Error("Bad volume name");
 }
 //alert('activity='+op_type+'&par_id='+par_id+'&volume_name='+volumename);
 xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&volume_name='+volumename+'&drivername='+drivername+'&driveropts='+driveropts+'&volumelabels='+volumelabels));
 document.getElementById("btn_create_volume").value="Wait...";
 document.getElementById("btn_create_volume").disabled=true;
}
 else if (op_type=='update_name')
{
 var text_box = 'newcontname'+par_id;
 var val_newname = document.getElementById(text_box).value;
   if (val_newname.length<1)
 {
   alert("The new name cannot be empty");
   throw new Error("The new name cannot be empty");
 }

 if (val_newname.length==1)
 {
   alert("The container name must start with alphanumeric character and cannot be one character long. The following can be used together with alphanumeric characters -, . or -");
   throw new Error("Bad container name");
 } else if (val_newname.length>1)
 {
   var code = val_newname.charCodeAt(0);
   if (!(code > 47 && code < 58) && // numeric (0-9)
       !(code > 64 && code < 91) && // upper alpha (A-Z)
       !(code > 96 && code < 123)) { // lower alpha (a-z)
         alert("The container name must start with alphanumeric character.");
         throw new Error("Bad container name");
   }
 }




 xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&newcontname='+document.getElementById(text_box).value.trim()));
}  else if (op_type=='start_container')
 {
   xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id));
 }else if (op_type=='stop_container')
 {
   xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id));
 } else if (op_type=='restart_container')
 {
   xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id));
 }else if (op_type=='rename_container_form')
 {

  //alert(par_id);

var hidden_tr = document.getElementById(par_id);
hidden_tr.style.display = "block";


 }else if (op_type=='list_all')
 {
   xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id));
 }else if (op_type=='update_swarm_form' ||op_type=='leave_swarm_form' ||op_type=='join_existing_swarm_form' || op_type=='disconnect_container_network' || op_type=='connect_container_network' ||op_type=='inspect_network' || op_type=='delete_container' || op_type=='update_container_form' || op_type=='inspect_container' || op_type=='inspect_volume' || op_type=='delete_volume')
 {
   xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id));
 }else if (op_type=='update_container')
 {
   sanitizeUpdateForm('txtcpushares','CPU Shares');
   sanitizeUpdateForm('txtmemory',' Memory ');
   sanitizeUpdateForm('txtblkioweight','BlkioWeight');
   sanitizeUpdateForm('txtCpuRealtimePeriod','CpuRealtimePeriod');
   sanitizeUpdateForm('txtCpuQuota','CpuQuota');
   sanitizeUpdateForm('txtCpuPeriod','CpuPeriod');
   sanitizeUpdateForm('txtCpuRealtimeRuntime','CpuRealtimeRuntime');
   sanitizeUpdateForm('txtKernelMemory','KernelMemory');
   sanitizeUpdateForm('txtKernelMemoryTCP','KernelMemoryTCP');
   sanitizeUpdateForm('txtMemoryReservation','MemoryReservation');

   sanitizeUpdateForm('txtPidsLimit','PidsLimit');
   sanitizeUpdateForm('txtIOMaximumBandwidth','IOMaximumBandwidth');
   sanitizeUpdateForm('txtIOMaximumIOps','IOMaximumIOps');
   sanitizeUpdateForm('txtCpuPercent','CpuPercent');
   sanitizeUpdateForm('txtCpuCount','CpuCount');

var valMemorySwap = (document.getElementById("txtMemorySwap").value).trim();
var intMemorySwap = parseInt(valMemorySwap, 10);

if (!Number.isInteger(intMemorySwap) && valMemorySwap.length>1)
{
 alert("MemorySwap should be a number or leave field blank.");
 throw new Error("MemorySwap should be a number or leave field blank.");
}


var valMemorySwappiness = (document.getElementById("txtMemorySwappiness").value).trim();
var intMemorySwappiness = parseInt(valMemorySwappiness, 10);

if (!Number.isInteger(intMemorySwappiness) && valMemorySwappiness.length>1)
{
 alert("MemorySwappiness should be a number or leave field blank.");
 throw new Error("MemorySwappiness should be a number or leave field blank.");
}
else {
 if (intMemorySwappiness<0 || intMemorySwappiness>100)
 {
   alert("MemorySwappiness should be a number between 0 and 100.");
   throw new Error("MemorySwappiness should be a number between 0 and 100.");
 }
}

var varNanoCPUs = (document.getElementById("txtNanoCPUs").value).trim();

if(!isNumber(varNanoCPUs) && varNanoCPUs.length >1){
 alert("NanoCPUs should be a number or leave field blank.");
 throw new Error("NanoCPUs should be a number or leave field blank.");
}




   checkValidJson(document.getElementById('blkioweightdevicearea').value,'BlkioWeightDevice');
   checkValidJson(document.getElementById('BlkioDeviceReadBpsarea').value,'BlkioDeviceReadBps');
   checkValidJson(document.getElementById('BlkioDeviceWriteBpsarea').value,'BlkioDeviceWriteBps');
   checkValidJson(document.getElementById('BlkioDeviceReadIOpsarea').value,'BlkioDeviceReadIOps');
   checkValidJson(document.getElementById('BlkioDeviceWriteIOpsarea').value,'BlkioDeviceWriteIOps');
   checkValidJson(document.getElementById('Devicesarea').value,'Devices');
   checkValidJson(document.getElementById('DeviceRequestsarea').value,'DeviceRequests');
   checkValidJson(document.getElementById('Ulimitsarea').value,'Ulimit');
   checkValidJson(document.getElementById('RestartPolicyarea').value,'RestartPolicy');

   let cpu_shares=(document.getElementById('txtcpushares').value).trim();
   let memory=(document.getElementById('txtmemory').value).trim();
   xhr.send(encodeURI('activity='+op_type+'&par_id='+par_id+'&'+'c_newname='+'NULL'+'&'+'c_cpu_shares='+cpu_shares+'&'+'c_memory='+memory+'&'+'c_groupparentarea='+(document.getElementById('cgroupparentarea').value).trim()+'&'+'BlkioDeviceReadBpsarea='+(document.getElementById('BlkioDeviceReadBpsarea').value).trim()+'&'+'BlkioDeviceWriteBpsarea='+(document.getElementById('BlkioDeviceWriteBpsarea').value).trim()+'&'+'BlkioDeviceReadIOpsarea='+(document.getElementById('BlkioDeviceReadIOpsarea').value).trim()+'&'+'txtCpuPeriod='+(document.getElementById('txtCpuPeriod').value).trim()+'&'+'txtCpuQuota='+(document.getElementById('txtCpuQuota').value).trim()+'&'+'txtCpuRealtimePeriod='+(document.getElementById('txtCpuRealtimePeriod').value).trim()+'&'+'txtCpuRealtimeRuntime='+document.getElementById('txtCpuRealtimeRuntime').value+'&'+'txtCpusetCpus='+(document.getElementById('txtCpusetCpus').value).trim()+'&'+'txtCpusetMems='+(document.getElementById('txtCpusetMems').value).trim()+'&'+'BlkioDeviceWriteIOpsarea='+(document.getElementById('BlkioDeviceWriteIOpsarea').value).trim()+'&'+'Devicesarea='+(document.getElementById('Devicesarea').value).trim()+'&'+'DeviceCgroupRulesarea='+(document.getElementById('DeviceCgroupRulesarea').value).trim()+'&'+'txtKernelMemory='+(document.getElementById('txtKernelMemory').value).trim()+'&'+'txtKernelMemoryTCP='+(document.getElementById('txtKernelMemoryTCP').value).trim()+'&'+'txtMemoryReservation='+(document.getElementById('txtMemoryReservation').value).trim()+'&'+'txtMemorySwap='+(document.getElementById('txtMemorySwap').value).trim()+'&'+'txtMemorySwappiness='+(document.getElementById('txtMemorySwappiness').value).trim()+'&'+'txtNanoCPUs='+(document.getElementById('txtNanoCPUs').value).trim()+'&'+'txtOomKillDisable='+getRadioValue('txtOomKillDisable')+'&'+'txtInit='+getRadioValue('txtInit')+'&'+'txtPidsLimit='+(document.getElementById('txtPidsLimit').value).trim()+'&'+'Ulimitsarea='+(document.getElementById('Ulimitsarea').value).trim()+'&'+'txtCpuCount='+document.getElementById('txtCpuCount').value+'&'+'txtCpuPercent='+document.getElementById('txtCpuPercent').value+'&'+'txtIOMaximumIOps='+document.getElementById('txtIOMaximumIOps').value+'&'+'txtIOMaximumBandwidth='+document.getElementById('txtIOMaximumBandwidth').value+'&'+'RestartPolicyarea='+document.getElementById('RestartPolicyarea').value+'&'+'DeviceRequestsarea='+(document.getElementById('DeviceRequestsarea').value).trim()+'&'+'BlkioWeight='+document.getElementById('txtblkioweight').value+'&'+'blkioweightdevicearea='+(document.getElementById('blkioweightdevicearea').value).trim()));
 }
 }

 function getRadioValue(theRadioGroup)
{
    var elements = document.getElementsByName(theRadioGroup);
    for (var i = 0, l = elements.length; i < l; i++)
    {
        if (elements[i].checked)
        {
            return elements[i].value;
        }
    }
}

function generateNetworkConfigJyson()
{


jsonStr = `
{
	"Bridge": "",
	"SandboxID": "",
	"HairpinMode": false,
	"LinkLocalIPv6Address": "",
	"LinkLocalIPv6PrefixLen": 0,
	"Ports": {},
	"SandboxKey": "",
	"SecondaryIPAddresses": null,
	"SecondaryIPv6Addresses": null,
	"EndpointID": "",
	"Gateway": "",
	"GlobalIPv6Address": "",
	"GlobalIPv6PrefixLen": 0,
	"IPAddress": "",
	"IPPrefixLen": 0,
	"IPv6Gateway": "",
	"MacAddress": "",
	"Networks": {
		"bridge": {
			"IPAMConfig": null,
			"Links": null,
			"Aliases": null,
			"NetworkID": "",
			"EndpointID": "",
			"Gateway": "",
			"IPAddress": "",
			"IPPrefixLen": 0,
			"IPv6Gateway": "",
			"GlobalIPv6Address": "",
			"GlobalIPv6PrefixLen": 0,
			"MacAddress": "",
			"DriverOpts": null
		}
	}
}

`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#NetworkingConfig").text(jsonPretty);
}

function sanitizeUpdateForm(txtbox,display_name)
{
  //CPU Shares

  var query = (document.getElementById(txtbox).value).trim();
  var additional_message = '';
  var error_message = display_name + " must be an integer or field should be blank to inherit default behaviour"
  if (query.length > 1)
  {
  var isNumeric=query.match(/^\d+$/);
   if(isNumeric){

     if (txtbox=='txtblkioweight' && (query<0 || query>1000))
     {
       var additional_message = error_message+". Secondly, BlkioWeight must be between 0 and 1000.";
       alert (additional_message);
       throw new Error(additional_message);

     }


   }else{

     alert (error_message+".");
     throw new Error(error_message+".");

   }
}

}


function checkValidJson(str,txtbox)
{
  if ((str.trim()).length > 1)
  {
    try {
      JSON.parse(str);
    }
    catch(e)
    {
      alert ("Text in "+txtbox+" should be valid json.");
      throw new Error("Text in "+txtbox+" should be valid json.");
    }
    return true;
  }
}


function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

function pullImage(op_type){

if (op_type=='pull_image' || op_type=='search_image')
{
  var txtname = document.getElementById("txt_pull_image").value;
  if(txtname.length==0)
  {
    alert("You have to enter name of image to pull e.g ubuntu:latest");
    throw new Error("You have to enter name of image to pull e.g ubuntu:latest");
  }
}
   	$('#div_dashboard').html('');
     $('#chart_div').html('');
   refreshdivDisp = false;
   let xhr = new XMLHttpRequest();
  xhr.open('POST', '/cont_operations',true);
  xhr.setRequestHeader("X-CSRFToken", csrftoken);
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onload = function() {
  let divDisp=document.getElementById("div-right-pane");
  if (xhr.status === 200) {
  divDisp.innerHTML=xhr.responseText;

if ($('#image_pull_result').html() != null){
   var jsonStr = $('#image_pull_result').text();
   //console.log(jsonStr);
   var jsonObj = JSON.parse(jsonStr);
   var jsonPretty = JSON.stringify(jsonObj, null, '\t');
   //console.log(jsonPretty);
   $('#image_pull_result').text(jsonPretty);
}

if ($('#img-search').length)
{
  $('#img-search').DataTable();
}
 }
  else if (xhr.status !== 200) {
  divDisp.innerHTML='Request failed.  Returned status of ' + xhr.status;     } };
  if (op_type =='pull_image_form')
  {
    xhr.send(encodeURI('activity=pull_image_form'));
  }
  if (op_type =='pull_image') {
    xhr.send(encodeURI('activity=pull_image&txt_pull_image='+document.getElementById("txt_pull_image").value));
    document.getElementById("btn_pull_image").value="Wait...";
    document.getElementById("btn_pull_image").disabled=true;

  }

  if (op_type =='search_image') {
    xhr.send(encodeURI('activity=search_image&txt_pull_image='+document.getElementById("txt_pull_image").value));
  }

  }



   function buildImageTarball(){
      let xhr = new XMLHttpRequest();
     let formdata=new FormData();
     let fileInput = document.getElementById('tarballfileupload').files[0];
     if(fileInput!=null ||fileInput!=undefined)
     {
   formdata.append("filename",fileInput);
   formdata.append("tagarea",document.getElementById('tagarea').value);
   formdata.append("activity","tar_uploaded");
    xhr.open('POST', '/cont_operations');
     xhr.send(formdata);
     xhr.onload = function() {
    let divDisp=document.getElementById("div-right-pane");
    if (xhr.status === 200) {
    divDisp.innerHTML=xhr.responseText;
    }
    else if (xhr.status !== 200) {
    divDisp.innerHTML='Request failed.  Returned status of ' + xhr.status;     } };
   }
   else {alert('You need to select a file');}
    }


function buildImage(op_type){


  if (op_type == 'delete_cache' || op_type == 'delete_unused_images')
  {
    if (confirm('Are you sure?')) {
      //continue execution
  } else {
  throw new Error('Deletion aborted on user request');
  }
  }


  if (op_type=='build_image' || op_type=='search_image')
  {
   var txtname = document.getElementById("txt_pull_image").value;
   if(txtname.length==0)
   {
     alert("You have to enter name of image to pull e.g ubuntu:latest");
     throw new Error("You have to enter name of image to pull e.g ubuntu:latest");
   }
  }
     $('#div_dashboard').html('');
      $('#chart_div').html('');
    refreshdivDisp = false;
    let xhr = new XMLHttpRequest();
   xhr.open('POST', '/cont_operations',true);
   xhr.setRequestHeader("X-CSRFToken", csrftoken);
   xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
   xhr.onload = function() {
   let divDisp=document.getElementById("div-right-pane");
   if (xhr.status === 200) {
   divDisp.innerHTML=xhr.responseText;

  if ($('#image_pull_result').html() != null){
    var jsonStr = $('#image_pull_result').text();
    //console.log(jsonStr);
    var jsonObj = JSON.parse(jsonStr);
    var jsonPretty = JSON.stringify(jsonObj, null, '\t');
    //console.log(jsonPretty);
    $('#image_pull_result').text(jsonPretty);
  }
  }
   else if (xhr.status !== 200) {
   divDisp.innerHTML='Request failed.  Returned status of ' + xhr.status;     } };
   if (op_type =='build_image_form')
   {
     xhr.send(encodeURI('activity=build_image_form'));
   }
   if (op_type =='render_build_image_form')
   {
     xhr.send(encodeURI('activity=render_build_image_form'));
   }

   if ( op_type=='delete_cache' ||op_type=='delete_unused_images')
   {
     xhr.send(encodeURI('activity='+op_type));
   }

if (op_type =='render_build_image_form_tarball')
{
  //alert(op_type);
  xhr.send(encodeURI('activity=render_build_image_form_tarball'));
}

   if (op_type =='build_image_submit')
   {
     xhr.send(encodeURI('activity=build_image_submit&c_dockerfilearea='+document.getElementById("dockerfilearea").value+'&'+'c_tagarea='+document.getElementById("tagarea").value));
     document.getElementById("submitbuild").value="Wait...";
     document.getElementById("submitbuild").disabled=true;

   }




   if (op_type =='pull_image') {
     xhr.send(encodeURI('activity=pull_image&txt_pull_image='+document.getElementById("txt_pull_image").value));
     document.getElementById("btn_pull_image").value="Wait...";
     document.getElementById("btn_pull_image").disabled=true;

   }

   if (op_type =='search_image') {
     xhr.send(encodeURI('activity=search_image&txt_pull_image='+document.getElementById("txt_pull_image").value));
   }

   }



















function pullImageFromSearch(img_name){
  refreshdivDisp = false;
  let xhr = new XMLHttpRequest();
 xhr.open('POST', '/cont_operations',true);
 xhr.setRequestHeader("X-CSRFToken", csrftoken);
 xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
 xhr.onload = function() {
 let divDisp=document.getElementById("div-right-pane");
 if (xhr.status === 200) {
 divDisp.innerHTML=xhr.responseText;

if ($('#image_pull_result').html() != null){
  var jsonStr = $('#image_pull_result').text();
  //console.log(jsonStr);
  var jsonObj = JSON.parse(jsonStr);
  var jsonPretty = JSON.stringify(jsonObj, null, '\t');
  //console.log(jsonPretty);
  $('#image_pull_result').text(jsonPretty);
}
}
 else if (xhr.status !== 200) {
 divDisp.innerHTML='Request failed.  Returned status of ' + xhr.status;     } };
 document.getElementById("wait_pull").style.display = "block";
 document.getElementById("pull_image").style.display = "none";
 document.getElementById("pull_image_ico").style.display = "none";
  xhr.send(encodeURI('activity=pull_image&txt_pull_image='+img_name));
 }




 function isAlphaNumeric(str) {
  var code, i, len;

  for (i = 0, len = str.length; i < len; i++) {
    code = str.charCodeAt(i);
    if (!(code > 47 && code < 58) && // numeric (0-9)
        !(code > 64 && code < 91) && // upper alpha (A-Z)
        !(code > 96 && code < 123)) { // lower alpha (a-z)
      return false;
    }
  }
  return true;
};


function networkSettings(txtarea,pre_area)
{
  document.getElementById(txtarea).style.display = 'block';
  document.getElementById(pre_area).style.display = 'block';
}

function networkOperations(op_type,network_id,cont_id,create_endpoint_config){
if(op_type=='network_disc')
{
  var force_net_delete=getRadioValue("Force"+cont_id);
}
else
{
  var send_endpoint_config = document.getElementById(create_endpoint_config).value;
  if (send_endpoint_config.length>1)
  {
    checkValidJson(document.getElementById(create_endpoint_config).value,'Network Settings');
  }
}


$('#div_dashboard').html('');
$('#chart_div').html('');
refreshdivDisp = false;
let xhr = new XMLHttpRequest();
xhr.open('POST', '/cont_operations',true);
xhr.setRequestHeader("X-CSRFToken", csrftoken);
xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
xhr.onload = function() {
let divDisp=document.getElementById("div-right-pane");
if (xhr.status === 200) {
divDisp.innerHTML=xhr.responseText;
}
else if (xhr.status !== 200) {
divDisp.innerHTML='Request failed.  Returned status of ' + xhr.status;     }
};

if(op_type=='network_disc')
{

  xhr.send(encodeURI('activity='+op_type+'&par_id='+network_id+'&cont_id='+cont_id+'&force_net_delete='+force_net_delete));

}
else {
  xhr.send(encodeURI('activity='+op_type+'&par_id='+network_id+'&cont_id='+cont_id+'&send_endpoint_config='+send_endpoint_config));

}

}


function getTableFromJson()
{
  jsonPretty("#state");
  jsonPretty("#host_config");
  jsonPretty("#graph_driver");
  jsonPretty("#network_settings");
  jsonPretty("#config");
  jsonPretty("#mounts");
  //jsonPretty("#pre_processes");

}

function jsonPretty(tdval)
{
var jsonStr = $(tdval).text();
//console.log(tdval);
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
//console.log(jsonPretty);
$(tdval).text(jsonPretty);
}

function generateVolumeLabels()
{
jsonStr = `
{
  "storage_type": "nfs",
  "application": "To be used with MySQL database",
  "owner": "African Software Group"
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#txt_label_opts").text(jsonPretty);
}

function generateDriverOpts()
{
jsonStr = `
{
  "type": "nfs",
  "device": "fsid123456.amazonaws.com:/",
  "o": "addr=fsid123456.amazonaws.com,nfsvers=4.0,rsize=4096,wsize=4096,hard,timeo=300,retrans=3"
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#txt_driver_opts").text(jsonPretty);
}

function generateEndpointOptions(txtarea)
{
jsonStr = `
{
"IPAMConfig": {
"IPv4Address": "172.24.56.89",
"IPv6Address": "2001:db8::5689"
}
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#"+txtarea).text(jsonPretty);
}

function generateIPAM()
{
jsonStr = `
{
"Driver": "default",
"Config": [
{
"Subnet": "172.20.0.0/16",
"IPRange": "172.20.10.0/24",
"Gateway": "172.20.10.11"
},
{
"Subnet": "2001:db8:abcd::/64",
"Gateway": "2001:db8:abcd::1011"
}
],
"Options": {
"foo": "bar"
}
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#txt_ipam").text(jsonPretty);
}


function generateNetworkOptions()
{
jsonStr = `
{
  "com.docker.network.bridge.default_bridge": "true",
  "com.docker.network.bridge.enable_icc": "true",
  "com.docker.network.bridge.enable_ip_masquerade": "true",
  "com.docker.network.bridge.host_binding_ipv4": "0.0.0.0",
  "com.docker.network.bridge.name": "docker0",
  "com.docker.network.driver.mtu": "1500"
  }
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#txt_options").text(jsonPretty);
}

function generateNetworkLabels()
{
jsonStr = `
{
  "network_use": "database",
  "organization": "Africa Software Group"
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#txt_label_opts").text(jsonPretty);
}

function generateSwarmSpec(txtarea)
{
jsonStr = `
{
"Orchestration": { },
"Raft": { },
"Dispatcher": { },
"CAConfig": { },
"EncryptionConfig": {
"AutoLockManagers": false
}
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#"+txtarea).text(jsonPretty);
}

function generateTaskTemplate(txtarea)
{
jsonStr = `
{
"ContainerSpec": {
"Image": "alpine"
},
"Resources": {
"Limits": { },
"Reservations": { }
},
"RestartPolicy": {
"Condition": "any",
"MaxAttempts": 0
},
"Placement": { },
"ForceUpdate": 0
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#"+txtarea).text(jsonPretty);
}


function generateTaskDefaults(txtarea)
{
jsonStr = `
{
"LogDriver": {
"Name": "json-file",
"Options": {
"max-file": "10",
"max-size": "100m"
}
}
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#"+txtarea).text(jsonPretty);
}

function generateCAConfig(txtarea)
{
jsonStr = `
{
"NodeCertExpiry": 7776000000000000,
"ExternalCAs": [
{
"Protocol": "cfssl",
"URL": "string",
"Options": {
"property1": "string",
"property2": "string"
},
"CACert": "string"
}
],
"SigningCACert": "string",
"SigningCAKey": "string",
"ForceRotate": 0
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#"+txtarea).text(jsonPretty);
}

function generateOrchestration(txtarea)
{
jsonStr = `
{
"TaskHistoryRetentionLimit": 10
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#"+txtarea).text(jsonPretty);
}

function generateDispatcher(txtarea)
{
jsonStr = `
{
"HeartbeatPeriod": 5000000000
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#"+txtarea).text(jsonPretty);
}

function generateOrchestration(txtarea)
{
jsonStr = `
{
"TaskHistoryRetentionLimit": 10
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#"+txtarea).text(jsonPretty);
}

function generateRaft(txtarea)
{
jsonStr = `
{
"SnapshotInterval": 10000,
"KeepOldSnapshots": 0,
"LogEntriesForSlowFollowers": 500,
"ElectionTick": 3,
"HeartbeatTick": 1
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#"+txtarea).text(jsonPretty);
}


function generateSwarmLabel(txtarea)
{
jsonStr = `
{
"organization": "African Software Group",
"department": "Sales"
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#"+txtarea).text(jsonPretty);
}

function generateSwarmSpec(txtarea)
{
jsonStr = `
{
"Orchestration": { },
"Raft": { },
"Dispatcher": { },
"CAConfig": { },
"EncryptionConfig": {
"AutoLockManagers": false
}
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#"+txtarea).text(jsonPretty);
}
function generateDispatcher(txtarea)
{
jsonStr = `
{
"HeartbeatPeriod": 5000000000
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#"+txtarea).text(jsonPretty);
}

function generateEncryptionConfig(txtarea)
{
jsonStr = `
{
"AutoLockManagers": false
}
`;
var jsonObj = JSON.parse(jsonStr);
var jsonPretty = JSON.stringify(jsonObj, null, '\t');
$("#"+txtarea).text(jsonPretty);
}





function dockerCreate()
{
  // Get the modal
  var modal = document.getElementById("docker_create_modal");

  // Get the button that opens the modal
  var btn = document.getElementById("btn_docker_create");

  // Get the <span> element that closes the modal

  modal.style.display = "block";
  create_full_str = '';
  if ($('#containername').val())
  {
    cont_name = $('#containername').val();
    create_full_str = create_full_str + ' --name ' + cont_name + ' ';
  }
  port_str='';
  for(i=1;i<=g_port_counter;i++)
  {
    host_port = 'txt_host_port'+i;
    cont_port = 'txt_cont_port'+i;
    if($('#'+host_port).val() && $('#'+cont_port).val())
    {
      if(port_str.length>1)
      {
      port_str = port_str + ' -p '+$('#'+host_port).val()+':'+$('#'+cont_port).val();
      }
      else
      {
        port_str = '-p '+$('#'+host_port).val()+':'+$('#'+cont_port).val();
      }

    }

  }

  if (port_str.length > 1)
  {
    create_full_str = create_full_str + port_str + ' ';
  }







  volume_str='';
    for(i=1;i<=g_volume_counter;i++)
  {
    host_volume = 'txt_volume_'+i;
    cont_volume = 'txt_cont_path_'+i;
    volume_perm = 'volume_perm_'+i;
    mount_type = 'volume_type_'+i;
    if($('#'+host_volume).val() && $('#'+cont_volume).val())
    {
      perm = 'rw';
      mnt = 'bind';



      if($('#'+mount_type).val()=='true')
      {
        perm = 'ro';
      }


      if($('#'+volume_perm).val()=='true')
      {
        perm = 'ro';
      }

      if(volume_str.length>1)
      {
      volume_str = volume_str + ' -v '+$('#'+host_volume).val()+':'+$('#'+cont_volume).val()+':'+perm;
      }
      else
      {
        volume_str = '-v '+$('#'+host_volume).val()+':'+$('#'+cont_volume).val()+':'+perm;
      }

    }

  }



  if (volume_str.length > 1)
  {
    create_full_str = create_full_str + volume_str + ' ';
  }






if($('#hostname').val())
{
  create_full_str = create_full_str + ' --hostname ' + $('#hostname').val() + ' ';
}

if($('#domainname').val())
{
  create_full_str = create_full_str + ' --domainname ' + $('#domainname').val() + ' ';
}

if($('#fusername').val())
{
  create_full_str = create_full_str + ' --user ' + $('#fusername').val() + ' ';
}

if (getRadioValue("AttachStdin") == 'true')
{
  create_full_str = create_full_str + ' --attach STDIN '
}

if (getRadioValue("AttachStdout") == 'true')
{
  create_full_str = create_full_str + ' --attach STDOUT '
}

if (getRadioValue("AttachStderr") == 'true')
{
  create_full_str = create_full_str + ' --attach STDERR '
}

port_str = '';
for(i=1;i<=exposed_p_counter;i++)
{
  exposed_port = 'exposed_ports_'+i;
  if($('#'+exposed_port).val())
  {

    if(port_str.length>1)
    {
    port_str = port_str + ' --expose '+$('#'+exposed_port).val()+' ';
    }
    else
    {
      port_str = ' --expose '+$('#'+exposed_port).val()+' ';
    }

  }

}

if (port_str.length > 1)
{
  create_full_str = create_full_str + port_str + ' ';
}

if (getRadioValue("Tty") == 'true')
{
  create_full_str = create_full_str + ' --tty '
}

if (getRadioValue("OpenStdin") == 'true')
{
  create_full_str = create_full_str + ' --interactive '
}



if($('#WorkingDir').val())
{
create_full_str = create_full_str + ' --workdir ' + $('#WorkingDir').val() + ' ' ;
}

if($('#Entrypoint').val())
{
create_full_str = create_full_str + ' --entrypoint ' + $('#Entrypoint').val() + ' ' ;
}

if($('#MacAddress').val())
{
create_full_str = create_full_str + ' --mac-address ' + $('#MacAddress').val() + ' ' ;
}

if($('#StopSignal').val())
{
create_full_str = create_full_str + ' --stop-signal ' + $('#StopSignal').val() + ' ' ;
}

if($('#StopTimeout').val())
{
create_full_str = create_full_str + ' --stop-timeout ' + $('#StopTimeout').val() + ' ' ;
}


  parentid = $('#parentid').val();
  create_full_str = 'docker create ' + create_full_str+' '+parentid;
  $('#docker_create_text').text(create_full_str);
}

function generateContainerUpdate()
{
  // Get the modal
  var modal = document.getElementById("docker_create_modal");

  // Get the button that opens the modal
  var btn = document.getElementById("btn_docker_update");

  // Get the <span> element that closes the modal

  modal.style.display = "block";
  create_full_str = '';
  if($('#txtcpushares').val())
  {
  create_full_str = create_full_str + ' --cpu-shares ' + $('#txtcpushares').val() + ' ' ;
  }

  if($('#txtmemory').val())
  {
  create_full_str = create_full_str + ' -m ' + $('#txtmemory').val() + ' ' ;
  }

  if($('#txtblkioweight').val())
  {
  create_full_str = create_full_str + ' --blkio-weight ' + $('#txtblkioweight').val() + ' ' ;
  }

  if($('#txtCpuPeriod').val())
  {
  create_full_str = create_full_str + ' --cpu-period ' + $('#txtCpuPeriod').val() + ' ' ;
  }

  if($('#txtCpuQuota').val())
  {
  create_full_str = create_full_str + ' --cpu-quota ' + $('#txtCpuQuota').val() + ' ' ;
  }

  if($('#txtCpuRealtimePeriod').val())
  {
  create_full_str = create_full_str + ' --cpu-rt-period ' + $('#txtCpuRealtimePeriod').val() + ' ' ;
  }

  if($('#txtCpuRealtimeRuntime').val())
  {
  create_full_str = create_full_str + ' --cpu-rt-runtime ' + $('#txtCpuRealtimeRuntime').val() + ' ' ;
  }

  if($('#txtCpuRealtimeRuntime').val())
  {
  create_full_str = create_full_str + ' --cpu-rt-runtime ' + $('#txtCpuRealtimeRuntime').val() + ' ' ;
  }

  if($('#txtCpusetCpus').val())
  {
  create_full_str = create_full_str + ' --cpuset-cpus ' + $('#txtCpusetCpus').val() + ' ' ;
  }

  if($('#txtCpusetMems').val())
  {
  create_full_str = create_full_str + ' --cpuset-mems ' + $('#txtCpusetMems').val() + ' ' ;
  }

  if($('#txtCpusetMems').val())
  {
  create_full_str = create_full_str + ' --cpuset-mems ' + $('#txtCpusetMems').val() + ' ' ;
  }

  if($('#txtKernelMemory').val())
  {
  create_full_str = create_full_str + ' --kernel-memory ' + $('#txtKernelMemory').val() + ' ' ;
  }

  if($('#txtMemoryReservation').val())
  {
  create_full_str = create_full_str + ' --memory-reservation ' + $('#txtMemoryReservation').val() + ' ' ;
  }

  if($('#txtMemorySwap').val())
  {
  create_full_str = create_full_str + ' --memory-swap ' + $('#txtMemorySwap').val() + ' ' ;
  }

  if($('#txtPidsLimit').val())
  {
  create_full_str = create_full_str + ' --pids-limit ' + $('#txtPidsLimit').val() + ' ' ;
  }

  if($('#RestartPolicyarea').val())
  {
  restartstr = '';
  str = $('#RestartPolicyarea').val()
  if (str.search("on-failure")!=-1)
  {
    restartstr = 'on-failure';
  }
  if (str.search("always")!=-1)
  {
    restartstr = 'always';
  }
  if (str.search("unless-stopped")!=-1)
  {
    restartstr = 'unless-stopped';
  }

  if (restartstr.length > 1)
  {
    create_full_str = create_full_str + ' --restart ' + restartstr + ' ' ;
  }

  }

  parentid = $('#parent_id').val();
  if (create_full_str.length > 1)
  {
  create_full_str = 'docker update ' + create_full_str+' '+parentid;
  $('#docker_create_text').text(create_full_str);
  }
  else {
    {
      $('#docker_create_text').text('No updates selected. Nothing to change.');
    }
  }
}


function generateRestartPolicy()
{
  jsonStr = `
  {
    "Name":"on-failure",
    "MaximumRetryCount":3
  }
  `;
  var jsonObj = JSON.parse(jsonStr);
  var jsonPretty = JSON.stringify(jsonObj, null, '\t');
  $("#RestartPolicyarea").text(jsonPretty);
}


function containerReload(cont_id)
{
  $.get('docker/container_dashboard', {cont_id:cont_id},function(response) {
  $('#cont-dashboard').html(response);
    });
}


window.setInterval(function(){
  if ($('#cont-dashboard').length)
  {
     var a = $('#var_cont_id').val();
    containerReload(a); // this will run after every 5 seconds

  }
}, 5000);

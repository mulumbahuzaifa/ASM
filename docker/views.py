from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Setting
from django.contrib.auth.decorators import login_required
import json
import os
#host_port = ''
#docker_version = ''
#try:
#    properties = Setting.objects.filter(afparam='docker_host')
#    host_port = properties[0].afvalue
#except Exception:
#    host_port = 'http://localhost:2375'

def afriProperty(af_filter,default):
	try:
		properties = Setting.objects.filter(afparam=af_filter)
		return properties[0].afvalue
	except Exception:
		return default

#host_port = afriProperty('docker_host','http://localhost:2375')+'/'+afriProperty('docker_version','v1.40')
# host_port=os.getenv('HOST_URL','http://172.17.0.1:2375')
host_port=os.getenv('HOST_URL','http://ec2-3-143-221-231.us-east-2.compute.amazonaws.com:2375')
class DockerRequest():
    """Class to send get and post request to docker"""

    def __init__(self, url):
        self.__url = url
        self.__c_error = ''
        self.__data = {}
    def getResponse(self):
        from urllib.request import urlopen
        try:
            with urlopen(self.__url) as response:
                self.__data.update({'info':json.loads(response.read())})
        except HTTPError as e:
            self.__data.update({'error':e})
        except URLError as e:
            self.__data.update({'error':e})
        except Exception as e:
            self.__data.update({'error':e})
            #self.__c_error = 'We were unable to connect to docker server. Check that it is up and reachable\n.'+e
        finally:
            return self.__data

@login_required
def index(request):
    data = {'app_title':afriProperty('app_title','ASM'),'docker_host':host_port}
    return render(request,'index.html',data)
'''
@login_required
def dashboard(request):
    c_error = ''
    info_data = ''
    mem_name_list = ''
    mem_val_list = ''
    data = DockerRequest(host_port+'/info').getResponse()
    data.update({'mem_name_list':['a','b']})
    data.update({'mem_val_list':[1,2]})
    data.update({'url':host_port+'/info'})
    return render(request,'dashboard.html',data)
'''

def containerDashboard(request):
    try:
        cont_id = request.GET.get("cont_id", None)
        data = {}
        from urllib.request import urlopen
        with urlopen(host_port+"/info") as response:
            source = response.read()
            data = json.loads(source)
            data.update({'info':data})
        mem_dict=[]
        with urlopen(host_port+"/containers/json") as c_response:
                c_source = c_response.read()
                c_data = json.loads(c_source)
        with urlopen(host_port+"/containers/json?all=true") as c_response_all:
                c_source_all = c_response_all.read()
                c_data_all = json.loads(c_source_all)
                data.update({'all_containers':c_data_all})
        c_data = [cont_id]
        for id in c_data:
                #c_id=id["Id"][0:12]
                c_id=id
                c_url = host_port+"/containers/"+c_id+"/stats?stream=false"
                with urlopen(c_url) as c_response:
                        c_source = c_response.read()
                        c_data = json.loads(c_source)
                        mem_stats = c_data['memory_stats']
                        network_stats = c_data['networks']
                        eth0 = network_stats['eth0']
                        rx_bytes = '{0:.2f}'.format((((eth0['rx_bytes'])/1024)))
                        tx_bytes = '{0:.2f}'.format((((eth0['tx_bytes'])/1024)))

                        values = [mem_stats['limit'], mem_stats['max_usage'],mem_stats['usage']]
                        mem_usage_no_cache = mem_stats['usage'] - mem_stats['stats']['cache']
                        mem_percent_raw = 100.0 * mem_usage_no_cache / mem_stats['limit']
                        mem_percent = '{0:.2f}'.format(mem_percent_raw)
                        c_name=c_data['name'].replace('/','')
                        c_id=c_data['id'][0:12]
                        mem_mib='{0:.2f}'.format((mem_usage_no_cache/1024)/1024)
                        #CPU STATS
                        cpu_stats = c_data['cpu_stats']
                        cpu_usage = cpu_stats['cpu_usage']
                        percpu = cpu_usage['percpu_usage']
                        items = sorted(cpu_stats['throttling_data'].items())
                        system_cpu_usage = cpu_stats['system_cpu_usage']
                        values = [cpu_usage['total_usage'], cpu_usage['usage_in_kernelmode'],cpu_usage['usage_in_usermode'], system_cpu_usage]
                        # CPU Percentage based on calculateCPUPercent Docker method
                        # https://github.com/docker/docker/blob/master/api/client/stats.go
                        cpu_percent = 0.0
                        if 'precpu_stats' in c_data:
                             precpu_stats = c_data['precpu_stats']
                             precpu_usage = precpu_stats['cpu_usage']
                             cpu_delta = cpu_usage['total_usage'] - precpu_usage['total_usage']
                             system_delta = system_cpu_usage - precpu_stats['system_cpu_usage']
                             if system_delta > 0 and cpu_delta > 0:
                                 cpu_percent = 100.0 * cpu_delta / system_delta * len(percpu)

                        mem_dict.append({"id":c_id,"name":c_name,"mem_mib":mem_mib,"mem_percent":mem_percent,"cpu_percent":cpu_percent,"rx_bytes":rx_bytes,"tx_bytes":tx_bytes})
        list_mem_name=[]
        list_mem_val=[]
        list_cpu_val=[]
        list_rx_bytes_val=[]
        list_tx_bytes_val=[]

        for item in mem_dict:
                list_mem_name.append(item["name"])
                list_mem_val.append(item["mem_percent"])
                list_cpu_val.append(item["cpu_percent"])
                list_rx_bytes_val.append(item["rx_bytes"])
                list_tx_bytes_val.append(item["tx_bytes"])
        data.update({"mem_val_list":list_mem_val})
        data.update({"mem_name_list":list_mem_name})
        data.update({"cpu_percent":list_cpu_val})
        data.update({"rx_bytes":list_rx_bytes_val})
        data.update({"tx_bytes":list_tx_bytes_val})
        data.update({"contattr":mem_dict})
        data.update({"cont_id":cont_id})
    except Exception as e:
        data.update({'error':e})
    finally:
        return render(request,'container_dashboard.html',data)



def dashboard(request):
    try:
        data = {}
        from urllib.request import urlopen
        with urlopen(host_port+"/info") as response:
            source = response.read()
            data = json.loads(source)
            data.update({'info':data})
        mem_dict=[]
        with urlopen(host_port+"/containers/json") as c_response:
                c_source = c_response.read()
                c_data = json.loads(c_source)
        with urlopen(host_port+"/containers/json?all=true") as c_response_all:
                c_source_all = c_response_all.read()
                c_data_all = json.loads(c_source_all)
                data.update({'all_containers':c_data_all})

        for id in c_data:
                c_id=id["Id"][0:12]
                c_url = host_port+"/containers/"+c_id+"/stats?stream=false"
                with urlopen(c_url) as c_response:
                        c_source = c_response.read()
                        c_data = json.loads(c_source)
                        mem_stats = c_data['memory_stats']
                        network_stats = c_data['networks']
                        eth0 = network_stats['eth0']
                        rx_bytes = '{0:.2f}'.format((((eth0['rx_bytes'])/1024)))
                        tx_bytes = '{0:.2f}'.format((((eth0['tx_bytes'])/1024)))

                        values = [mem_stats['limit'], mem_stats['max_usage'],mem_stats['usage']]
                        mem_usage_no_cache = mem_stats['usage'] - mem_stats['stats']['cache']
                        mem_percent_raw = 100.0 * mem_usage_no_cache / mem_stats['limit']
                        mem_percent = '{0:.2f}'.format(mem_percent_raw)
                        c_name=c_data['name'].replace('/','')
                        c_id=c_data['id'][0:12]
                        mem_mib='{0:.2f}'.format((mem_usage_no_cache/1024)/1024)
                        #CPU STATS
                        cpu_stats = c_data['cpu_stats']
                        cpu_usage = cpu_stats['cpu_usage']
                        percpu = cpu_usage['percpu_usage']
                        items = sorted(cpu_stats['throttling_data'].items())
                        system_cpu_usage = cpu_stats['system_cpu_usage']
                        values = [cpu_usage['total_usage'], cpu_usage['usage_in_kernelmode'],cpu_usage['usage_in_usermode'], system_cpu_usage]
                        # CPU Percentage based on calculateCPUPercent Docker method
                        # https://github.com/docker/docker/blob/master/api/client/stats.go
                        cpu_percent = 0.0
                        if 'precpu_stats' in c_data:
                             precpu_stats = c_data['precpu_stats']
                             precpu_usage = precpu_stats['cpu_usage']
                             cpu_delta = cpu_usage['total_usage'] - precpu_usage['total_usage']
                             system_delta = system_cpu_usage - precpu_stats['system_cpu_usage']
                             if system_delta > 0 and cpu_delta > 0:
                                 cpu_percent = 100.0 * cpu_delta / system_delta * len(percpu)

                        mem_dict.append({"id":c_id,"name":c_name,"mem_mib":mem_mib,"mem_percent":mem_percent,"cpu_percent":cpu_percent,"rx_bytes":rx_bytes,"tx_bytes":tx_bytes})
        list_mem_name=[]
        list_mem_val=[]
        list_cpu_val=[]
        list_rx_bytes_val=[]
        list_tx_bytes_val=[]

        for item in mem_dict:
                list_mem_name.append(item["name"])
                list_mem_val.append(item["mem_percent"])
                list_cpu_val.append(item["cpu_percent"])
                list_rx_bytes_val.append(item["rx_bytes"])
                list_tx_bytes_val.append(item["tx_bytes"])
        data.update({"mem_val_list":list_mem_val})
        data.update({"mem_name_list":list_mem_name})
        data.update({"cpu_percent":list_cpu_val})
        data.update({"rx_bytes":list_rx_bytes_val})
        data.update({"tx_bytes":list_tx_bytes_val})
        data.update({"contattr":mem_dict})
    except Exception as e:
        data.update({'error':e})
    finally:
        return render(request,'dashboard.html',data)

@login_required
def renderImages(request):
	request_error = False
	actual_error = ''
	try:
	    from urllib.request import urlopen
	    import datetime, pytz
	    with urlopen(host_port+"/images/json") as img_response:
	        img_source = img_response.read()
	        img_data = json.loads(img_source)
	        response_code = img_response.code
	        img_object = []
	        img_no = 0
	        for item in img_data:
	            img_no = img_no +1
	            img_id = item['Id'][7:18]
	            created_date = datetime.datetime.utcfromtimestamp(item['Created']).strftime('%Y-%m-%d %H:%M:%S')
	            img_lables = item['Labels']
	            img_parent_id = item['ParentId']
	            img_repo_tags = item['RepoTags']
	            img_shared_size = item['SharedSize']
	            img_size = item['Size']
	            img_virtual_size = item['VirtualSize']
	            img_object.append({"Id":img_id,"Created":created_date,"Labels":img_lables,"ParentId":img_parent_id,"RepoTags":img_repo_tags,"SharedSize":img_shared_size, "Size":img_size , "VirtualSize":img_virtual_size})
	    object = {"img_no":img_no,"img_json":img_object,"request_error":False,"actual_error":actual_error,"response_code":response_code}
	    return render(request,'imagesdisp.html',object)
	except Exception as e:
		actual_error = 'An error occurred: ' + str(e)
		object = {"request_error":True,"actual_error":actual_error}
		return render(request,'imagesdisp.html',object)

from django.views.decorators.csrf import csrf_exempt
@login_required
@csrf_exempt
def containerOperations(request):
    search_value = request.POST.get("activity", None)
    c_parameter = request.POST.get("par_id", None)
    c_parent_id = request.POST.get("c_parentid", None)
    c_containername = request.POST.get("c_containername", None)
    c_tty = request.POST.get("c_tty", None)
    c_hostname = request.POST.get("c_hostname", None)
    c_domainname = request.POST.get("c_domainname", None)
    c_fusername = request.POST.get("c_fusername", None)
    c_attachstdin = request.POST.get("c_attachstdin", None)
    c_attachstdout = request.POST.get("c_attachstdout", None)
    c_attachstder = request.POST.get("c_attachstder", None)
    c_exposedports = request.POST.get("c_exposedports", None)
    c_openstdin = request.POST.get("c_openstdin", None)
    c_stdinonce = request.POST.get("c_stdinonce", None)
    c_env = request.POST.get("c_env", None)
    c_cmd = request.POST.get("c_cmd", None)
    c_healthcheck = request.POST.get("c_healthcheck", None)
    c_argsescaped = request.POST.get("c_argsescaped", None)
    c_volumes = request.POST.get("c_volumes", None)
    c_workingdir = request.POST.get("c_workingdir", None)
    c_entrypoint = request.POST.get("c_entrypoint", None)
    c_networkdisabled = request.POST.get("c_networkdisabled", None)
    c_macaddress = request.POST.get("c_macaddress", None)
    c_onbuild = request.POST.get("c_onbuild", None)
    c_labels = request.POST.get("c_labels", None)
    c_stopsignal = request.POST.get("c_stopsignal", None)
    c_stoptimeout = request.POST.get("c_stoptimeout", None)
    c_shell = request.POST.get("c_shell", None)
    c_hostconfig = request.POST.get("c_hostconfig", None)
    c_networkingconfig = request.POST.get("c_networkingconfig", None)
    if (search_value == 'create_container_form'):
        object = {"c_activity":"build_create_form","c_parameter":c_parameter}
        return render(request,'container_ops.html',object)

#Tasks operations
    elif (search_value == 'view_log_task'):
        import json
        import requests
        details = request.POST.get("details", None)
        follow = request.POST.get("follow", None)
        stdout = request.POST.get("stdout", None)
        stderr = request.POST.get("stderr", None)
        timestamps = request.POST.get("timestamps", None)
        txt_tail = request.POST.get("txt_tail", None)
        if (len(txt_tail)>= 1):
            url_start = host_port+'/tasks/'+c_parameter+'/logs?details='+details+'&follow='+follow+'&stdout='+stdout+'&stderr='+stderr+'&timestamps='+timestamps+'&tail='+txt_tail
        else:
            url_start = host_port+'/tasks/'+c_parameter+'/logs?details='+details+'&follow='+follow+'&stdout='+stdout+'&stderr='+stderr+'&timestamps='+timestamps
        response = requests.get(url_start)
        object = {"len_resp":len(response.text),"url_start":url_start,"http_resp_code":response.status_code,"full_response":response.text,"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'tasks_ops.html',object)

    elif (search_value == 'view_log_task_form'):
        object = {"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'tasks_ops.html',object)
    elif (search_value == 'list_tasks'):
        import json
        import requests
        url_start = host_port+'/tasks'
        response = requests.get(url_start)
        resp_dict = json.loads(response.text)
        dict_len = len(resp_dict)
        object = {"dict_len":dict_len,"resp_dict":resp_dict,"http_resp_code":response.status_code,"full_response":response.text,"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'tasks_ops.html',object)
    elif (search_value == 'inspect_task'):
        import json
        import requests
        url_start = host_port+'/tasks/'+c_parameter
        response = requests.get(url_start)
        resp_dict = json.loads(response.text)
        task_id = resp_dict['ID']
        task_version = resp_dict['Version']['Index']
        dict_len = len(resp_dict)
        object = {"task_version":task_version,"task_id":task_id,"dict_len":dict_len,"resp_dict":resp_dict,"http_resp_code":response.status_code,"full_response":response.text,"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'tasks_ops.html',object)

#Service operations

    elif (search_value == 'view_log_swarm_service'):
        import json
        import requests
        details = request.POST.get("details", None)
        follow = request.POST.get("follow", None)
        stdout = request.POST.get("stdout", None)
        stderr = request.POST.get("stderr", None)
        timestamps = request.POST.get("timestamps", None)
        txt_tail = request.POST.get("txt_tail", None)
        if (len(txt_tail)>= 1):
            url_start = host_port+'/services/'+c_parameter+'/logs?details='+details+'&follow='+follow+'&stdout='+stdout+'&stderr='+stderr+'&timestamps='+timestamps+'&tail='+txt_tail
        else:
            url_start = host_port+'/services/'+c_parameter+'/logs?details='+details+'&follow='+follow+'&stdout='+stdout+'&stderr='+stderr+'&timestamps='+timestamps
        response = requests.get(url_start)
        object = {"len_resp":len(response.text),"url_start":url_start,"http_resp_code":response.status_code,"full_response":response.text,"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'services_ops.html',object)

    elif (search_value == 'view_log_swarm_service_form'):
        object = {"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'services_ops.html',object)

    elif (search_value == 'delete_swarm_service'):
        import json
        import requests
        url_start = host_port+'/services/'+c_parameter
        response = requests.delete(url_start)
        object = {"http_resp_code":response.status_code,"full_response":response.text,"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'services_ops.html',object)

    elif (search_value == 'update_swarm_service'):
        import pycurl, json
        from io import BytesIO
        c = pycurl.Curl()
        txt_service_id = request.POST.get("txt_service_id", None)
        txt_service_version = request.POST.get("txt_service_version", None)
        registry_auth_from = request.POST.get("registry_auth_from", None)
        id_rollback = request.POST.get("id_rollback", None)

        txt_service_name = request.POST.get("txt_service_name", None)
        txt_service_labels = request.POST.get("txt_service_labels", None)
        txt_task_template = request.POST.get("txt_task_template", None)
        txt_scheduling_mode = request.POST.get("txt_scheduling_mode", None)
        txt_update_config = request.POST.get("txt_update_config", None)
        txt_rollback_config = request.POST.get("txt_rollback_config", None)
        txt_service_network = request.POST.get("txt_service_network", None)
        txt_endpoint_specification = request.POST.get("txt_endpoint_specification", None)

        if (len(id_rollback)>= 1 and id_rollback=='previous'):
            url_start = host_port+'/services/'+txt_service_id+'/update?version='+txt_service_version+'&registryAuthFrom='+registry_auth_from+'&rollback='+id_rollback
        else:
            url_start = host_port+'/services/'+txt_service_id+'/update?version='+txt_service_version+'&registryAuthFrom='+registry_auth_from

        c.setopt(pycurl.URL, url_start)
        c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
        cont_data = {}

        if (len(txt_service_name)>= 1):
            cont_data.update({"Name":txt_service_name})
        if (len(txt_service_labels)>= 1):
            cont_data.update({"Labels":json.loads(txt_service_labels)})
        if (len(txt_task_template)>= 1):
            cont_data.update({"TaskTemplate":json.loads(txt_task_template)})
        if (len(txt_scheduling_mode)>= 1):
            cont_data.update({"Mode":json.loads(txt_scheduling_mode)})
        if (len(txt_update_config)>= 1):
            cont_data.update({"UpdateConfig":json.loads(txt_update_config)})
        if (len(txt_rollback_config)>= 1):
            cont_data.update({"RollbackConfig":json.loads(txt_rollback_config)})
        if (len(txt_service_network)>= 1):
            cont_data.update({"Networks":json.loads(txt_service_network)})
        if (len(txt_endpoint_specification)>= 1):
            cont_data.update({"EndpointSpec":json.loads(txt_endpoint_specification)})
        data = json.dumps(cont_data)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(pycurl.VERBOSE, 1)
        buffer = BytesIO()
        #c.setopt(c.WRITEDATA, b)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        time_taken = c.getinfo(pycurl.TOTAL_TIME)
        http_resp_code = c.getinfo(pycurl.HTTP_CODE)
        body = buffer.getvalue()
        resp_raw = body.decode('iso-8859-1')
        object = {"begin":"none","txt_service_id":txt_service_id}
        object.update({"c_activity":search_value})
        object.update({"full_response":resp_raw})
        object.update({"dict_resp":json.loads(resp_raw)})
        object.update({"c_parameter":c_parameter})
        object.update({"http_resp_code":http_resp_code})
        c.close()
        return render(request,'services_ops.html',object)

    elif (search_value == 'update_swarm_service_form'):
        txt_swarm_service_id = request.POST.get("txt_swarm_service_id", None)
        txt_swarm_service_version = request.POST.get("txt_swarm_service_version", None)
        object = {"txt_swarm_service_id":txt_swarm_service_id,"txt_swarm_service_version":txt_swarm_service_version,"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'services_ops.html',object)

    elif (search_value == 'inspect_service'):
        import json
        import requests
        url_start = host_port+'/services/'+c_parameter
        response = requests.get(url_start)
        resp_dict = json.loads(response.text)
        service_id = resp_dict['ID']
        service_version = resp_dict['Version']['Index']
        dict_len = len(resp_dict)
        object = {"service_version":service_version,"service_id":service_id,"dict_len":dict_len,"resp_dict":resp_dict,"http_resp_code":response.status_code,"full_response":response.text,"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'services_ops.html',object)

    elif (search_value == 'create_new_service'):
        import pycurl, json
        from io import BytesIO
        c = pycurl.Curl()
        txt_service_name = request.POST.get("txt_service_name", None)
        txt_service_labels = request.POST.get("txt_service_labels", None)
        txt_task_template = request.POST.get("txt_task_template", None)
        txt_scheduling_mode = request.POST.get("txt_scheduling_mode", None)
        txt_update_config = request.POST.get("txt_update_config", None)
        txt_rollback_config = request.POST.get("txt_rollback_config", None)
        txt_service_network = request.POST.get("txt_service_network", None)
        txt_endpoint_specification = request.POST.get("txt_endpoint_specification", None)
        url_start = host_port+'/services/create'
        c.setopt(pycurl.URL, url_start)
        c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
        cont_data = {}
        if (len(txt_service_name)>= 1):
            cont_data.update({"Name":txt_service_name})
        if (len(txt_service_labels)>= 1):
            cont_data.update({"Labels":json.loads(txt_service_labels)})
        if (len(txt_task_template)>= 1):
            cont_data.update({"TaskTemplate":json.loads(txt_task_template)})
        if (len(txt_scheduling_mode)>= 1):
            cont_data.update({"Mode":json.loads(txt_scheduling_mode)})
        if (len(txt_update_config)>= 1):
            cont_data.update({"UpdateConfig":json.loads(txt_update_config)})
        if (len(txt_rollback_config)>= 1):
            cont_data.update({"RollbackConfig":json.loads(txt_rollback_config)})
        if (len(txt_service_network)>= 1):
            cont_data.update({"Networks":json.loads(txt_service_network)})
        if (len(txt_endpoint_specification)>= 1):
            cont_data.update({"EndpointSpec":json.loads(txt_endpoint_specification)})
        data = json.dumps(cont_data)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(pycurl.VERBOSE, 1)
        buffer = BytesIO()
        #c.setopt(c.WRITEDATA, b)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        time_taken = c.getinfo(pycurl.TOTAL_TIME)
        http_resp_code = c.getinfo(pycurl.HTTP_CODE)
        body = buffer.getvalue()
        resp_raw = body.decode('iso-8859-1')
        object = {"begin":"none"}
        object.update({"c_activity":search_value})
        object.update({"full_response":resp_raw})
        object.update({"dict_resp":json.loads(resp_raw)})
        object.update({"c_parameter":c_parameter})
        object.update({"http_resp_code":http_resp_code})
        c.close()
        return render(request,'services_ops.html',object)
    elif (search_value == 'create_service_form'):
        object = {"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'services_ops.html',object)

    elif (search_value == 'list_services'):
        import json
        import requests
        url_start = host_port+'/services'
        response = requests.get(url_start)
        resp_dict = json.loads(response.text)
        dict_len = len(resp_dict)
        object = {"dict_len":dict_len,"resp_dict":resp_dict,"http_resp_code":response.status_code,"full_response":response.text,"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'services_ops.html',object)

#Node operations
    elif (search_value == 'list_nodes'):
        import json
        import requests
        url_start = host_port+'/nodes'
        response = requests.get(url_start)
        resp_dict = json.loads(response.text)
        dict_len = len(resp_dict)
        object = {"dict_len":dict_len,"resp_dict":resp_dict,"http_resp_code":response.status_code,"full_response":response.text,"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'node_ops.html',object)


    elif (search_value == 'update_swarm_node_form'):
        txt_swarm_node_id = request.POST.get("txt_swarm_node_id", None)
        txt_swarm_node_version = request.POST.get("txt_swarm_node_version", None)
        object = {"swarm_node_id":txt_swarm_node_id,"swarm_node_version":txt_swarm_node_version,"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'node_ops.html',object)
    elif (search_value == 'delete_node_form'):
        object = {"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'node_ops.html',object)
    elif (search_value == 'inspect_node'):
        import json
        import requests
        url_start = host_port+'/nodes/'+c_parameter
        response = requests.get(url_start)
        resp_dict = json.loads(response.text)
        node_id = resp_dict['ID']
        node_version = resp_dict['Version']['Index']
        dict_len = len(resp_dict)
        object = {"node_version":node_version,"node_id":node_id,"dict_len":dict_len,"resp_dict":resp_dict,"http_resp_code":response.status_code,"full_response":response.text,"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'node_ops.html',object)
    elif (search_value == 'delete_swarm_node'):
        import json
        import requests
        force_delete_swarm_node = request.POST.get("force_delete_swarm_node", None)
        url_start = host_port+'/nodes/'+c_parameter+'?force='+force_delete_swarm_node
        response = requests.delete(url_start)
        resp_dict = json.loads(response.text)
        dict_len = len(resp_dict)
        object = {"dict_len":dict_len,"resp_dict":resp_dict,"http_resp_code":response.status_code,"full_response":response.text,"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'node_ops.html',object)

    elif (search_value == 'update_swarm_node'):
        import pycurl, json
        from io import BytesIO
        c = pycurl.Curl()
        txt_swarm_node_idno = request.POST.get("txt_swarm_node_idno", None)
        txt_swarm_node_ver = request.POST.get("txt_swarm_node_ver", None)
        txt_swarm_node_name = request.POST.get("txt_swarm_node_name", None)
        txt_node_label = request.POST.get("txt_node_label", None)
        swarm_node_roles = request.POST.get("swarm_node_roles", None)
        swarm_node_availability = request.POST.get("swarm_node_availability", None)
        url_start = host_port+'/nodes/'+txt_swarm_node_idno+'/update?version='+txt_swarm_node_ver
        c.setopt(pycurl.URL, url_start)
        c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
        cont_data = {}
        if (len(txt_swarm_node_name)>= 1):
            cont_data.update({"Name":txt_swarm_node_name})
        if (len(txt_node_label)>= 1):
            cont_data.update({"Labels":json.loads(txt_node_label)})
        if (len(swarm_node_roles)>= 1):
            cont_data.update({"Role":swarm_node_roles})
        if (len(swarm_node_availability)>= 1):
            cont_data.update({"Availability":swarm_node_availability})
        data = json.dumps(cont_data)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(pycurl.VERBOSE, 1)
        buffer = BytesIO()
        #c.setopt(c.WRITEDATA, b)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        time_taken = c.getinfo(pycurl.TOTAL_TIME)
        http_resp_code = c.getinfo(pycurl.HTTP_CODE)
        body = buffer.getvalue()
        resp_raw = body.decode('iso-8859-1')
        object = {"begin":"none","node_id":txt_swarm_node_idno}
        object.update({"c_activity":search_value})
        object.update({"full_response":resp_raw})
        object.update({"c_parameter":c_parameter})
        object.update({"http_resp_code":http_resp_code})
        c.close()
        return render(request,'node_ops.html',object)



#Swarm operations

    elif (search_value == 'unlock_manager'):
        import pycurl, json
        from io import BytesIO
        c = pycurl.Curl()
        txt_unlock_key = request.POST.get("txt_unlock_key", None)
        url_start = host_port+'/swarm/unlockkey'
        c.setopt(pycurl.URL, url_start)
        c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
        cont_data = {"UnlockKey":txt_unlock_key}
        data = json.dumps(cont_data)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(pycurl.VERBOSE, 1)
        buffer = BytesIO()
        #c.setopt(c.WRITEDATA, b)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        time_taken = c.getinfo(pycurl.TOTAL_TIME)
        http_resp_code = c.getinfo(pycurl.HTTP_CODE)
        body = buffer.getvalue()
        resp_raw = body.decode('iso-8859-1')
        object = {"begin":"none"}
        object.update({"c_activity":search_value})
        object.update({"full_response":resp_raw})
        object.update({"c_parameter":c_parameter})
        object.update({"http_resp_code":http_resp_code})
        c.close()
        return render(request,'swarm_ops.html',object)






    elif (search_value == 'update_swarm'):
        import pycurl, json
        from io import BytesIO
        c = pycurl.Curl()
        txt_swarm_version = request.POST.get("txt_swarm_version", None)
        txt_rotate_worker_token = request.POST.get("txt_rotate_worker_token", None)
        txt_rotate_manager_token = request.POST.get("txt_rotate_manager_token", None)
        txt_rotate_manager_key = request.POST.get("txt_rotate_manager_key", None)
        txt_swarm_name = request.POST.get("txt_swarm_name", None)
        txt_swarm_labels = request.POST.get("txt_swarm_labels", None)
        txt_swarm_orchestration = request.POST.get("txt_swarm_orchestration", None)
        txt_swarm_raft_configuration = request.POST.get("txt_swarm_raft_configuration", None)
        txt_swarm_dispatcher = request.POST.get("txt_swarm_dispatcher", None)
        txt_swarm_caconfig = request.POST.get("txt_swarm_caconfig", None)
        txt_swarm_encryption_config = request.POST.get("txt_swarm_encryption_config", None)
        txt_swarm_task_defaults = request.POST.get("txt_swarm_task_defaults", None)
        url_start = host_port+'/swarm/update?version='+txt_swarm_version+'&rotateWorkerToken='+txt_rotate_worker_token+'&rotateManagerToken='+txt_rotate_manager_token+'&rotateManagerUnlockKey='+txt_rotate_manager_key
        c.setopt(pycurl.URL, url_start)
        c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
        cont_data = {}
        if (len(txt_swarm_name)>= 1):
            cont_data.update({"Name":txt_swarm_name})
        if (len(txt_swarm_labels)>= 1):
            cont_data.update({"Labels":json.loads(txt_swarm_labels)})
        if (len(txt_swarm_orchestration)>= 1):
            cont_data.update({"Orchestration":json.loads(txt_swarm_orchestration)})
        if (len(txt_swarm_raft_configuration)>= 1):
            cont_data.update({"Raft":json.loads(txt_swarm_raft_configuration)})
        if (len(txt_swarm_dispatcher)>= 1):
            cont_data.update({"Dispatcher":json.loads(txt_swarm_dispatcher)})
        if (len(txt_swarm_caconfig)>= 1):
            cont_data.update({"CAConfig":json.loads(txt_swarm_caconfig)})
        if (len(txt_swarm_encryption_config)>= 1):
            cont_data.update({"EncryptionConfig":json.loads(txt_swarm_encryption_config)})
        if (len(txt_swarm_task_defaults)>= 1):
            cont_data.update({"TaskDefaults":json.loads(txt_swarm_task_defaults)})
        data = json.dumps(cont_data)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(pycurl.VERBOSE, 1)
        buffer = BytesIO()
        #c.setopt(c.WRITEDATA, b)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        time_taken = c.getinfo(pycurl.TOTAL_TIME)
        http_resp_code = c.getinfo(pycurl.HTTP_CODE)
        body = buffer.getvalue()
        resp_raw = body.decode('iso-8859-1')
        object = {"begin":"none"}
        object.update({"c_activity":search_value})
        object.update({"full_response":resp_raw})
        object.update({"c_parameter":c_parameter})
        object.update({"http_resp_code":http_resp_code})
        c.close()
        return render(request,'swarm_ops.html',object)




    elif (search_value == 'leave_swarm'):
        import json
        import requests
        force_leave_swarm = request.POST.get("force_leave_swarm", None)
        url_start = host_port+'/swarm/leave?force='+force_leave_swarm
        response = requests.post(url_start)
        object = {"http_resp_code":response.status_code,"full_response":response.text,"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'swarm_ops.html',object)
    elif (search_value == 'update_swarm_form'):
        object = {"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'swarm_ops.html',object)
    elif (search_value == 'join_existing_swarm_form'):
        object = {"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'swarm_ops.html',object)

    elif (search_value == 'unlock_manager_form'):
        object = {"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'swarm_ops.html',object)
    elif (search_value == 'get_the_unlock_key'):
        import json
        import requests
        url_start = host_port+'/swarm/unlockkey'
        response = requests.get(url_start)
        object = {"http_resp_code":response.status_code,"full_response":response.text,"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'swarm_ops.html',object)

    elif (search_value == 'initialize_new_swarm_form'):
        object = {"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'swarm_ops.html',object)
    elif (search_value == 'leave_swarm_form'):
        object = {"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'swarm_ops.html',object)
    elif (search_value == 'join_existing_swarm'):
        import pycurl, json
        from io import BytesIO
        c = pycurl.Curl()
        url_start = host_port+'/swarm/join'
        c.setopt(pycurl.URL, url_start)
        txt_listen_address = request.POST.get("txt_listen_address", None)
        txt_advertise_address = request.POST.get("txt_advertise_address", None)
        txt_data_path_address = request.POST.get("txt_data_path_address", None)
        txt_remote_address = request.POST.get("txt_remote_address", None)
        txt_join_token = request.POST.get("txt_join_token", None)
        c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
        cont_data = {"AdvertiseAddr": txt_advertise_address}
        if (len(txt_listen_address)>= 1):
            cont_data.update({"ListenAddr":txt_listen_address})
        if (len(txt_data_path_address)>= 1):
            cont_data.update({"DataPathAddr":txt_data_path_address})
        if (len(txt_remote_address)>= 1):
            cont_data.update({"RemoteAddrs":txt_remote_address})
        if (len(txt_join_token)>= 1):
            cont_data.update({"JoinToken":txt_join_token})
        data = json.dumps(cont_data)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(pycurl.VERBOSE, 1)
        buffer = BytesIO()
        #c.setopt(c.WRITEDATA, b)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        time_taken = c.getinfo(pycurl.TOTAL_TIME)
        http_resp_code = c.getinfo(pycurl.HTTP_CODE)
        body = buffer.getvalue()
        resp_raw = body.decode('iso-8859-1')
        object = {"begin":"none"}
        object.update({"c_activity":search_value})
        object.update({"full_response":resp_raw})
        object.update({"c_parameter":c_parameter})
        object.update({"http_resp_code":http_resp_code})
        c.close()
        return render(request,'swarm_ops.html',object)




    elif (search_value == 'initialize_new_swarm'):
        import pycurl, json
        from io import BytesIO
        c = pycurl.Curl()
        url_start = host_port+'/swarm/init'
        c.setopt(pycurl.URL, url_start)
        txt_listen_address = request.POST.get("txt_listen_address", None)
        txt_advertise_address = request.POST.get("txt_advertise_address", None)
        txt_data_path_address = request.POST.get("txt_data_path_address", None)
        txt_data_path_port = request.POST.get("txt_data_path_port", None)
        txt_subnet_pools = request.POST.get("txt_subnet_pools", None)
        force_new_cluster = request.POST.get("force_new_cluster", None)
        txt_subnet_size = request.POST.get("txt_subnet_size", None)
        txt_swarm_spec = request.POST.get("txt_swarm_spec", None)
        c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
        cont_data = {"AdvertiseAddr": txt_advertise_address}
        if (len(txt_listen_address)>= 1):
            cont_data.update({"ListenAddr":txt_listen_address})
        if (len(txt_data_path_address)>= 1):
            cont_data.update({"DataPathAddr":txt_data_path_address})
        if (len(txt_data_path_port)>= 1):
            cont_data.update({"DataPathPort":int(txt_data_path_port)})
        if (len(txt_subnet_pools)>= 1):
            cont_data.update({"DefaultAddrPool":txt_subnet_pools})
        if (len(force_new_cluster)>= 1):
            var_force_new_cluster = force_new_cluster
            if (var_force_new_cluster=="true"):
                var_force_new_cluster = True
            else:
                var_force_new_cluster = False
            cont_data.update({"ForceNewCluster":var_force_new_cluster})

        if (len(txt_swarm_spec)>= 1):
            cont_data.update({"Spec":json.loads(txt_swarm_spec)})
        data = json.dumps(cont_data)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(pycurl.VERBOSE, 1)
        buffer = BytesIO()
        #c.setopt(c.WRITEDATA, b)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        time_taken = c.getinfo(pycurl.TOTAL_TIME)
        http_resp_code = c.getinfo(pycurl.HTTP_CODE)
        body = buffer.getvalue()
        resp_raw = body.decode('iso-8859-1')
        object = {"begin":"none"}
        object.update({"c_activity":search_value})
        object.update({"full_response":resp_raw})
        object.update({"c_parameter":c_parameter})
        object.update({"http_resp_code":http_resp_code})
        c.close()
        return render(request,'swarm_ops.html',object)



    elif (search_value == 'inspect_swarm'):
        import json
        import requests
        url_start = host_port+'/swarm'
        response = requests.get(url_start)
        orig_response = response.text
        swarm_dict = json.loads(response.text)
        #swarm_id = swarm_dict['ID']
        object = {"code":response.status_code,"swarm_dict":swarm_dict,"orig_response":orig_response,"dict_len":len(swarm_dict),"c_activity":search_value,"full_response":orig_response,"c_parameter":c_parameter}
        return render(request,'swarm_ops.html',object)

#tar_uploaded
    elif (search_value == 'tar_uploaded'):
        import tempfile
        import shutil
        import os
        FILE_UPLOAD_DIR = 'data/'
        source = request.FILES['filename']
        c_tagarea = request.POST.get("tagarea", None)
        fd, filepath = tempfile.mkstemp(prefix=source.name, dir=FILE_UPLOAD_DIR)
        with open(filepath, 'wb') as dest:
            shutil.copyfileobj(source, dest)
        tag_len = len(c_tagarea)
        if (tag_len > 1):
            add_tag="/build?t="+c_tagarea
        else:
            add_tag="/build"
        import requests

        with open(filepath, 'rb') as f:
            data = f.read()
        response = requests.post(url=host_port+add_tag,
                    data=data,
                    headers={'Content-Type': 'application/tar'})
        j_response = response.text
        #j_response = full_tar_path
        object = {"tarfile":source,"url":host_port+add_tag,"j_response":j_response,"tag_len":tag_len,"c_activity":"tar_uploaded","tag":c_tagarea}

        #object = {"c_activity":"tar_uploaded","message":filepath}
        return render(request,'image_ops.html',object)
        os.remove(filepath)
#Delete Image
    elif (search_value == 'delete_cache' or search_value == 'delete_unused_images' or search_value == 'history_image' or search_value == 'delete_image' or search_value == 'inspect_image'):
        import requests
        import json
        resp_dict_obj = []
        if (search_value == 'delete_image'):
            url_start = host_port+'/images/'+c_parameter
            response = requests.delete(url_start)
        if (search_value == 'inspect_image'):
            url_start = host_port+'/images/'+c_parameter+'/json'
            response = requests.get(url_start)
        if (search_value == 'delete_cache'):
            url_start = host_port+'/build/prune?all=true'
            response = requests.post(url_start)
        if (search_value == 'delete_unused_images'):
            url_start = host_port+'/images/prune'
            response = requests.post(url_start)
        if (search_value == 'history_image'):
            url_start = host_port+'/images/'+c_parameter+'/history'
            response = requests.get(url_start)
            resp_dict = json.loads(response.text)
            for item in resp_dict:
                resp_dict_obj.append(item)
        resp = {"code":response.status_code}
        if (response.status_code == 200):
            object = {"len_resp_dict_obj":len(resp_dict_obj),"resp_dict_obj":resp_dict_obj,"url_start":url_start,"status_code":response.status_code,"full_response":response.text,"c_activity":search_value,"c_parameter":c_parameter,"resp":resp,"error":"","ostatus":"ok","response_dict":json.loads(response.text)}
        else:
            object = {"status_code":response.status_code,"full_response":response.text,"c_activity":search_value,"c_parameter":c_parameter,"resp":resp,"error":"Unable to delete. Error #D0001","ostatus":"notok"}
        return render(request,'image_ops.html',object)

#Network operations
    elif (search_value == 'create_network'):
            import pycurl, json
            from io import BytesIO
            c = pycurl.Curl()
            url_start = host_port+'/networks/create'
            c.setopt(pycurl.URL, url_start)
            networkname = request.POST.get("networkname", None)
            check_duplicate = request.POST.get("check_duplicate", None)
            txt_driver_network = request.POST.get("txt_driver_network", None)
            var_internal = request.POST.get("var_internal", None)
            var_attachable = request.POST.get("var_attachable", None)
            var_ingress = request.POST.get("var_ingress", None)
            txt_ipam = request.POST.get("txt_ipam", None)
            var_enable_ipv6 = request.POST.get("var_enable_ipv6", None)
            txt_options = request.POST.get("txt_options", None)
            txt_label_opts = request.POST.get("txt_label_opts", None)
            c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
            cont_data = {"Name": networkname}
            if (len(check_duplicate)>= 1):
                var_check_duplicate = check_duplicate
                if (var_check_duplicate=="true"):
                    var_check_duplicate = True
                else:
                    var_check_duplicate = False
                cont_data.update({"CheckDuplicate":var_check_duplicate})

            if (len(txt_driver_network)>= 1):
                cont_data.update({"Driver":txt_driver_network})

            if (len(var_internal)>= 1):
                var_internal = var_internal
                if (var_internal=="true"):
                    var_internal = True
                else:
                    var_internal = False
                cont_data.update({"Internal":var_internal})

            if (len(var_attachable)>= 1):
                var_attachable = var_attachable
                if (var_attachable=="true"):
                    var_attachable = True
                else:
                    var_attachable = False
                cont_data.update({"Attachable":var_attachable})

            if (len(var_ingress)>= 1):
                var_ingress = var_ingress
                if (var_ingress=="true"):
                    var_ingress = True
                else:
                    var_ingress = False
                cont_data.update({"Ingress":var_ingress})


            if (len(txt_ipam)>= 1):
                cont_data.update({"IPAM":json.loads(txt_ipam)})
            if (len(var_enable_ipv6)>= 1):
                var_enable_ipv6 = var_enable_ipv6
                if (var_enable_ipv6=="true"):
                    var_enable_ipv6 = True
                else:
                    var_enable_ipv6 = False
                cont_data.update({"EnableIPv6":var_enable_ipv6})

            if (len(txt_options)>= 1):
                cont_data.update({"Options":json.loads(txt_options)})

            if (len(txt_label_opts)>= 1):
                cont_data.update({"Labels":json.loads(txt_label_opts)})
            data = json.dumps(cont_data)
            c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.POSTFIELDS, data)
            c.setopt(pycurl.VERBOSE, 1)
            buffer = BytesIO()
            #c.setopt(c.WRITEDATA, b)
            c.setopt(c.WRITEDATA, buffer)
            c.perform()
            time_taken = c.getinfo(pycurl.TOTAL_TIME)
            http_resp_code = c.getinfo(pycurl.HTTP_CODE)
            body = buffer.getvalue()
            resp_raw = body.decode('iso-8859-1')
            object = {"begin":"none"}
            object.update({"c_activity":"create_network"})
            object.update({"full_response":resp_raw})
            object.update({"c_parameter":c_parameter})
            c.close()
            return render(request,'network_ops.html',object)

    elif (search_value == 'connect_container_network' or search_value == 'disconnect_container_network'):
        from urllib.request import urlopen
        import json
        cont_url = host_port+'/containers/json?all=true'
        with urlopen(cont_url) as cont_resp_response_list:
            cont_resp_source_l = cont_resp_response_list.read()
            cont_data_l = json.loads(cont_resp_source_l)
            resp = cont_data_l
            len_obj = len(resp)
            object = {"c_activity":search_value,"c_parameter":c_parameter,"resp":resp,"len":len_obj}
        return render(request,'network_ops.html',object)


    elif (search_value == 'list_all'):
        from urllib.request import urlopen
        import json
        if (c_parameter == 'none'):
            cont_url = host_port+'/containers/json?all=true'
        else:
            cont_url = host_port+'/containers/json?all=true&filters={"status":["'+c_parameter+'"]}'
        with urlopen(cont_url) as cont_resp_response_list:
            cont_resp_source_l = cont_resp_response_list.read()
            cont_data_l = json.loads(cont_resp_source_l)
            resp = cont_data_l
            len_obj = len(resp)
            if c_parameter == 'none':
                object = {"c_activity":"list_all","c_parameter":"","resp":resp,"len":len_obj}
            else:
                object = {"c_activity":"list_all","c_parameter":c_parameter,"resp":resp,"len":len_obj}
        return render(request,'container_ops.html',object)

    elif (search_value == 'network_disc'):
        import pycurl, json
        from io import BytesIO
        c = pycurl.Curl()
        url_start = host_port+'/networks/'+c_parameter+'/disconnect'
        cont_id = request.POST.get("cont_id", None)
        force_net_delete = request.POST.get("force_net_delete", None)
        c.setopt(pycurl.URL, url_start)
        c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
        cont_data = {"Container": cont_id}
        if (len(force_net_delete)>= 1):
            if(force_net_delete == 'true'):
                force_net_delete = True
            else:
                force_net_delete = False
            cont_data.update({"Force":force_net_delete})
        data = json.dumps(cont_data)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(pycurl.VERBOSE, 1)
        buffer = BytesIO()
        #c.setopt(c.WRITEDATA, b)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        time_taken = c.getinfo(pycurl.TOTAL_TIME)
        http_resp_code = c.getinfo(pycurl.HTTP_CODE)
        body = buffer.getvalue()
        resp_raw = body.decode('iso-8859-1')
        object = {"begin":"none"}
        object.update({"c_activity":"network_disc"})
        object.update({"full_response":resp_raw})
        object.update({"http_resp_code":http_resp_code})
        object.update({"c_parameter":c_parameter})
        c.close()
        return render(request,'network_ops.html',object)


    elif (search_value == 'container_network'):
        import pycurl, json
        from io import BytesIO
        c = pycurl.Curl()
        url_start = host_port+'/networks/'+c_parameter+'/connect'
        cont_id = request.POST.get("cont_id", None)
        send_endpoint_config = request.POST.get("send_endpoint_config", None)
        c.setopt(pycurl.URL, url_start)
        c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
        cont_data = {"Container": cont_id}
        if (len(send_endpoint_config)>= 1):
            cont_data.update({"EndpointConfig":json.loads(send_endpoint_config)})
        data = json.dumps(cont_data)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(pycurl.VERBOSE, 1)
        buffer = BytesIO()
        #c.setopt(c.WRITEDATA, b)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        time_taken = c.getinfo(pycurl.TOTAL_TIME)
        http_resp_code = c.getinfo(pycurl.HTTP_CODE)
        body = buffer.getvalue()
        resp_raw = body.decode('iso-8859-1')
        object = {"begin":"none"}
        object.update({"c_activity":"container_network"})
        object.update({"http_resp_code":http_resp_code})
        object.update({"full_response":resp_raw})
        object.update({"c_parameter":c_parameter})
        c.close()
        return render(request,'network_ops.html',object)



    elif (search_value == 'create_network_form'):
        object = {"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'network_ops.html',object)
    elif (search_value == 'list_networks'):
            import requests
            import json
            url_start = host_port+'/networks'
            response = requests.get(url_start)
            orig_response = response.text
            network_dict = json.loads(response.text)
            object = {"orig_response":orig_response,"network_dict":network_dict,"dict_len":len(network_dict),"c_activity":search_value,"full_response":response.text,"c_parameter":c_parameter}
            return render(request,'network_ops.html',object)
    elif (search_value == 'inspect_network'):
            import requests
            import json
            url_start = host_port+'/networks/'+c_parameter
            response = requests.get(url_start)
            orig_response = response.text
            network_dict = json.loads(response.text)
            object = {"orig_response":orig_response,"network_dict":network_dict,"dict_len":len(network_dict),"c_activity":search_value,"full_response":response.text,"c_parameter":c_parameter}
            return render(request,'network_ops.html',object)

    elif (search_value == 'delete_network'):
        import requests
        import json
        url_start = host_port+'/networks/'+c_parameter
        response = requests.delete(url_start)
        orig_response = response.text
        orig_code = response.status_code
        if (response.status_code == 204):
                url_start = host_port+'/networks'
                response = requests.get(url_start)
                network_dict = json.loads(response.text)
                object = {"network_dict":network_dict,"orig_code":orig_code,"orig_response":orig_response,"dict_len":len(network_dict),"c_activity":search_value,"full_response":response.text,"c_parameter":c_parameter}
        else:
                object = {"orig_code":orig_code,"response_code":response.status_code,"c_activity":search_value,"full_response":response.text,"c_parameter":c_parameter}
        return render(request,'network_ops.html',object)

    elif (search_value == 'delete_unused_networks'):
        import requests
        import json
        url_start = host_port+'/networks/prune'
        response = requests.post(url_start)
        orig_response = response.text
        orig_code = response.status_code
        if (response.status_code == 200):
                url_start = host_port+'/networks'
                response = requests.get(url_start)
                network_dict = json.loads(response.text)
                object = {"network_dict":network_dict,"orig_code":orig_code,"orig_response":orig_response,"dict_len":len(network_dict),"c_activity":search_value,"full_response":response.text,"c_parameter":c_parameter}
        else:
                object = {"orig_response":orig_response,"orig_code":orig_code,"response_code":response.status_code,"c_activity":search_value,"full_response":response.text,"c_parameter":c_parameter}
        return render(request,'network_ops.html',object)


#Volume operations
    elif (search_value == 'create_volume_form'):
        object = {"c_activity":search_value,"c_parameter":c_parameter}
        return render(request,'volume_ops.html',object)

    elif (search_value == 'delete_unused' or search_value == 'delete_volume' or search_value == 'list_volumes' or search_value == 'create_volume' or search_value == 'inspect_volume'):
        import requests
        import json
        resp_dict_obj = []
        if (search_value == 'delete_unused'):
            url_start = host_port+'/volumes/prune'
            response = requests.post(url_start)
            orig_response = response.text
            if (response.status_code == 200):
                url_start = host_port+'/volumes'
                response = requests.get(url_start)
                vol_dict = json.loads(response.text)
                vol_names = vol_dict['Volumes']
                object = {"orig_response":orig_response,"vol_names":vol_names,"dict_len":len(vol_names),"vol_dict":vol_dict,"c_activity":search_value,"full_response":response.text,"c_parameter":c_parameter}
                #object = {"response_code":response.status_code,"c_activity":search_value,"full_response":response.text,"c_parameter":c_parameter}
            else:
                object = {"response_code":response.status_code,"c_activity":search_value,"full_response":response.text,"c_parameter":c_parameter}

        if (search_value == 'delete_volume'):
            url_start = host_port+'/volumes/'+c_parameter
            response = requests.delete(url_start)
            orig_response = response.text
            if (response.status_code == 204):
                url_start = host_port+'/volumes'
                response = requests.get(url_start)
                vol_dict = json.loads(response.text)
                vol_names = vol_dict['Volumes']
                object = {"orig_response":orig_response,"vol_names":vol_names,"dict_len":len(vol_names),"vol_dict":vol_dict,"c_activity":search_value,"full_response":response.text,"c_parameter":c_parameter}
                #object = {"response_code":response.status_code,"c_activity":search_value,"full_response":response.text,"c_parameter":c_parameter}
            else:
                object = {"response_code":response.status_code,"c_activity":search_value,"full_response":response.text,"c_parameter":c_parameter}

        if (search_value == 'list_volumes'):
            url_start = host_port+'/volumes'
            response = requests.get(url_start)
            orig_response = response.text
            vol_dict = json.loads(response.text)
            vol_names = vol_dict['Volumes']
            object = {"orig_response":orig_response,"vol_names":vol_names,"dict_len":len(vol_names),"vol_dict":vol_dict,"c_activity":"list_volumes","full_response":response.text,"c_parameter":c_parameter}
        if (search_value == 'inspect_volume'):
            url_start = host_port+'/volumes/'+c_parameter
            response = requests.get(url_start)
            vol_dict = json.loads(response.text)
            object = {"vol_dict":vol_dict,"c_activity":search_value,"full_response":response.text,"c_parameter":c_parameter}

        if (search_value == 'create_volume'):
            import pycurl, json
            from io import BytesIO
            c = pycurl.Curl()
            url_start = host_port+'/volumes/create'
            c.setopt(pycurl.URL, url_start)
            volume_name = request.POST.get("volume_name", None)
            drivername = request.POST.get("drivername", None)
            driveropts = request.POST.get("driveropts", None)
            volumelabels = request.POST.get("volumelabels", None)
            c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
            cont_data = {"Name": volume_name}
            if (len(drivername)>= 1):
                cont_data.update({"Driver":drivername})
            if (len(driveropts)>= 1):
                cont_data.update({"DriverOpts":json.loads(driveropts)})
            if (len(volumelabels)>= 1):
                cont_data.update({"Labels":json.loads(volumelabels)})
            data = json.dumps(cont_data)
            c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.POSTFIELDS, data)
            c.setopt(pycurl.VERBOSE, 1)
            buffer = BytesIO()
            #c.setopt(c.WRITEDATA, b)
            c.setopt(c.WRITEDATA, buffer)
            c.perform()
            time_taken = c.getinfo(pycurl.TOTAL_TIME)
            http_resp_code = c.getinfo(pycurl.HTTP_CODE)
            body = buffer.getvalue()
            resp_raw = body.decode('iso-8859-1')
            object = {"begin":"none"}
            object.update({"c_activity":"create_volume"})
            object.update({"full_response":resp_raw})
            object.update({"c_parameter":c_parameter})
            c.close()
        return render(request,'volume_ops.html',object)

#Build Image from dockerfile
    elif (search_value == 'build_image_submit'):
        import os
        import random
        import string
        import tarfile
        c_dockerfilearea = request.POST.get("c_dockerfilearea", None)
        c_tagarea = request.POST.get("c_tagarea", None)
        #print("Tag Area",c_tagarea)
        tag_len = len(c_tagarea)
        if (tag_len > 1):
            add_tag="/build?t="+c_tagarea
        else:
            add_tag="/build"

        letters = string.ascii_letters
        result_str = ''.join(random.choice(letters) for i in range(12))
        dir_path = 'data/'+result_str
        os.mkdir(dir_path)
        f = open(dir_path+"/Dockerfile", "w")
        f.write(c_dockerfilearea)
        f.close()
        full_dir_path=dir_path
        full_file_path=dir_path+"/Dockerfile"
        fp = tarfile.open(full_dir_path+"/Dockerfile.tar","w")
        fp.add(full_file_path,arcname="Dockerfile")
        fp.close()
        full_tar_path=full_dir_path+"/Dockerfile.tar"
        #tar_path = "Content-Type:application/tar"+" "+"--data-binary"+" "+full_tar_path+" "+host_port+"/build"
        import requests

        with open(full_tar_path, 'rb') as f:
            data = f.read()
        response = requests.post(url=host_port+add_tag,
                    data=data,
                    headers={'Content-Type': 'application/tar'})

        import shutil
        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            print("Error: %s : %s" % (dir_path, e.strerror))
        #headers = {"Content-Type": "Content-Type:application/tar"}
        #response = requests.post(host_port+"/build/tag=ochi3", headers= headers, data=open(full_tar_path, "rb"))
        j_response = response.text
        #j_response = full_tar_path
        object = {"url":host_port+add_tag,"j_response":j_response,"tag_len":tag_len,"c_activity":search_value,"tag":c_tagarea,"dockerfile":c_dockerfilearea}

        return render(request,'image_ops.html',object)
#Generate Build Image Form
    elif (search_value == 'build_image_form' or search_value == 'render_build_image_form' or search_value == 'render_build_image_form_tarball'):
        object = {"c_activity":search_value}
        return render(request,'image_ops.html',object)
#Generate Pull Image Form
    elif (search_value == 'pull_image_form'):
        object = {"c_activity":"pull_image_form"}
        return render(request,'image_ops.html',object)
#Pull Image

    elif (search_value == 'pull_image'):
        image_name = request.POST.get("txt_pull_image", None)
        if ":" in image_name:
            good_image_name=image_name
        else:
            good_image_name=image_name+":latest"
        url_start = host_port+'/images/create?fromImage='+good_image_name
        import requests
        import json
        response = requests.post(url_start)
        resp = {"code":response.status_code}
        j_response = response.text
        if (response.status_code == 200):
            object = {"image_name":good_image_name,"status_code":response.status_code,"full_response":j_response,"c_activity":"pull_image"}
        else:
            object = {"image_name":good_image_name,"c_activity":"pull_image","status_code":response.status_code,"full_response":j_response}
        return render(request,'image_ops.html',object)

#Search Image

    elif (search_value == 'search_image'):
        image_name = request.POST.get("txt_pull_image", None)
        url_start = host_port+'/images/search?term='+image_name
        import requests
        import json
        response = requests.get(url_start)
        resp_load = json.loads(response.text)
        resp = {"code":response.status_code}
        j_response = response.text
        if (response.status_code == 200):
            object = {"url_start":url_start,"search_len":len(resp_load),"resp_load":resp_load,"image_name":image_name,"status_code":response.status_code,"full_response":j_response,"c_activity":"search_image"}
        else:
            object = {"url_start":url_start,"search_len":len(resp_load),"resp_load":resp_load,"image_name":image_name,"c_activity":"search_image","status_code":response.status_code,"full_response":j_response}
        return render(request,'image_ops.html',object)





#Delete a Container
    elif (search_value == 'delete_container'):
        url_start = host_port+'/containers/'+c_parameter
        import requests
        import json
        response = requests.delete(url_start)
        resp = {"code":response.status_code}
        if (response.status_code == 204):
            object = {"c_activity":"delete_container","c_parameter":c_parameter,"resp":resp,"error":"","ostatus":"ok"}
        else:
            object = {"c_activity":"delete_container","c_parameter":c_parameter,"resp":resp,"error":"Unable to delete. Error #D0001","ostatus":"notok"}
        return render(request,'container_ops.html',object)
#Inspect Container

    elif (search_value == 'inspect_container'):
        http_resp_code = 200
        if (http_resp_code == 200):
            import json
            cont_url = host_port+'/containers/'+c_parameter+'/json'
            from urllib.request import urlopen
            with urlopen(cont_url) as cont_resp_response:
                cont_resp_source = cont_resp_response.read()
                cont_data = json.loads(cont_resp_source)
                state = cont_data['State']
                state_j = json.dumps(state)
                host_config = cont_data['HostConfig']
                host_config_j = json.dumps(host_config)
                graph_driver = cont_data['GraphDriver']
                graph_driver_j = json.dumps(graph_driver)

                config = cont_data['Config']
                config_j = json.dumps(config)

                network_settings = cont_data['NetworkSettings']
                network_settings_j = json.dumps(network_settings)

                mounts = cont_data['Mounts']
                mounts_j = json.dumps(mounts)

                resp = json.dumps(cont_data)




                object = {"mounts":mounts_j,"config":config_j,"network_settings":network_settings_j,"graph_driver":graph_driver_j,"host_config":host_config_j,"state":state_j,"c_activity":"inspect_container","c_parameter":c_parameter,"c_parameter_len":len(c_parameter),"http_resp_code":http_resp_code,"resp":resp,"cont_data":cont_data}
                #object = {"c_activity":"_container","c_parameter":c_parameter,"http_resp_code":http_resp_code}
        #object = {"c_activity":"inspect_container","c_parameter":c_parameter,"http_resp_code":http_resp_code,"resp":resp}
        return render(request,'inspect.html',object)

#Update container
    elif (search_value == 'update_container'):
        object = {"begin":"none"}
        object.update({"c_activity":"update_container"})
        c_cpu_shares = request.POST.get("c_cpu_shares", None)
        c_memory = request.POST.get("c_memory", None)
        c_groupparentarea = request.POST.get("c_groupparentarea", None)
        BlkioDeviceReadBpsarea = request.POST.get("BlkioDeviceReadBpsarea", None)
        BlkioDeviceWriteBpsarea = request.POST.get("BlkioDeviceWriteBpsarea", None)
        BlkioDeviceReadIOpsarea = request.POST.get("BlkioDeviceReadIOpsarea", None)
        txtCpuPeriod = request.POST.get("txtCpuPeriod", None)
        txtCpuQuota = request.POST.get("txtCpuQuota", None)
        txtCpuRealtimePeriod = request.POST.get("txtCpuRealtimePeriod", None)
        txtCpuRealtimeRuntime = request.POST.get("txtCpuRealtimeRuntime", None)
        txtCpusetCpus = request.POST.get("txtCpusetCpus", None)
        txtCpusetMems = request.POST.get("txtCpusetMems", None)
        BlkioDeviceWriteIOpsarea = request.POST.get("BlkioDeviceWriteIOpsarea", None)
        Devicesarea = request.POST.get("Devicesarea", None)
        DeviceCgroupRulesarea = request.POST.get("DeviceCgroupRulesarea", None)
        txtKernelMemory = request.POST.get("txtKernelMemory", None)
        txtKernelMemoryTCP = request.POST.get("txtKernelMemoryTCP", None)
        txtMemoryReservation = request.POST.get("txtMemoryReservation", None)
        txtMemorySwap = request.POST.get("txtMemorySwap", None)
        txtMemorySwappiness = request.POST.get("txtMemorySwappiness", None)
        txtNanoCPUs = request.POST.get("txtNanoCPUs", None)
        txtOomKillDisable = request.POST.get("txtOomKillDisable", None)
        txtInit = request.POST.get("txtInit", None)
        txtPidsLimit = request.POST.get("txtPidsLimit", None)
        Ulimitsarea = request.POST.get("Ulimitsarea", None)
        txtCpuCount = request.POST.get("txtCpuCount", None)
        txtCpuPercent = request.POST.get("txtCpuPercent", None)
        txtIOMaximumIOps = request.POST.get("txtIOMaximumIOps", None)
        txtIOMaximumBandwidth = request.POST.get("txtIOMaximumBandwidth", None)
        RestartPolicyarea = request.POST.get("RestartPolicyarea", None)
        DeviceRequestsarea = request.POST.get("DeviceRequestsarea", None)
        BlkioWeight = request.POST.get("BlkioWeight", None)
        blkioweightdevicearea = request.POST.get("blkioweightdevicearea", None)

        import pycurl, json
        from io import BytesIO
        c = pycurl.Curl()
        c.setopt(pycurl.URL, host_port+'/containers/'+c_parameter+'/update')
        c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
        cont_data = {"Image":""}
        if (len(c_cpu_shares)>= 1):
            cont_data.update({"CpuShares":int(c_cpu_shares)})
        if (len(c_memory)>= 1):
            cont_data.update({"Memory":int(c_memory)})
        if (len(c_groupparentarea)>= 1):
            cont_data.update({"CgroupParent":c_groupparentarea})
        if (len(BlkioWeight)>= 1):
            cont_data.update({"BlkioWeight":int(BlkioWeight)})
        if (len(BlkioDeviceReadBpsarea)>= 1):
            cont_data.update({"BlkioDeviceReadBps":json.loads(BlkioDeviceReadBpsarea)})
        if (len(BlkioDeviceWriteBpsarea)>= 1):
            cont_data.update({"BlkioDeviceWriteBps":json.loads(BlkioDeviceWriteBpsarea)})
        if (len(blkioweightdevicearea)>= 1):
            cont_data.update({"BlkioWeightDevice":json.loads(blkioweightdevicearea)})
        if (len(BlkioDeviceReadIOpsarea)>= 1):
            cont_data.update({"BlkioDeviceReadIOps":json.loads(BlkioDeviceReadIOpsarea)})
        if (len(BlkioDeviceWriteIOpsarea)>= 1):
            cont_data.update({"BlkioDeviceWriteIOps":json.loads(BlkioDeviceWriteIOpsarea)})

        if (len(txtCpuRealtimePeriod)>= 1):
            cont_data.update({"CpuRealtimePeriod":int(txtCpuRealtimePeriod)})
        if (len(txtCpuQuota)>= 1):
            cont_data.update({"CpuQuota":int(txtCpuQuota)})
        if (len(txtCpuPeriod)>= 1):
            cont_data.update({"CpuPeriod":int(txtCpuPeriod)})
        if (len(txtCpuRealtimeRuntime)>= 1):
            cont_data.update({"CpuRealtimeRuntime":int(txtCpuRealtimeRuntime)})
        if (len(txtCpusetCpus)>= 1):
            cont_data.update({"CpusetCpus":txtCpusetCpus})
        if (len(txtCpusetMems)>= 1):
            cont_data.update({"CpusetMems":txtCpusetMems})
        if (len(Devicesarea)>= 1):
            cont_data.update({"Devices":json.loads(Devicesarea)})
        if (len(Ulimitsarea)>= 1):
            cont_data.update({"Ulimits":json.loads(Ulimitsarea)})

        if (len(RestartPolicyarea)>= 1):
            cont_data.update({"RestartPolicy":json.loads(RestartPolicyarea)})
        if (len(RestartPolicyarea)>= 1):
            cont_data.update({"RestartPolicy":json.loads(RestartPolicyarea)})

        if (len(txtCpuPercent)>= 1):
            cont_data.update({"CpuPercent":int(txtCpuPercent)})
        if (len(txtIOMaximumIOps)>= 1):
            cont_data.update({"IOMaximumIOps":int(txtIOMaximumIOps)})
        if (len(txtIOMaximumBandwidth)>= 1):
            cont_data.update({"IOMaximumBandwidth":int(txtIOMaximumBandwidth)})
        if (len(txtCpuCount)>= 1):
            cont_data.update({"CpuCount":int(txtCpuCount)})

        if (len(DeviceCgroupRulesarea)>= 1):
            cont_data.update({"DeviceCgroupRules":DeviceCgroupRulesarea.split(',')})
        if (len(DeviceRequestsarea)>= 1):
            cont_data.update({"DeviceRequests":json.loads(DeviceRequestsarea)})
        if (len(txtCpuQuota)>= 1):
            cont_data.update({"KernelMemory":int(txtKernelMemory)})

        if (len(txtCpuQuota)>= 1):
            cont_data.update({"PidsLimit":int(txtPidsLimit)})

        if (len(txtCpuQuota)>= 1):
            cont_data.update({"KernelMemoryTCP":int(txtKernelMemoryTCP)})
        if (len(txtCpuQuota)>= 1):
            cont_data.update({"MemoryReservation":int(txtMemoryReservation)})
        if (len(txtCpuQuota)>= 1):
            cont_data.update({"MemorySwap":int(txtMemorySwap)})
        if (len(txtCpuQuota)>= 1):
            cont_data.update({"MemorySwappiness":int(txtMemorySwappiness)})
        if (len(txtCpuQuota)>= 1):
            cont_data.update({"NanoCPUs":int(txtNanoCPUs)})
        if (len(txtOomKillDisable)>= 1):
            OomKillDisable = txtOomKillDisable
            if (OomKillDisable=="true"):
                OomKillDisable = True
            else:
                OomKillDisable = False
            cont_data.update({"OomKillDisable":OomKillDisable})

        if (len(txtInit)>= 1):
            Init = txtInit
            if (Init=="true"):
                Init = True
            else:
                Init = False
            cont_data.update({"Init":Init})

        data = json.dumps(cont_data)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(pycurl.VERBOSE, 1)
        buffer = BytesIO()
        #c.setopt(c.WRITEDATA, b)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        time_taken = c.getinfo(pycurl.TOTAL_TIME)
        http_resp_code = c.getinfo(pycurl.HTTP_CODE)
        body = buffer.getvalue()
        resp_raw = body.decode('iso-8859-1')
        object.update({"resp_raw":resp_raw})
        c.close()
        if (http_resp_code == 200):
            cont_url = host_port+'/containers/'+c_parameter+'/json'
            from urllib.request import urlopen
            with urlopen(cont_url) as cont_resp_response:
                cont_resp_source = cont_resp_response.read()
                cont_data = json.loads(cont_resp_source)
                #resp = cont_data
                state = cont_data['State']
                state_j = json.dumps(state)
                host_config = cont_data['HostConfig']
                host_config_j = json.dumps(host_config)
                graph_driver = cont_data['GraphDriver']
                graph_driver_j = json.dumps(graph_driver)
                config = cont_data['Config']
                config_j = json.dumps(config)
                network_settings = cont_data['NetworkSettings']
                network_settings_j = json.dumps(network_settings)
                resp = json.dumps(cont_data)


                #object = {"c_activity":"update_container","c_parameter":c_parameter,"http_resp_code":http_resp_code}
                #object = {"c_activity":"update_container","c_parameter":c_parameter,"http_resp_code":http_resp_code,"resp":resp}

                #object = {"config":config_j,"network_settings":network_settings_j,"graph_driver":graph_driver_j,"host_config":host_config_j,
                #"state":state_j,"c_activity":"update_container","c_parameter":c_parameter,"http_resp_code":http_resp_code,
                #"resp":resp,"cont_data":cont_data}
                object.update({"config":config_j})
                object.update({"network_settings":network_settings_j})
                object.update({"graph_driver":graph_driver_j})
                object.update({"host_config":host_config_j})
                object.update({"state":state_j})
                object.update({"c_parameter":c_parameter})
                object.update({"c_parameter_len":len(c_parameter)})
                object.update({"http_resp_code":http_resp_code})
                object.update({"resp":resp})
                object.update({"cont_data":cont_data})




                #object = {"c_activity":"_container","c_parameter":c_parameter,"http_resp_code":http_resp_code}
        #object = {"c_activity":"inspect_container","c_parameter":c_parameter,"http_resp_code":http_resp_code,"resp":resp}

        return render(request,'inspect.html',object)

#Generate Container form
    elif (search_value == 'update_container_form'):
        object = {"c_activity":"update_container_form","c_parameter":c_parameter}
        return render(request,'update_container_form.html',object)


    elif (search_value == 'restart_container'):
        url_start = host_port+'/containers/'+c_parameter+'/restart'
        import requests
        import json
        #data = {"name": "abc"}
        response = requests.post(url_start)
        content = response.content
        #resp = response.status_code
        #resp = response
        if (response.status_code == 204):
            from urllib.request import urlopen
            cont_url = host_port+'/containers/json?all=true&filters={"id":["'+c_parameter+'"]}'
            #c = 'http://127.0.0.1:2375/containers/json?all=true&filters={"id":["75accfaebfae"]}'
            with urlopen(cont_url) as cont_resp_response_list:
                cont_resp_source_l = cont_resp_response_list.read()
                cont_data_l = json.loads(cont_resp_source_l)
                resp = cont_data_l
                object = {"len_resp":len(resp),"content_len":len(content),"c_activity":"restart_container","c_parameter":c_parameter,"resp":resp,"content":content,"status_code":response.status_code}
        else: #Check if error occured
            object = {"content":content,"c_activity":"restart_container","c_parameter":c_parameter,"status_code":response.status_code}
        return render(request,'container_ops.html',object)


    elif (search_value == 'start_container'):
        url_start = host_port+'/containers/'+c_parameter+'/start'
        import requests
        import json
        #data = {"name": "abc"}
        response = requests.post(url_start)
        content = response.content
        #resp = response.status_code
        #resp = response
        if (response.status_code == 204):
            from urllib.request import urlopen
            cont_url = host_port+'/containers/json?all=true&filters={"id":["'+c_parameter+'"]}'
            #c = 'http://127.0.0.1:2375/containers/json?all=true&filters={"id":["75accfaebfae"]}'
            with urlopen(cont_url) as cont_resp_response_list:
                cont_resp_source_l = cont_resp_response_list.read()
                cont_data_l = json.loads(cont_resp_source_l)
                resp = cont_data_l
                object = {"len_resp":len(resp),"c_activity":"start_container","c_parameter":c_parameter,"resp":resp,"content":content,"status_code":response.status_code}
        else: #Check if error occured
            object = {"content":content,"c_activity":"start_container","c_parameter":c_parameter,"status_code":response.status_code}
        return render(request,'container_ops.html',object)

#Get processes running in a Containers
    elif (search_value == 'list_processes'):
        url_start = host_port+'/containers/'+c_parameter+'/top'
        import requests
        import json
        #data = {"name": "abc"}
        response = requests.get(url_start)
        content = response.content
        #print(url_start)
        #resp = response.status_code
        #resp = response
        if (response.status_code == 200):
            from urllib.request import urlopen
            cont_url = host_port+'/containers/json?all=true&filters={"id":["'+c_parameter+'"]}'
            #c = 'http://127.0.0.1:2375/containers/json?all=true&filters={"id":["75accfaebfae"]}'
            with urlopen(cont_url) as cont_resp_response_list:
                cont_resp_source_l = cont_resp_response_list.read()
                cont_data_l = json.loads(cont_resp_source_l)
                resp = cont_data_l
                object = {"len_resp":len(resp),"content_len":len(content),"c_activity":"list_processes","c_parameter":c_parameter,"resp":resp,"content_len":len(content),"content":content,"status_code":response.status_code}
        else: #Check if error occured
            object = {"content_len":len(content),"content":content,"c_activity":"list_processes","c_parameter":c_parameter,"status_code":response.status_code}
        return render(request,'container_ops.html',object)

#Get logs running in a Containers
    elif (search_value == 'list_logs'):
        url_start = host_port+'/containers/'+c_parameter+'/logs?stdout=true&stderr=true'
        import requests
        import json
        #data = {"name": "abc"}
        response = requests.get(url_start)
        content = response.content.decode('ISO-8859-1')
        #print(url_start)
        #resp = response.status_code
        #resp = response
        if (response.status_code == 200):
            from urllib.request import urlopen
            cont_url = host_port+'/containers/json?all=true&filters={"id":["'+c_parameter+'"]}'
            #c = 'http://127.0.0.1:2375/containers/json?all=true&filters={"id":["75accfaebfae"]}'
            with urlopen(cont_url) as cont_resp_response_list:
                cont_resp_source_l = cont_resp_response_list.read()
                cont_data_l = json.loads(cont_resp_source_l)
                resp = cont_data_l
                object = {"len_resp":len(resp),"c_activity":"list_logs","c_parameter":c_parameter,"resp":resp,"content_len":len(content),"content":content,"status_code":response.status_code}
        else: #Check if error occured
            object = {"content_len":len(content),"content":content,"c_activity":"list_logs","c_parameter":c_parameter,"status_code":response.status_code}
        return render(request,'container_ops.html',object)

#Get changes on a container’s filesystem
    elif (search_value == 'filesystem_changes'):
        url_start = host_port+'/containers/'+c_parameter+'/changes'
        import requests
        import json
        #data = {"name": "abc"}
        response = requests.get(url_start)
        content = response.content
        content2= str(content).replace("'","")
        content2= content2.replace("\\n","")
        content_null = "no"
        if content2 == "bnull":
            content_null = "yes"
        #print("Content2:",content2,"Content Null",content_null)
        #print(url_start)
        #resp = response.status_code
        #resp = response
        if (response.status_code == 200):
            from urllib.request import urlopen
            cont_url = host_port+'/containers/json?all=true&filters={"id":["'+c_parameter+'"]}'
            #c = 'http://127.0.0.1:2375/containers/json?all=true&filters={"id":["75accfaebfae"]}'
            with urlopen(cont_url) as cont_resp_response_list:
                cont_resp_source_l = cont_resp_response_list.read()
                cont_data_l = json.loads(cont_resp_source_l)
                resp = cont_data_l
                object = {"len_resp":len(resp),"content_null":content_null,"c_activity":"filesystem_changes","c_parameter":c_parameter,"resp":resp,"content_len":len(content),"content":content,"status_code":response.status_code}
        else: #Check if error occured
            object = {"content_null":content_null,"content_len":len(content),"content":content,"c_activity":"filesystem_changes","c_parameter":c_parameter,"status_code":response.status_code}
        return render(request,'container_ops.html',object)

#Get a container’s stats
    elif (search_value == 'container_stats'):
        url_start = host_port+'/containers/'+c_parameter+'/stats?stream=false'
        import requests
        import json
        response = requests.get(url_start)
        content = response.content
        content2= str(content).replace("'","")
        content2= content2.replace("\\n","")
        content_null = "no"
        if content2 == "bnull":
            content_null = "yes"
        #print("Content2:",content2,"Content Null",content_null)
        #print(url_start)
        #resp = response.status_code
        #resp = response
        if (response.status_code == 200):
            from urllib.request import urlopen
            cont_url = host_port+'/containers/json?all=true&filters={"id":["'+c_parameter+'"]}'
            #c = 'http://127.0.0.1:2375/containers/json?all=true&filters={"id":["75accfaebfae"]}'
            with urlopen(cont_url) as cont_resp_response_list:
                cont_resp_source_l = cont_resp_response_list.read()
                cont_data_l = json.loads(cont_resp_source_l)
                resp = cont_data_l
                object = {"len_resp":len(resp),"content_null":content_null,"c_activity":"container_stats","c_parameter":c_parameter,"resp":resp,"content_len":len(content),"content":content,"status_code":response.status_code}
        else: #Check if error occured
            object = {"content_null":content_null,"content_len":len(content),"content":content,"c_activity":"container_stats","c_parameter":c_parameter,"status_code":response.status_code}
        return render(request,'container_ops.html',object)

#Export the contents of a container as a tarball.
    elif (search_value == 'export_container'):
        url_start = host_port+'/containers/'+c_parameter+'/export'
        object = {"url":url_start,"c_activity":"export_container","c_parameter":c_parameter}
        return render(request,'container_ops.html',object)

#Unpause a container
    elif (search_value == 'unpause_container'):
        url_start = host_port+'/containers/'+c_parameter+'/unpause'
        import requests
        import json
        #data = {"name": "abc"}
        response = requests.post(url_start)
        content = response.content
        #resp = response.status_code
        #resp = response
        if (response.status_code == 204):
            from urllib.request import urlopen
            cont_url = host_port+'/containers/json?all=true&filters={"id":["'+c_parameter+'"]}'
            #c = 'http://127.0.0.1:2375/containers/json?all=true&filters={"id":["75accfaebfae"]}'
            with urlopen(cont_url) as cont_resp_response_list:
                cont_resp_source_l = cont_resp_response_list.read()
                cont_data_l = json.loads(cont_resp_source_l)
                resp = cont_data_l
                object = {"len_resp":len(resp),"c_activity":"unpause_container","c_parameter":c_parameter,"resp":resp,"content":content,"status_code":response.status_code}
        else: #Check if error occured
            object = {"content":content,"c_activity":"unpause_container","c_parameter":c_parameter,"status_code":response.status_code}
        return render(request,'container_ops.html',object)


    elif (search_value == 'pause_container'):
        url_start = host_port+'/containers/'+c_parameter+'/pause'
        import requests
        import json
        #data = {"name": "abc"}
        response = requests.post(url_start)
        content = response.content
        #resp = response.status_code
        #resp = response
        if (response.status_code == 204):
            from urllib.request import urlopen
            cont_url = host_port+'/containers/json?all=true&filters={"id":["'+c_parameter+'"]}'
            #c = 'http://127.0.0.1:2375/containers/json?all=true&filters={"id":["75accfaebfae"]}'
            with urlopen(cont_url) as cont_resp_response_list:
                cont_resp_source_l = cont_resp_response_list.read()
                cont_data_l = json.loads(cont_resp_source_l)
                resp = cont_data_l
                object = {"len_resp":len(resp),"c_activity":"pause_container","c_parameter":c_parameter,"resp":resp,"content":content,"status_code":response.status_code}
        else: #Check if error occured
            object = {"content":content,"c_activity":"pause_container","c_parameter":c_parameter,"status_code":response.status_code}
        return render(request,'container_ops.html',object)



    elif (search_value == 'update_name'):
        newcontname = request.POST.get("newcontname", None)
        url_start = host_port+'/containers/'+c_parameter+'/rename?name='+newcontname
        import requests
        import json
        #data = {"name": "abc"}
        response = requests.post(url_start)
        content = response.content
        #resp = response.status_code
        #resp = response
        if (response.status_code == 204):
            from urllib.request import urlopen
            cont_url = host_port+'/containers/json?all=true&filters={"id":["'+c_parameter+'"]}'
            #c = 'http://127.0.0.1:2375/containers/json?all=true&filters={"id":["75accfaebfae"]}'
            with urlopen(cont_url) as cont_resp_response_list:
                cont_resp_source_l = cont_resp_response_list.read()
                cont_data_l = json.loads(cont_resp_source_l)
                resp = cont_data_l
                object = {"len_resp":len(resp),"c_activity":"update_name","c_parameter":c_parameter,"resp":resp,"content":content,"status_code":response.status_code}
        else: #Check if error occured
            object = {"content":content,"c_activity":"update_name","c_parameter":c_parameter,"status_code":response.status_code}
        return render(request,'container_ops.html',object)


    elif (search_value == 'kill_container'):
        url_start = host_port+'/containers/'+c_parameter+'/kill'
        import requests
        import json
        #data = {"name": "abc"}
        response = requests.post(url_start)
        content = response.content
        #resp = response.status_code
        #resp = response
        if (response.status_code == 204):
            from urllib.request import urlopen
            cont_url = host_port+'/containers/json?all=true&filters={"id":["'+c_parameter+'"]}'
            #c = 'http://127.0.0.1:2375/containers/json?all=true&filters={"id":["75accfaebfae"]}'
            with urlopen(cont_url) as cont_resp_response_list:
                cont_resp_source_l = cont_resp_response_list.read()
                cont_data_l = json.loads(cont_resp_source_l)
                resp = cont_data_l
                object = {"len_resp":len(resp),"c_activity":"kill_container","c_parameter":c_parameter,"resp":resp,"content":content,"status_code":response.status_code}
        else: #Check if error occured
            object = {"content":content,"c_activity":"kill_container","c_parameter":c_parameter,"status_code":response.status_code}
        return render(request,'container_ops.html',object)


    elif (search_value == 'stop_container'):
        url_start = host_port+'/containers/'+c_parameter+'/stop'
        import requests
        import json
        #data = {"name": "abc"}
        response = requests.post(url_start)
        content = response.content
        #resp = response.status_code
        #resp = response
        if (response.status_code == 204):
            from urllib.request import urlopen
            cont_url = host_port+'/containers/json?all=true&filters={"id":["'+c_parameter+'"]}'
            #c = 'http://127.0.0.1:2375/containers/json?all=true&filters={"id":["75accfaebfae"]}'
            with urlopen(cont_url) as cont_resp_response_list:
                cont_resp_source_l = cont_resp_response_list.read()
                cont_data_l = json.loads(cont_resp_source_l)
                resp = cont_data_l
                object = {"len_resp":len(resp),"c_activity":"stop_container","c_parameter":c_parameter,"resp":resp,"content":content,"status_code":response.status_code}
        else: #Check if error occured
            object = {"content":content,"c_activity":"stop_container","c_parameter":c_parameter,"status_code":response.status_code}
        return render(request,'container_ops.html',object)

#Create container from image
    elif (search_value == 'create_container_from_image'):
        import pycurl, json
        from io import BytesIO

        c = pycurl.Curl()
        if (len(c_containername) >= 2):
            c.setopt(pycurl.URL, host_port+'/containers/create?name='+c_containername)
        else:
            c.setopt(pycurl.URL, host_port+'/containers/create')

        #c.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
        c.setopt(pycurl.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
        #data_list={"Image": "alpine","Tty":c_tty}
        if (c_tty=="true"):
            tty = True
        else:
            tty = False

        if (c_attachstdin=="true"):
            attachstdin = True
        else:
            attachstdin = False

        if (c_attachstdout=="true"):
            attachstdout = True
        else:
            attachstdout = False
        #print("AttachStdErr",c_attachstder)
        if (c_attachstder=="true"):
            attachstder = True
        else:
            attachstder = False

        if (c_openstdin=="true"):
            openstdin = True
        else:
            openstdin = False

        if (c_stdinonce=="true"):
            stdinonce = True
        else:
            stdinonce = False
        if (c_argsescaped=="true"):
            argsescaped = True
        else:
            argsescaped = False
        if (c_networkdisabled=="true"):
            networkdisabled = True
        else:
            networkdisabled = False

        cont_data = {"Image": c_parent_id, "Tty": tty,"AttachStdin":attachstdin,"AttachStdout":attachstdout,"AttachStderr":attachstder,"OpenStdin":openstdin,"StdinOnce":stdinonce,"ArgsEscaped":argsescaped,"NetworkDisabled":networkdisabled}
        if (len(c_hostname)>= 1):
            cont_data.update({"Hostname":c_hostname})
        if (len(c_domainname)>=1):
            cont_data.update({"Domainname":c_domainname})
        if (len(c_fusername)>=1):
            cont_data.update({"User":c_domainname})

        if (len(c_shell)>=1):
            cont_data.update({"Shell":c_shell.split(',')})
        if (len(c_stoptimeout)>=1):
            cont_data.update({"StopTimeout":int(c_stoptimeout)})
        if (len(c_stopsignal)>=1):
            cont_data.update({"StopSignal":c_stopsignal})

        if (len(c_labels)>=1):
            cont_data.update({"Labels":json.loads(c_labels)})

        if (len(c_onbuild)>=1):
            cont_data.update({"OnBuild":c_onbuild.split(',')})
        if (len(c_hostconfig)>=1):
            cont_data.update({"HostConfig":json.loads(c_hostconfig)})

        if (len(c_networkingconfig)>=1):
            cont_data.update({"NetworkingConfig":json.loads(c_networkingconfig)})

        if (len(c_macaddress)>=1):
            cont_data.update({"MacAddress":c_macaddress})
        if (len(c_entrypoint)>=1):
            cont_data.update({"Entrypoint":c_entrypoint.split(',')})
        if (len(c_workingdir)>=1):
            cont_data.update({"WorkingDir":c_workingdir})
        if (len(c_volumes)>=1):
            cont_data.update({"Volumes":json.loads(c_volumes)})
        if ((len(c_healthcheck)>=1) and (not isspace(c_healthcheck))):
            cont_data.update({"Healthcheck":json.loads(c_healthcheck)})
        if (len(c_cmd)>=1):
            cont_data.update({"Cmd":c_cmd.split(',')})
        if (len(c_env)>=1):
            cont_data.update({"Env":c_env.split(',')})
        if (len(c_exposedports)>=1):
            cont_data.update({"ExposedPorts":json.loads(c_exposedports)})


        data = json.dumps(cont_data)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, data)
        c.setopt(pycurl.VERBOSE, 1)
        buffer = BytesIO()
        #c.setopt(c.WRITEDATA, b)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        time_taken = c.getinfo(pycurl.TOTAL_TIME)
        http_resp_code = c.getinfo(pycurl.HTTP_CODE)
        body = buffer.getvalue()
        resp_raw = body.decode('iso-8859-1')
        c.close()
        if (http_resp_code == 201):
            resp_dict = json.loads(resp_raw)
            resp_id = resp_dict["Id"][0:12]
            from urllib.request import urlopen
            cont_url = host_port+'/containers/json?filters={"status":["created"],"id":["'+resp_id+'"]}'
            #resp = cont_url
            with urlopen(cont_url) as cont_resp_response:
                cont_resp_source = cont_resp_response.read()
                cont_data = json.loads(cont_resp_source)
                resp = cont_data
                object = {"http_resp_code":http_resp_code,"content":resp_raw,"c_activity":"create_container_from_image","c_parameter":c_parameter, "parentid":c_parent_id,"containername":c_containername,"resp":resp}
        else:
            object = {"http_resp_code":http_resp_code,"content":resp_raw,"c_activity":"create_container_from_image"}
            return render(request,'container_ops.html',object)

    else:
        object = {"http_resp_code":http_resp_code,"c_activity":"some_issue","content":resp_raw}
    return render(request,'container_ops.html',object)

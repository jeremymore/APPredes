import requests
import json
import xmltodict
USER="root"
PWD="Juniper"
DEVICES =  {"SC1":"172.16.1.1","SD1":"172.16.1.2","SA1":"172.16.1.6","SA2":"172.16.1.3","SA3":"172.16.1.4","SA4":"172.16.1.5"}
COMMIT = """<rpc>
    <commit/>
</rpc>"""
def get_segments():
        FILTER = """<rpc>
        <get-config>
                <source>
                        <running/>
                </source>
                <filter type="subtree">
                        <configuration>
                        </configuration>
                </filter>
        </get-config>
</rpc>"""
        reply = requests.post("http://172.16.1.1:3000/rpc",data=FILTER,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        json_data = xmltodict.parse("<configuration>"+"\n".join(reply.text.splitlines()[6:-3])+"</configuration>")
        irb_interfaces = {}
        # Itera sobre las interfaces
        for interface in json_data['configuration']['interfaces']['interface']:
            # Si el nombre de la interfaz es 'irb'
            if interface['name'] == 'irb':
                # Itera sobre las unidades de la interfaz IRB
                for unit in interface['unit']:
                    # Agrega el nombre de la interfaz IRB y su dirección de name al diccionario
                    irb_interfaces[unit['name']] = unit['family']['inet']['address']['name']
        return (json.dumps(irb_interfaces, indent=4))
def get_device():
        FILTER = """<rpc>
        <get-config>
                <source>
                        <running/>
                </source>
                <filter type="subtree">
                        <configuration>
                        </configuration>
                </filter>
        </get-config>
</rpc>"""
        interfaces_vlan_data = []
        for key, value in DEVICES.items():
                reply = requests.post("http://{}:3000/rpc".format(value),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                json_data = xmltodict.parse("<configuration>"+"\n".join(reply.text.splitlines()[6:-3])+"</configuration>")
                # Crear una lista para almacenar las VLANs en el formato deseado
                interfaces_data = []
                for interface in json_data['configuration']['interfaces']['interface']:
                        nombre = interface['name']
                        if 'irb' in nombre:
                                break
                        else:
                                unit = interface['unit']
                                unit_name = unit['name']
                                family = unit['family']
                                if 'ethernet-switching' in family:
                                        ethernet_switching = family['ethernet-switching']
                                        interface_mode = ethernet_switching['interface-mode']
                                        vlan = ethernet_switching.get('vlan', {})
                                        vlan_members = vlan.get('members', [])
                                        interface_info = {
                                                "name": nombre,
                                                "mode": interface_mode,
                                                "member": vlan_members
                                        }
                                        interfaces_data.append(interface_info)
                aux =[]                
                for item in interfaces_data:
                        if 'mode' in item and item['mode'] == 'access' and item['member']:
                                jijiaja = {
                                                f"{item['name']}": item['member']
                                        }
                                aux.append(jijiaja)
                jiji ={f"{key}":aux}
                interfaces_vlan_data.append(jiji)
                        # Utilizamos un diccionario de comprensión para obtener un diccionario plano de todas las interfaces y sus VLAN
        interfaces_por_dispositivo = {dispositivo: [item for sublist in interfaces for item in sublist.items()] for data in interfaces_vlan_data for dispositivo, interfaces in data.items()}

        # Utilizamos otro diccionario de comprensión para invertir las claves y valores
        dispositivos_por_vlan = {vlan: [dispositivo for dispositivo, interfaz_vlan in interfaces_por_dispositivo.items() if vlan in [v for k, v in interfaz_vlan]] for vlan in {v for sublist in interfaces_por_dispositivo.values() for k, v in sublist}}

        return dispositivos_por_vlan
def get_allvlans():
        FILTER = """<rpc>
        <get-config>
                <source>
                        <running/>
                </source>
                <filter type="subtree">
                        <configuration>
                                <vlans>
                                </vlans>
                        </configuration>
                </filter>
        </get-config>
</rpc>"""
        switch_vlans = []
        for key, value in DEVICES.items():
                reply = requests.post("http://{}:3000/rpc".format(value),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                json_data = xmltodict.parse("\n".join(reply.text.splitlines()[5:-3]))
                switch_vlans.append(json_data)
        vlan_info = {}
        # Iteramos sobre cada VLAN en switch_vlans
        for switch in switch_vlans:
            vlans = switch['vlans']['vlan']
            for vlan in vlans:
                vlan_id = vlan['vlan-id']
                vlan_name = vlan['name']     
                # Si la VLAN no está en el diccionario, la agregamos con una lista vacía de dispositivos
                if vlan_id not in vlan_info:
                    vlan_info[vlan_name] = {'id': vlan_id, 'devices': [], 'segmento_red': ''}
        # Iteramos sobre los dispositivos y actualizamos la información de la VLAN en vlan_info
        json_device = get_device()
        # Iteramos sobre los dispositivos y actualizamos la información de la VLAN en vlan_info
        # Actualizar el formato JSON existente con el nuevo formato
        for vlan, dispositivos in json_device.items():
                if vlan in vlan_info:
                        vlan_info[vlan]['devices'] += dispositivos
                else:
                        vlan_info[vlan] = {"devices": dispositivos}
        # Actualizamos el segmento de red en el nuevo formato con los datos de las interfaces IRB
        json_segments = get_segments()
        segments_dict = json.loads(json_segments)
        for key, value in vlan_info.items():
            vlan_id = value['id']
            if vlan_id in segments_dict:
                aux = segments_dict[vlan_id].split(".")
                aux[3] = "0/24"
                vlan_info[key]['segmento_red'] = ".".join(aux)
        return vlan_info
#DELETE
def delete_irb(id: int):
        FILTER = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <interfaces>
                                        <interface>
                                                <name>irb</name>
                                                <unit operation="delete">
                                                        <name>{}</name>
                                                        <family>
                                                        </family>
                                                </unit>
                                        </interface>
                                </interfaces>
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(id)
        for key, value in DEVICES.items():
                reply = requests.post("http://{}:3000/rpc".format(value),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(value),data=COMMIT,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                print("Create request: ", reply.content)
                print("Commit Response: ", commit.content)
def deleteallvlan(name: str,id:int):
        FILTER = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <vlans>
                                        <vlan operation="delete">
                                        <name>{}</name>
                                        </vlan>
                                </vlans>
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(name)
        for key, value in DEVICES.items():
                reply = requests.post("http://{}:3000/rpc".format(value),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(value),data=COMMIT,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                print("Create request: ", reply)
                print("Commit Response: ", commit)
        delete_irb(id)
        deleteintvlan(name)
        delete_dhcp_pool(name,id)
        delete_group(name,id)
        deleteintvlansc1(name)
def deleteintvlan(name: str):
        DEVICES =  {"SD1":"172.16.1.2","SA1":"172.16.1.3","SA2":"172.16.1.4","SA3":"172.16.1.5","SA4":"172.16.1.6"}
        for key, value in DEVICES.items():
                
                        FILTER = """<rpc>
                <edit-config>
                        <target>
                                <candidate/>
                        </target>
                        <config>
                                <configuration>
                                        <interfaces>
                                                <interface>
                                                <name>xe-1/0/0</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/1</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/2</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/3</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/4</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/5</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/6</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/7</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/8</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                        </interfaces>
                                </configuration>
                        </config>
                </edit-config>
                </rpc>""".format(name,name,name,name,name,name,name,name,name)
                        reply = requests.post("http://{}:3000/rpc".format(value),data=FILTER,
                        auth=requests.auth.HTTPBasicAuth(USER, PWD),
                        headers={"Accept": "application/json","Content-Type": "application/xml"})
                        commit = requests.post("http://{}:3000/rpc".format(value),data=COMMIT,
                        auth=requests.auth.HTTPBasicAuth(USER, PWD),
                        headers={"Accept": "application/json","Content-Type": "application/xml"})
                        print(reply.content) 
def deleteintvlansc1(name: str):
        FILTER = """<rpc>
                <edit-config>
                        <target>
                                <candidate/>
                        </target>
                        <config>
                                <configuration>
                                        <interfaces>
                                                <interface>
                                                <name>xe-1/0/0</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/1</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/3</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/4</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/5</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/6</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/7</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                                <interface>
                                                <name>xe-1/0/8</name>
                                                <unit>
                                                        <name>0</name>
                                                        <family>
                                                        <ethernet-switching>
                                                                <vlan>
                                                                <members operation="delete">{}</members>
                                                                </vlan>
                                                        </ethernet-switching>
                                                        </family>
                                                </unit>
                                                </interface>
                                        </interfaces>
                                </configuration>
                        </config>
                </edit-config>
                </rpc>""".format(name,name,name,name,name,name,name,name,name)
        reply = requests.post("http://172.16.1.1:3000/rpc",data=FILTER,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        commit = requests.post("http://172.16.1.1:3000/rpc",data=COMMIT,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        print(reply.content) 
def delete_dhcp_pool(name:str, id: int):
        FILTER = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <access>
                                        <address-assignment>
                                                <pool operation="delete">
                                                        <name>{}</name>
                                                </pool>
                                        </address-assignment>   
                                </access>            
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(name)
        GROUP = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <system>
                                        <services>
                                                <dhcp-local-server>
                                                        <group operation="delete">
                                                                <name>{}</name>
                                                         </group>
                                                </dhcp-local-server>
                                        </services>
                                </system>        
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(name,id)
        reply = requests.post("http://172.16.1.1:3000/rpc",data=FILTER,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        reply2 = requests.post("http://172.16.1.1:3000/rpc",data=GROUP,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        commit = requests.post("http://172.16.1.1:3000/rpc",data=COMMIT,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        print("Delete request: ", reply.content)
        print("Delete request: ", reply2.content)
        print("Commit Response: ", commit.content)
def delete_group(name:str, id: int):
        FILTER = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <forwarding-options>
                                        <dhcp-relay>
                                                <server-group>
                                                        <server-group operation="delete">
                                                        <name>{}</name>
                                                        </server-group>
                                                </server-group>
                                        </dhcp-relay>
                                </forwarding-options>
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(name,id)
        GROUP = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <forwarding-options>
                                        <dhcp-relay>
                                                <forward-only>
                                                </forward-only>
                                                        <group>
                                                                <name>DHCP</name>
                                                                <active-server-group>
                                                                <active-server-group>DHCP_SERVER</active-server-group>
                                                                </active-server-group>
                                                                <interface operation="delete">
                                                                <name >irb.{}</name>
                                                                </interface>
                                                        </group>

                                        </dhcp-relay>
                                </forwarding-options>
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(id)
        DEVICES =  {"SD1":"172.16.1.2","SA1":"172.16.1.3","SA2":"172.16.1.4","SA3":"172.16.1.5","SA4":"172.16.1.6"}
        for key, value in DEVICES.items():
                reply = requests.post("http://172.16.1.2:3000/rpc",data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                reply = requests.post("http://{}:3000/rpc".format(value),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                reply2 = requests.post("http://172.16.1.2:3000/rpc",data=GROUP,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                reply3 = requests.post("http://{}:3000/rpc".format(value),data=GROUP,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit2 = requests.post("http://{}:3000/rpc".format(value),data=COMMIT,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                print("Create request: ", reply.content)
                print("Create request: ", reply2.content)
                print("Create request: ", reply3.content)
#CREATE
def create_irb(id: int):
        for key, value in DEVICES.items():
                aux= value.split(".")
                aux[2] = str(id)
                nuevo = ".".join(aux)
                FILTER = """<rpc>
                <edit-config>
                        <target>
                                <candidate/>
                        </target>
                        <config>
                                <configuration>
                                        <interfaces>
                                                <interface>
                                                        <name>irb</name>
                                                        <unit>
                                                                <name>{}</name>
                                                                <family>
                                                                <inet>
                                                                        <address operation="create">
                                                                        <name>{}/24</name>
                                                                        </address>
                                                                </inet>
                                                                </family>
                                                        </unit>
                                                </interface>
                                        </interfaces>
                                </configuration>
                        </config>
                </edit-config>
        </rpc>""".format(id,nuevo)
                reply = requests.post("http://{}:3000/rpc".format(value),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(value),data=COMMIT,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                print("Create request: ", reply.content)
                print("Commit Response: ", commit.content)
def create_l3_int(name:str, id: int):
        for key, value in DEVICES.items():
                FILTER = """<rpc>
                <edit-config>
                        <target>
                                <candidate/>
                        </target>
                        <config>
                                <configuration>
                                        <vlans>
                                                <vlan>
                                                <name>{}</name>
                                                <vlan-id>{}</vlan-id>
                                                <l3-interface operation="create">irb.{}</l3-interface>
                                                </vlan>
                                        </vlans>           
                                </configuration>
                        </config>
                </edit-config>
        </rpc>""".format(name,id,id)
                reply = requests.post("http://{}:3000/rpc".format(value),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(value),data=COMMIT,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                print("Create request: ", reply.content)
                print("Commit Response: ", commit.content)
def create_vlan(name: str,id: int ,device:str, interfaces: list):
        FILTER = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <vlans>
                                        <vlan operation="create">
                                        <name>{}</name>
                                        <vlan-id>{}</vlan-id>
                                        </vlan>
                                </vlans>
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(name, id)
        for key, value in DEVICES.items():
                reply = requests.post("http://{}:3000/rpc".format(value),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(value),data=COMMIT,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                
                print("Create request: ", reply)
                print("Commit Response: ", commit)
        create_irb(id)
        create_l3_int(name,id)
        create_int_trunk_vlan(name)
        create_dhcp_pool(name,id)
        create_int_trunk_SD(name)
        create_int_acc_vlan(name,device,interfaces)
        create_group(name,id,device)    
def create_int_trunk_vlan(name: str):
        interface = "xe-1/0/0"
        devices = ["172.16.1.1","172.16.1.2","172.16.1.3","172.16.1.4","172.16.1.5","172.16.1.6"]
        for key, value in DEVICES.items():
                FILTER = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <interfaces>
                                        <interface>
                                        <name>{}</name>
                                        <unit>
                                                <name>0</name>
                                                <family>
                                                <ethernet-switching>
                                                        <vlan>
                                                        <members operation="create">{}</members>
                                                        </vlan>
                                                </ethernet-switching>
                                                </family>
                                        </unit>
                                        </interface>
                                </interfaces>
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(interface,name)
                reply = requests.post("http://{}:3000/rpc".format(value),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(value),data=COMMIT,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                print(reply.content) 
                print(commit.content) 
def create_int_trunk_SD(name: str):
        interfaces = ["xe-1/0/1","xe-1/0/2","xe-1/0/3","xe-1/0/4"]
        for interface in interfaces:
                FILTER = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <interfaces>
                                        <interface>
                                        <name>{}</name>
                                        <unit>
                                                <name>0</name>
                                                <family>
                                                <ethernet-switching>
                                                        <vlan>
                                                        <members operation="create">{}</members>
                                                        </vlan>
                                                </ethernet-switching>
                                                </family>
                                        </unit>
                                        </interface>
                                </interfaces>
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(interface,name)
                reply = requests.post("http://172.16.1.2:3000/rpc",data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://172.16.1.2:3000/rpc",data=COMMIT,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                print(reply.content) 
                print(commit.content) 
def create_int_acc_vlan(name: str, device: str, interfaces: list):
        for interface in interfaces:
                FILTER = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <interfaces>
                                        <interface>
                                        <name>{}</name>
                                        <unit>
                                                <name>0</name>
                                                <family>
                                                <ethernet-switching>
                                                        <vlan>
                                                        <members operation="create">{}</members>
                                                        </vlan>
                                                </ethernet-switching>
                                                </family>
                                        </unit>
                                        </interface>
                                </interfaces>
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(interface,name)
                print(FILTER)
                reply = requests.post("http://{}:3000/rpc".format(device),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(device),data=COMMIT,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                print(interfaces)
                print("ACCESSO")
                print(reply.content) 
                print(commit.content) 
#DHCP
def create_dhcp_pool(name:str, id: int):
        FILTER = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <access>
                                        <address-assignment>
                                                <pool>
                                                        <name>{}</name>
                                                        <family>
                                                        <inet>
                                                                <network>172.16.{}.0/24</network>
                                                                <range>
                                                                <name>{}</name>
                                                                <low>172.16.{}.11</low>
                                                                <high>172.16.{}.250</high>
                                                                </range>
                                                                <dhcp-attributes>
                                                                <router>
                                                                        <name>172.16.{}.1</name>
                                                                </router>
                                                                </dhcp-attributes>
                                                        </inet>
                                                        </family>
                                                </pool>
                                        </address-assignment>   
                                </access>            
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(name,id,name,id,id,id)
        GROUP = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <system>
                                        <services>
                                                <dhcp-local-server>
                                                        <group>
                                                                <name>{}</name>
                                                                <interface>
                                                                        <name>irb.{}</name>
                                                                </interface>

                                                         </group>
                                                </dhcp-local-server>
                                        </services>
                                </system>        
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(name,id)
        reply = requests.post("http://172.16.1.1:3000/rpc",data=FILTER,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        reply = requests.post("http://172.16.1.1:3000/rpc",data=GROUP,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        commit = requests.post("http://172.16.1.1:3000/rpc",data=COMMIT,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        print("Create request: ", reply.content)
        print("Commit Response: ", commit.content)
def create_group(name:str, id: int,device: str):
        FILTER = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <forwarding-options>
                                        <dhcp-relay>
                                                <forward-only>
                                                </forward-only>
                                                <server-group>
                                                        <server-group>
                                                        <name operation="Create">{}</name>
                                                        <address>
                                                                <name>172.16.{}.1</name>
                                                        </address>
                                                        </server-group>
                                                </server-group>
                                        </dhcp-relay>
                                </forwarding-options>
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(name,id)
        GROUP = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <forwarding-options>
                                        <dhcp-relay>
                                                <forward-only>
                                                </forward-only>
                                                        <group>
                                                                <name>DHCP</name>
                                                                <active-server-group>
                                                                <active-server-group>DHCP_SERVER</active-server-group>
                                                                </active-server-group>
                                                                <interface>
                                                                <name operation="create">irb.{}</name>
                                                                </interface>
                                                        </group>

                                        </dhcp-relay>
                                </forwarding-options>
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(id)
        reply = requests.post("http://172.16.1.2:3000/rpc",data=FILTER,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        reply = requests.post("http://{}:3000/rpc".format(device),data=FILTER,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        reply2 = requests.post("http://172.16.1.2:3000/rpc",data=GROUP,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        reply3 = requests.post("http://{}:3000/rpc".format(device),data=GROUP,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        commit2 = requests.post("http://{}:3000/rpc".format(device),data=COMMIT,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        print("Create request: ", reply.content)
        print("Create request: ", reply2.content)
        print("Create request: ", reply3.content)


#Creacion administracion de vlan
def get_devices(name):
        FILTER = """<rpc>
        <get-config>
                <source>
                        <running/>
                </source>
                <filter type="subtree">
                        <configuration>
                        </configuration>
                </filter>
        </get-config>
</rpc>"""
        device=DEVICES[name]
        interfaces_vlan_data = []
        reply = requests.post("http://{}:3000/rpc".format(device),data=FILTER,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        json_data = xmltodict.parse("<configuration>"+"\n".join(reply.text.splitlines()[6:-3])+"</configuration>")
        # Crear una lista para almacenar las VLANs en el formato deseado
        interfaces_data = []
        for interface in json_data['configuration']['interfaces']['interface']:
                nombre = interface['name']
                if 'irb' in nombre:
                        break
                else:
                        unit = interface['unit']
                        unit_name = unit['name']
                        family = unit['family']
                        if 'ethernet-switching' in family:
                                ethernet_switching = family['ethernet-switching']
                                interface_mode = ethernet_switching['interface-mode']
                                vlan = ethernet_switching.get('vlan', {})
                                vlan_members = vlan.get('members', [])
                                interface_info = {
                                        "name": nombre,
                                        "mode": interface_mode,
                                        "member": vlan_members
                                }
                                interfaces_data.append(interface_info)
        

        return interfaces_data


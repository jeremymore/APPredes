
import requests
import json
import xmltodict
USER="root"
PWD="Juniper"
DEVICES =  ["172.16.1.1","172.16.1.2","172.16.1.3","172.16.1.4","172.16.1.5","172.16.1.6"]
#interfaces = ["xe-1/0/0","xe-1/0/1","xe-1/0/2","xe-1/0/3","xe-1/0/4","xe-1/0/5","xe-1/0/6","xe-1/0/7","xe-1/0/8"]
COMMIT = """<rpc>
    <commit/>
</rpc>"""
def create_all_irb(id: int):
        for device in DEVICES:
                aux= device.split(".")
                aux[2] = "30"
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
                                                        <name>{id}</name>
                                                        <family>
                                                        <inet>
                                                                <address operation="create">
                                                                <name>{}</name>
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
                reply = requests.post("http://{}:3000/rpc".format(device),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(device),data=COMMIT,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                print("Create request: ", reply)
                print("Commit Response: ", commit)
def create_all_vlan(name: str,id: int):
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
        for device in DEVICES:
                reply = requests.post("http://{}:3000/rpc".format(device),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(device),data=COMMIT,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                print("Create request: ", reply)
                print("Commit Response: ", commit)
        create_all_irb(id)    


def get(name: str):#pendiente
        FILTER = """<rpc>
        <get-config>
                <source>
                        <running/>
                </source>
                <filter type="subtree">
                        <configuration>
                                <vlans>
                                        <vlan>
                                        <name>{}</name>
                                        </vlan>
                                </vlans>
                        </configuration>
                </filter>
        </get-config>
</rpc>""".format(name)
        reply = requests.post("http://172.16.1.6:3000/rpc",data=FILTER,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        json_data = xmltodict.parse("\n".join(reply.text.splitlines()[5:-3]))
        print(json.dumps(json_data, indent=4))
def get_device(name: str):#pendiente
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
        reply = requests.post("http://{}:3000/rpc".format(name),data=FILTER,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        json_data = xmltodict.parse("\n".join(reply.text.splitlines()[5:-3]))
        print(json.dumps(json_data, indent=4))
def get_vlans():#pendiente
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
        reply = requests.post("http://172.16.1.2:3000/rpc",data=FILTER,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        json_data = xmltodict.parse("\n".join(reply.text.splitlines()[5:-3]))
        print(json.dumps(json_data, indent=True))
def get_allvlans():#pendiente
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
        for device in DEVICES:
                reply = requests.post("http://{}:3000/rpc".format(device),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                json_data = xmltodict.parse("\n".join(reply.text.splitlines()[5:-3]))
                switch_vlans.append(json_data)
                print(switch_vlans)
def update():
        FILTER = """<rpc>
        <edit-config>
                <target>
                        <candidate/>
                </target>
                <config>
                        <configuration>
                                <vlans>
                                        <vlan>
                                        <name>AD</name>
                                        <vlan-id>400</vlan-id>
                                        </vlan>
                                </vlans>
                        </configuration>
                </config>
        </edit-config>
</rpc>"""
        reply = requests.post("http://172.16.1.6:3000/rpc",data=FILTER,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})
        print(reply) 

##CREATE
def create_irb(id: int):
        for device in DEVICES:
                aux= device.split(".")
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
                reply = requests.post("http://{}:3000/rpc".format(device),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(device),data=COMMIT,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                print("Create request: ", reply.content)
                print("Commit Response: ", commit.content)
def create_l3_int(name:str, id: int):
        for device in DEVICES:
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
                reply = requests.post("http://{}:3000/rpc".format(device),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(device),data=COMMIT,
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
        for device in DEVICES:
                reply = requests.post("http://{}:3000/rpc".format(device),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(device),data=COMMIT,
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
        for device in devices:
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
                reply = requests.post("http://{}:3000/rpc".format(device),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(device),data=COMMIT,
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
                reply = requests.post("http://{}:3000/rpc".format(device),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(device),data=COMMIT,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
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
        #print("Commit Response: ", commit2.content)
def create_group2(name:str, id: int):
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
        reply = requests.post("http://172.16.1.1:3000/rpc",data=GROUP,
        auth=requests.auth.HTTPBasicAuth(USER, PWD),
        headers={"Accept": "application/json","Content-Type": "application/xml"})

#deleteintvlan("VLAN30")
create_vlan("VLAN70",70,"172.16.1.5",["xe-1/0/5","xe-1/0/6"])
#create_int_acc_vlan("VLAN70","172.16.1.5",["xe-1/0/5","xe-1/0/6"])




##DELETE
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
        for device in DEVICES:
                reply = requests.post("http://{}:3000/rpc".format(device),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(device),data=COMMIT,
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
        for device in DEVICES:
                reply = requests.post("http://{}:3000/rpc".format(device),data=FILTER,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                commit = requests.post("http://{}:3000/rpc".format(device),data=COMMIT,
                auth=requests.auth.HTTPBasicAuth(USER, PWD),
                headers={"Accept": "application/json","Content-Type": "application/xml"})
                print("Create request: ", reply)
                print("Commit Response: ", commit)
        delete_irb(id)
        deleteintvlan(name)
        delete_dhcp_pool(name,id)
        delete_group(name,id)
def deleteintvlan(name: str):
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
                        print(key)
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
                                                        <server-group>
                                                        <name operation="delete">{}</name>
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
                                                                <name operation="delete">irb.{}</name>
                                                                </interface>
                                                        </group>

                                        </dhcp-relay>
                                </forwarding-options>
                        </configuration>
                </config>
        </edit-config>
</rpc>""".format(id)
        for device in DEVICES:
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

from flask import Flask,render_template,request,redirect
from wtforms import Form,StringField,IntegerField,SelectMultipleField,SelectField,widgets,validators
from wtforms.widgets import NumberInput,CheckboxInput,ListWidget
import requests
import json
import xmltodict
import time
from controllers.switchs import *
app =Flask(__name__)
app.config['SECRET_KEY'] = "admin123"
choicesdevice=["SA1","SA2","SA3","SA4"]
"""
activar el entorno
#flask --app index run --debug --port 8080
@app.route('/')#ruta raiz
def principal():
    return 'Bienvenido a mi sitio web de administracion'
"""
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.TableWidget(with_table_tag=True)
    option_widget = widgets.CheckboxInput()

@app.route('/')#ruta raiz
def principal():
    return render_template('index.html')#Hace la llamada al documento HTML buscando en carpetas template

# create form class
class VLANForm(Form):
    vlan_name = StringField("Nombre VLAN: ",validators=[validators.InputRequired()])
    vlan_id = IntegerField("ID VLAN: ",validators=[validators.InputRequired()],widget=NumberInput(min=10,max=100))
    switch_acc=SelectField("Switch de Acceso: ",validators=[validators.InputRequired()],choices=choicesdevice)
    switch_int = MultiCheckboxField('Interfaz de Acceso:',choices=[(1,"xe-1/0/1"), (2,"xe-1/0/2"), (3,"xe-1/0/3"),(4,"xe-1/0/4"),(5,"xe-1/0/5" ),(6,"xe-1/0/6"),(7,"xe-1/0/7"),(8,"xe-1/0/8")])


@app.route('/vlans',methods=["GET", "POST"])#ruta raiz
def mostrarvlans():
    vlans_dict={}
    vlans_dict = get_allvlans()
    return render_template('vlans.html',vlans_dict=vlans_dict)

@app.route('/delete/<string:name>/<int:id>',methods=["GET", "POST"])
def deletevlans(name,id):
    tiempoini=time.time()
    deleteallvlan(name,id)
    tiempofin=time.time()
    aux=tiempofin-tiempoini
    print(f"{aux} segundos")
    return redirect("/vlans")
@app.route('/create',methods=["GET", "POST"])#ruta raiz
def create():
    tiempoini=time.time()
    form = VLANForm(request.form)
    if request.method == "POST":
        name =form.vlan_name.data
        id =int(form.vlan_id.data)
        device=DEVICES.get(form.switch_acc.data, "")
        print(device)
        interface:list=form.switch_int.data
        create_vlan(name,id,device,interface)
        print("\n\n\n\nTiempo de ejecucion")
        tiempofin=time.time()
        aux=tiempofin-tiempoini
        print(f"{aux} segundos")
        return redirect("/vlans")
    else:
        return render_template('create.html',form=form)
@app.route('/device/<string:name>')#ruta raiz
def device(name):
    ports_info = get_devices(name)
    return render_template('device.html',ports_info=ports_info,name=name)

if __name__ == '_main_':
    app.run(debug=True, port=8080) # Para poder hacer que el servidor se reinicie con los cambios del servidor







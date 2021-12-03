#PROYECTO: Caballos Distribuidos (Web APi)

#Obtener la IP del servidor (El equipo)
#Importante si se quiere conectarse desde otro dispositivo.
import socket
nombre_equipo = socket.gethostname()
direccion_equipo = socket.gethostbyname(nombre_equipo)
URL = "http://"+direccion_equipo+":8080"

#DECLARACION DE LIBRERIAS 
from bottle import route, run, template, request
from datetime import datetime
import copy

#DECLARACION DE VARIABLES
now = datetime.now()
Pos_ini =[{"Fila": '', "Columna":''}]
ind = 0
Tableros_generados = []
respuestas = []
soluciones = []


#En en navegador:
#http://direccion_equipo:8080/cliente

#***********************************************************************
#*************************** Camino del Caballo ************************
#***********************************************************************
posPosibles = [[] for x in range(64)]
marcados = ["No" for x in range(64)]

def crearTableroMov():
	return [
		[2,3,4,4,4,4,3,2],
		[3,4,6,6,6,6,4,3],
		[4,6,8,8,8,8,6,4],
		[4,6,8,8,8,8,6,4],
		[4,6,8,8,8,8,6,4],
		[4,6,8,8,8,8,6,4],
		[3,4,6,6,6,6,4,3],
		[2,3,4,4,4,4,3,2]
	]

def crearTablero():
	return [
		[0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0],
		[0,0,0,0,0,0,0,0]
	]

#crearTableroMov se estiman los movimientos posibles para cada casilla
tableroMov = crearTableroMov()

def iniciar(Pos,Tablero):
	global posPosibles
	global marcados
	for i in range(len(posPosibles)):
		posPosibles[i] = []
	for i in range(len(marcados)):
		marcados[i] = "No"
	M = [[2,[Pos[0],Pos[1]],copy.deepcopy(Tablero)]]
	tamaño = len(M[0][2])*len(M[0][2][0]) - 3
	i = 0
	while i <= tamaño:
		iteracion = proceso(copy.deepcopy(M[i][2]),M[i][1][0],M[i][1][1],M[i][0])
		if iteracion:
			if (len(M)) >= (i+2):
				M[i+1] =[M[i][0]+1] + iteracion
			else:
				M.append([M[i][0]+1] + iteracion)
		else:
			i -= 2
		i += 1
	if len(M) == 63:
		print("Solución terminada.")
		return M
	else:
		print("Reintentando...")
		M2 = iniciar(Pos,Tablero)
		return M2

def proceso(t,posV,posH,i):
	pV = posV
	pH = posH
	espacios = contarEspacios(t)
	tamaño = len(t)*len(t[0])
	if espacios == 0:
		return False
	else:
		if espacios == tamaño:
			t[pV][pH] = tamaño - (espacios - 1)
		else:
			pV,pH = movSiguiente(t,posV,posH,i)
			if pV == posV and pH == posH:
				t[pV][pH] = 0
				marcados[i] = "No"
				return False
			else:
				t[pV][pH] = tamaño - (espacios - 1)
		return [[pV,pH],t]

def movSiguiente(T,pV,pH,i):
	posM = posiblesMovimientos(T,pV,pH)
	if posM:
		if not posPosibles[i] and marcados[i] == "No":
			posPosibles[i] = posM
			marcados[i] = "Si"
	if posPosibles[i]:
		pos = determinarMenorCantidad(T,i)
		pV = pos[0]
		pH = pos[1]
		posPosibles[i].remove(pos)
	return pV,pH

def posiblesMovimientos(T,pV,pH):
	valores = [2,1]
	formas = [[-1,1],[1,1],[1,-1],[-1,-1]]
	posiblesMov = []
	for i in valores:
		desH = i
		if desH == 1:
			desV = 2
		else:
			desV = 1
		for j in formas:
			aux_pV = pV + (j[0] * desV)
			aux_pH = pH + (j[1] * desH)
			if aux_pV >= 0 and aux_pV < len(T):
					if aux_pH >= 0 and aux_pH < len(T[0]):
						if T[aux_pV][aux_pH] == 0:
							posiblesMov.append([aux_pV,aux_pH])
	return posiblesMov

def contarEspacios(T):
	cont = 0
	for i in T:
		for j in i:
			if j == 0:
				cont += 1
	return cont

def determinarMenorCantidad(T,i):
	menor = 0
	pos = None
	for i in posPosibles[i]:
		if menor == 0:
			menor = tableroMov[i[0]][i[1]]
			pos = i
		else:
			if tableroMov[i[0]][i[1]] < menor:
				menor = tableroMov[i[0]][i[1]]
				pos = i
	return pos

#***********************************************************************
#***************************FIN DEL PROGRAMA****************************
#***********************************************************************

#***********************************************************************
#********************************WEB API********************************
#***********************************************************************

Encabezado = '''
	<!doctype html>
	<html>
		<head>
			<meta charset="UTF-8">
			<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
			<!-- Bootstrap CSS -->
			<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
			<!-- Script Tag AngularJS -->
			<script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.2.23/angular.min.js"></script>
			<style>
				.btn{
					width: 100px;
					margin-top: 3px;
				}
				button.btn-sm{
					margin-bottom: 3px;
				}
			</style>'''

@route('/cliente') 
def cliente():
	global now
	global Pos_ini
	global soluciones
	global respuestas
	global ind
	x = str(Pos_ini[0]['Fila'])
	y = str(Pos_ini[0]['Columna'])
	
	disabledBS = "disabled"
	if soluciones:
		disabledBS = ""
	
	for i in range(len(respuestas)):
		if respuestas[i] == []:
			ind = i
			break
		else:
			ind = ''
	
	alert = ''
	if ind == '':
		alert = '<div id="alert" style="display:none;">¡¡Ya no hay tableros para seleccionar!!</div>'
	
	return Encabezado + '''
		<title>Cliente</title>
		</head>
		<body onload="load()">
			<div>
			<p id="now" style="display:none;">'''+str(now)+'''</p>
				<h4>Caballos Distribuidos - Cliente</h4>
				<!-- BInicial -->
				<div ng-app="">
					<button id="BInicial" class="btn btn-primary" ng-click="ocultar=!ocultar" ng-init="ocultar=true">BInicial</button>
					<form id="formPI" action="/posicion_inicial" method="post" ng-hide="ocultar">
						<input type="number" id="x" name="x" min="0" max="7" placeholder="Fila:X" required style="width: 100px;" value="''' + x + '''">
						<input type="number" id="y" name="y" min="0" max="7" placeholder="Colum:Y" required style="width: 100px;" value="''' + y + '''">
						<input type="submit" class="btn btn-success btn-sm" onclick="EnviarPos_ini()" value="Enviar"/>
					</form>
				</div>
				<!-- BCamino -->
				<a href="''' + URL + '''/camino" onclick="event.preventDefault()"><button id="BCamino" class="btn btn-primary" onclick="EnviarCamino()" disabled>BCamino</button><a/>
				<br>
				<!-- BProcesar -->
				<a href="''' + URL + '''/respuesta" onclick="event.preventDefault()"><button id="BProcesar" class="btn btn-primary" onclick="EnviarProcesar()" disabled>BProcesar</button><a/>
				<br>
				<!-- BSoluciones -->
				<a href="''' + URL + '''/soluciones"><button id="BSoluciones" class="btn btn-primary" '''+ disabledBS + '''>BSoluciones</button><a/>
				<br>
				<br>
				<br>
				''' + alert + '''
				<div id="nc" style="display:none;">Datos del cliente ...</div>
				<div id="nt" style="display:none;"></div>
				<br>
				<div id="rt" style="display:none;"></div>
			</div>
			<script>
				const formPI = document.getElementById('formPI');
				formPI.addEventListener('submit', function(event){
						event.preventDefault();
					}
				)
				function EnviarPos_ini(){
					const data = new FormData(document.getElementById('formPI'));
					fetch('../posicion_inicial', {
						method: 'POST',
						body: data
					})
					.then(function(response) {
						if(response.ok) {
							document.getElementById('BCamino').disabled = false;
							return response.text()
						}else {
							throw "Error en la llamada Ajax";
						}
					})
					.then(function(texto) {
						console.log(texto);
					})
					.catch(function(err) {
						console.log(err);
					});
					var storedPos_x = localStorage.getItem('Pos_x');
					var storedPos_y = localStorage.getItem('Pos_y');
					if((!storedPos_x) || (storedPos_x == 'null') || (storedPos_x == 'undefined') || (!storedPos_y) || (storedPos_y == 'null') || (storedPos_y == 'undefined')){
						alert('¡¡Posicion inicial establecido!!');
						localStorage.setItem('Pos_x',document.getElementById('x').value);
						localStorage.setItem('Pos_y',document.getElementById('y').value);
						document.getElementById('x').value = localStorage.getItem('Pos_x');
						document.getElementById('y').value = localStorage.getItem('Pos_y');
					}else{
						alert('¡¡Ya se establecio la Posicion inicial!!');
					}
					document.getElementById('x').value = localStorage.getItem('Pos_x');
					document.getElementById('y').value = localStorage.getItem('Pos_y');
					if(document.getElementById('x').value != '' && document.getElementById('y').value != ''){
						document.getElementById('BInicial').click();
					}
				}
				function EnviarCamino(){
					var storedIndice = localStorage.getItem('Indice');
					if((!storedIndice) || (storedIndice == 'null') || (storedIndice == 'undefined')) {
							alert('¡¡Tablero seleccionado!!');
							localStorage.setItem('Indice', ''' + str(ind) + ''');
						}else{
							alert('¡¡Ya tienes un tablero seleccionado!!');
							localStorage['Indice'] = storedIndice;
						}
					document.getElementById('BProcesar').disabled = false;
				}
				function EnviarProcesar(){
					var storedRTablero = localStorage.getItem('RTablero');
					if(storedRTablero){
						alert('¡¡Ya realizaste y obtuviste la solucion!!');
						window.location.href = "''' + URL + '''/respuesta";
					}else{
						alert("¡¡Iniciando BProcesar!!");
						const data = new FormData();
						data.append('Indice', localStorage.getItem('Indice'));
						fetch('../respuesta', {
							method: 'POST',
							body: data
						})
						.then(function(response) {
							if(response.ok) {
								alert("¡¡Solucion terminada!!");
								window.location.href = "''' + URL + '''/respuesta";
							}else {
								alert("¡¡No hay Solucion!!");
								throw "Error en la llamada Ajax";
							}
						})
						.then(function(texto) {
							console.log(texto);
						})
						.catch(function(err) {
							console.log(err);
						});
					}
				}
				function load(){
					var storedNow = localStorage.getItem('now');
					if((storedNow != document.getElementById('now').innerHTML) || (!storedNow) || (storedNow == 'null') && (storedNow == 'undefined')){
						localStorage.clear();
						localStorage.setItem('now', document.getElementById('now').innerHTML);
					}
					if(document.getElementById('x').value != '' && document.getElementById('y').value != ''){
						document.getElementById('BCamino').disabled = false;
						localStorage.setItem('Pos_x',document.getElementById('x').value);
						localStorage.setItem('Pos_y',document.getElementById('y').value);
					}
					var storedIndice = localStorage.getItem('Indice');
					if((storedIndice) && (storedIndice != 'null') && (storedIndice != 'undefined')) {
						document.getElementById('BProcesar').disabled = false;
						document.getElementById('nc').style.display = "none";
						document.getElementById('nc').style.display = "block";
						document.getElementById('nc').innerHTML = "Datos del cliente #" + (JSON.parse(storedIndice) + 1) +"...";
						document.getElementById('nt').style.display = "block";
						document.getElementById('nt').innerHTML = "Tablero #" + (JSON.parse(storedIndice) + 1) + " seleccionado.";
					}else{
						document.getElementById('nc').style.display = "block";
					}
					var storedRT = localStorage.getItem('RTablero');
					if((storedRT) && (storedRT != 'null') && (storedRT != 'undefined')) {
						document.getElementById('rt').style.display = "block";
						document.getElementById('rt').innerHTML = "Solucion:<br>" + storedRT;
					}
				}
			</script>
		</body>
	</html>'''

@route('/posicion_inicial',method='POST') 
def posicion_inicialP():
	global Pos_ini
	global Tableros_generados
	global respuestas
	if not Pos_ini[0]['Fila'] or not Pos_ini[0]['Columna']:
		x = request.forms.get('x')
		y = request.forms.get('y')
		Pos_ini = [{"Fila": x, "Columna":y}]
		T = crearTablero()
		x = int(Pos_ini[0]['Fila'])
		y = int(Pos_ini[0]['Columna'])
		T[x][y] = 1
		Tableros_generados = []
		Primeros_movimientos = posiblesMovimientos(T,x,y)
		for i in range(len(Primeros_movimientos)):
			Seg_posicion = Primeros_movimientos[i]
			T2 = copy.deepcopy(T)
			T2[Seg_posicion[0]][Seg_posicion[1]] = 2
			Tableros_generados.append([Seg_posicion,T2])
			respuestas.append([])

@route('/respuesta',method='post') 
def respuestaP():
	global ind
	if ind != '':
		global respuestas
		global soluciones
		import ast
		Indice = ast.literal_eval(request.forms.get('Indice'))
		Pos = Tableros_generados[Indice][0]
		Tablero = Tableros_generados[Indice][1]
		result = iniciar(Pos,Tablero)
		respuestas[Indice] = result[62][2]
		if not soluciones:
			soluciones.append(Indice+1)
			soluciones.append(result[62][2])

@route('/respuesta') 
def respuestaG():
	global ind
	if ind != '':
		global respuestas
		div = ''''''
		select = '''<select id="selectRT" name="selectRT" style="visibility:hidden">'''
		for i in range(len(respuestas)):
			div += '''<div id="rt''' + str(i) + '''" style="display:none;">Respuesta del Tablero #''' + str(i+1)
			for j in respuestas[i]:
				div += '''<div>''' + str(j) + '''</div>'''
			div += '''</div>'''
			select += '<option value="' + str(respuestas[i]) +'">Solucion Tab#'+ str(i+1) +'</option>'
		select += '''</select>'''
		return Encabezado + '''
			<title>Respuesta</title>
			</head>
			<body onload="load()">
				<h4>Caballos Distribuidos - Respuesta</h4>
				''' + div + '''
				''' + select + '''
				<br><br><a href="''' + URL + '''/cliente"><button class="btn btn-primary btn-sm">Ir a cliente</button><a/>
				<script>
					function load(){
						var storedIndice = localStorage.getItem('Indice');
						var indrt = "rt" + storedIndice
						if(storedIndice) {
							document.getElementById(indrt).style.display = "block";
							document.getElementById('selectRT').selectedIndex = storedIndice;
							var storedRT = localStorage.getItem('RTablero');
							if((!storedRT) || (storedRT == 'null') || (storedRT == 'undefined')){
								localStorage.setItem('RTablero',document.getElementById('selectRT').value);
							}else{
								localStorage['RTablero'] = document.getElementById('selectRT').value;
							}
						}
					}
				</script>
			</body>
		</html>'''

@route('/soluciones') 
def solucionesG():
	global soluciones
	if soluciones:
		div = '''Primera solucion: Tablero #''' + str(soluciones[0]) + '''<br>'''
		for i in soluciones[1]:
			div += '''<div>''' + str(i) + '''</div>'''
		return Encabezado + '''
			<title>Soluciones</title>
			</head>
			<body>
				<h4>Caballos Distribuidos - Soluciones</h4>
				''' + div + '''
				<br><br><a href="''' + URL + '''/cliente"><button class="btn btn-primary btn-sm">Ir a cliente</button><a/>
			</body>
		</html>'''

run(host=direccion_equipo, port=8080)

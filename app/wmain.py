#
# (c) 2017 elias/vanissoft
#
#
#


from browser import window, document, ajax, alert
import wwebsockets
import wglobals

import json
from functools import partial

jq = window.jQuery



Menu_binds = {
	'link_limitorders': 'limit_orders.html',
	'link_dashboard': 'dashboard.html', 'link_metrics': 'metrics.html', 'link_usage': 'usage.html',
	'link_activity': 'activity.html', 'link_panels': 'panels.html', 'link_typography': 'typography.html',
	'link_icons': 'icons.html', 'link_buttons': 'buttons.html', 'link_tabs': 'tabs.html', 'link_modals': 'modals.html',
	'link_alerts': 'alerts.html', 'link_loaders': 'loaders.html', 'link_gridsystem': 'gridSystem.html',
	'link_draggable': 'draggable.html',
	'link_tablestyles': 'tableStyles.html', 'link_datatables': 'dataTables.html',
	'link_basicelements': 'formElements.html', 'link_autocomplete': 'autocomplete.html',
	'link_selectioncontrols': 'controls.html', 'link_texteditor': 'textEditor.html', 'link_flotcharts': 'flotCharts.html',
	'link_chartjs': 'chartJs.html', 'link_sparkline': 'sparkline.html', 'link_datamaps': 'datamaps.html',
	'link_profile': 'profile.html', 'link_contacts': 'contacts.html', 'link_projects': 'projects.html',
	'link_support': 'support.html', 'link_nestablelist': 'nestableList.html', 'link_timeline': 'timeline.html',
	'link_login': 'login.html', 'link_register': 'register.html', 'link_forgotpassword': 'forgotPassword.html',
	'link_error': 'error.html', 'link_versions': 'versions.html'}

Cnt = 0
Callbacks = {}
Active_module = None

def ws_received(data):
	global ws_comm
	print("wmain.ws_received")
	Active_module.incoming_data(data)


ws_comm = wwebsockets.Wscomm("ws://127.0.0.1:8808/comm", ws_received)

def init_data():
	if ws_comm.open:
		ws_comm.send({'operation': 'enqueue', 'module': "main", 'what': 'open_positions'})
		wglobals.clear_timer(0)

wglobals.set_timer(0, init_data, 0.1)


def html_loaded(url, rtn):
	global ws_comm, Active_module
	document['page_container'].innerHTML = rtn
	print("url:", url)
	if 'dashboard' in url:
		import wmoddashboard
		Active_module = wmoddashboard
	elif 'alerts' in url:
		import wmodalerts
		Active_module = wmodalerts
	elif 'draggable' in url:
		import wmoddraggable
		Active_module = wmoddraggable
	elif 'dataTables' in url:
		import wmoddatatables
		Active_module = wmoddatatables
	elif 'limit_orders' in url:
		import wmodlimitorders
		Active_module = wmodlimitorders
	else:
		return False
	if Active_module is not None:
		ws_comm.send("change from client")
		ws_comm.send({'operation': 'module_activation', 'module': Active_module.Module_name})
		Active_module.init(ws_comm)


def menu_click(ev):
	global Menu_binds, ws_comm
	query(Menu_binds[ev.target.id], html_loaded)


def query(url, callback):
	global Cnt
	url = url+"&nonce="+str(Cnt)
	Callbacks[url] = callback
	req = ajax.ajax()
	req.open('GET', url, True)
	req.send()
	func = partial(ajax_end, url)
	req.bind('complete', func)
	Cnt += 1


def ajax_end(url, request):
	global Cnt
	if request.responseText[0] == '{':
		try:
			rtn = json.loads(request.responseText)
		except Exception as err:
			print(err.__repr__())
			return
		if rtn is None:
			print("error\n"+request.responseText)
			return
		print(rtn['request'])
		if rtn['request'] in Callbacks:
			print("callback ok")
			Callbacks[rtn['request']](rtn)
			del Callbacks[rtn['request']]
	else:
		Callbacks.popitem()[1](url, request.responseText)



# bind menu links
for bind in Menu_binds.items():
	document[bind[0]].bind('click', menu_click)


print("ok2")
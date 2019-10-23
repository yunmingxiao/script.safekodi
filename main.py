import xbmcaddon
import xbmcgui
import requests
import json
 
addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
 
#line1 = "Hello World!"
#line2 = "We can write anything we want here"
#line3 = "Using Python"
 
#xbmcgui.Dialog().ok(addonname, line1, line2, line3)
#'''
resp = requests.get(
    "https://safekodi.com:5555/checkAddon",
    params={
        "addon": "plugin.video.abcfamily"
    }
)
#print(resp, resp.content)
line1 = resp.content

payload = {"uid":"svarvel", "addon_list":[{"vrs":"1.0", "name":"cnn"},{"vrs":"2.1","name":"youtube"}]}
resp = requests.post(
    "https://safekodi.com:5555/addonList",
    headers={
        "Content-Type": "application/json"
    },
    data=json.dumps(payload)
)
#print(resp, resp.status_code, resp.content)
line2 = resp.content

def get_installed_addons_info():
    json_cmd = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'Addons.GetAddons',
            'params': {
                'installed': True,
                'properties': ['dependencies', 'version','extrainfo', 'disclaimer','name','path','rating','summary','description', 'author']
                }
            }
    res = json.loads(xbmc.executeJSONRPC(json.dumps(json_cmd)))
    try:
        return res['result']['addons']
    except:
        return res

addon_list = get_installed_addons_info()
line3 = str(type(addon_list))
line4 = str(addon_list)
xbmcgui.Dialog().ok(addonname, line1, line2, line3, line4)
#'''
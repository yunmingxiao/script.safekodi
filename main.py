import xbmcaddon
import xbmcgui
import requests
try:
    import json
except:
    import simplejson as json
 
addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
 
#line1 = "Hello World!"
#line2 = "We can write anything we want here"
#line3 = "Using Python"
 
#xbmcgui.Dialog().ok(addonname, line1, line2, line3)
#'''
def get_addon(addonid):
    resp = requests.get(
        "https://safekodi.com:5555/checkAddon",
        params={
            "addon": "plugin.video.abcfamily"
        }
    )
    return resp

def post_addon(addon_list):
    payload = {"uid":"svarvel", "addon_list":[{"vrs":"1.0", "name":"cnn"},{"vrs":"2.1","name":"youtube"}]}
    resp = requests.post(
        "https://safekodi.com:5555/addonList",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    #print(resp, resp.status_code, resp.content)
    return resp

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

resp = get_installed_addons_info(addon_list)
line1 = str(resp) + str(resp.content)

line2 = ''
for addon in addon_list:
    resp = get_addon(addon['addonid'])
    line2 += str(resp) + str(resp.content) + '\n'

xbmcgui.Dialog().ok(addonname, line1, line2)
#'''
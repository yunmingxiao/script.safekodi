import sys
import os
import xbmcaddon
import xbmcplugin
from urllib import urlencode
import xbmcgui
import xbmc
import requests
try:
    import json
except:
    import simplejson as json
import uuid
 
ADDON       = xbmcaddon.Addon()
CWD = ADDON.getAddonInfo('path').decode('utf-8')
#addonname   = ADDON.getAddonInfo('name')
#SKIN = ADDON.getSetting('skin')

addon_url = sys.argv[0]
addon_handle = int(sys.argv[1])
#xbmcplugin.setContent(addon_handle, 'movies')
 

def get_addon(addonid):
    resp = requests.get(
        "https://safekodi.com:5555/checkAddon",
        params={
            "addon": addonid
        }
    )
    return resp

def post_addon(addon_list):
    payload = {"uid": uuid.getnode(), "addon_list":addon_list}
    resp = requests.post(
        "https://safekodi.com:5555/addonList",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
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


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(addon_url, urlencode(kwargs))


def list_categories(categories, addon_list):
    """
    Create the list of addons in the Kodi interface.
    """
    # Iterate through categories
    for aid in categories.keys():
        addon_msg, mark = 'Oops...\nAddon not in our database. \nPlease come back later\n', 'unknown.png'
        try:
            if 'OK' in categories[aid]:
                addon_status = json.loads('[' + categories[aid].split('[')[1].split(']')[0] + ']')
                addon_msg = ''
                if len(addon_status) == 0:
                    addon_msg = 'This addon is safe!\n'
                    mark = 'safe.png'
                if 'kodi' in addon_status:
                    addon_msg = 'This is an Kodi official addon!\n'
                    mark = 'safe.png'
                if 'ad' in addon_status:
                    addon_msg += 'This addon may contain some ads.\n'
                    mark = 'warning.png'
                if 'track' in addon_status:
                    addon_msg += 'This addon may contain some tracking links which lead to privacy leakage.\n'
                    mark = 'warning.png'
                if 'threat' in addon_status:
                    addon_msg += 'This addon may lead to some malacious URLs!\n'
                    mark = 'danger.png'
                if 'ipban' in addon_status:
                    addon_msg += 'This addon may communicate with malacious servers!\n'
                    mark = 'danger.png'
                if 'ban' in addon_status:
                    addon_msg += 'This addon is banned by the Kodi official!\n'
                    mark = 'danger.png'
                # TODO: delete this, just for debug
                addon_msg += aid + ', ' + str(addon_status)
            elif 'Connection errror!' in categories[aid]:
                addon_msg, mark = 'Oops...\nConnection error! \nPlease check your network configurations.\n', 'unknown.png'
            else:
                pass
            addon_msg += '\n\n' + 'Addon description:\n' + addon_list[aid]['description']
        except Exception as e:
            print(e)
            addon_msg = 'Error!\n' + str(addon_status) + '\n' + str(e)
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=addon_list[aid]['name'], label2=addon_msg)
        infolabels = { "title": addon_list[aid]['name'], "mpaa": addon_msg, "Plot": addon_msg }
        list_item.setInfo( type="Video", infoLabels=infolabels )
        image_path = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', mark)
        list_item.setArt({
            'thumb': image_path, 
            'icon': image_path, 
            'fanart': image_path, 
        })
        url = get_url(action='listing', category=aid)
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_SIZE)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_GENRE)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_STUDIO)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_PROGRAM_COUNT)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(addon_handle)

#xbmcplugin.endOfDirectory(addon_handle)
#xbmcgui.Dialog().ok(addonname, line2)

if __name__ == "__main__":
    addon_list = get_installed_addons_info()
    xbmc.log(str(addon_list), xbmc.LOGDEBUG)

    # report to safekodi
    try:
        resp = post_addon(addon_list)
    except Exception as e: 
        xbmc.log(str(e), xbmc.LOGDEBUG)

    # get the addon status from safekodi
    addon_status = {}
    addon_info = {}
    for addon in addon_list:
        try:
            resp = get_addon(addon['addonid'])
            addon_status[addon['addonid']] = resp.content
        except requests.ConnectionError:
            addon_status[addon['addonid']] = 'Connection errror!'

        addon_info[addon['addonid']] = {
            'name': addon['name'],
            'description': addon['description']
        }

    list_categories(addon_status, addon_info)

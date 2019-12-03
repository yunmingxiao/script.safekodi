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


def list_categories(categories):
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
                addon_msg += str(addon_status)
            else:
                pass
        except Exception as e:
            print(e)
            addon_msg = 'Error!\n' + str(addon_status) + '\n' + str(e)
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=aid, label2=addon_msg)
        infolabels = { "title": aid, "mpaa": addon_msg, "Plot": addon_msg }
        list_item.setInfo( type="Video", infoLabels=infolabels )
        image_path = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', mark)
        list_item.setArt({
            'thumb': image_path, 
            'icon': image_path, 
            'fanart': image_path, 
        })
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        #list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
        #                  'icon': VIDEOS[category][0]['thumb'],
        #                  'fanart': VIDEOS[category][0]['thumb']})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        #list_item.setInfo('video', {'title': category,
        #                            'mpaa': categories[category]})
        #                            'genre': category,
        #                            'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing', category=aid)
        # is_folder = True means that this item opens a sub-list of lower level items.
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

    # report to safekodi
    resp = post_addon(addon_list)

    addon_status = {}
    #i = 0
    for addon in addon_list:
        #i += 1
        #if i > 3:
        #    break
        resp = get_addon(addon['addonid'])
        addon_status[addon['addonid']] = resp.content

    list_categories(addon_status)

'''
class GUI(xbmcgui.WindowXML):
    def onInit(self):
        # select a view mode, '50' in our case, as defined in the skin file
        xbmc.executebuiltin('Container.SetViewMode(50)')
        # define a temporary list where we are going to add all the listitems to
        listitems = []
        # this will be the first item in the list. 'my first item' will be the label that is shown in the list
        listitem1 = xbmcgui.ListItem('my first item')
        # add this item to our temporary list
        listitems.append(listitem1)
        # let's create another item
        listitem2 = xbmcgui.ListItem('my second item')
        # and add it to the temporary list as well
        listitems.append(listitem2)
        listitem3 = xbmcgui.ListItem('my third item')
        listitems.append(listitem3)
        # by default the built-in container already contains one item, the 'up' (..) item, let's remove that one
        self.clearList()
        # now we are going to add all the items we have defined to the (built-in) container
        self.addItems(listitems)
        # give kodi a bit of (processing) time to add all items to the container
        xbmc.sleep(100)
        # this puts the focus on the top item of the container
        self.setFocusId(self.getCurrentContainerId())



if __name__ == "__main__":
    # define your xml window and pass these four (kodi 17) or five (kodi 18) arguments (more optional items can be passed as well):
    # 1 'the name of the xml file for this window', 
    # 2 'the path to your addon',
    # 3 'the name of the folder that contains the skin',
    # 4 'the name of the folder that contains the skin xml files'
    # 5 [kodi 18] set to True for a media window (a window that will list music / videos / pictures), set to False otherwise
    # 6 [optional] if you need to pass additional data to your window, simply add them to the list
    # you'll have to add them as key=value pairs: key1=value1, key2=value2, etc...
    ui = GUI('script-testwindow.xml', CWD, 'default', '1080i', False, defaultSkin=SKIN, optional1='some data') # for kodi 18 and up..
    #ui = GUI('script-testwindow.xml', CWD, 'default', '1080i', optional1='some data') # use this line instead for kodi 17 and earlier
    # now open your window. the window will be shown until you close your addon
    ui.doModal()
    # window closed, now cleanup a bit: delete your window before the script fully exits
    del ui
'''
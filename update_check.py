import sys
import os
import xbmcaddon
import xbmcplugin
from urllib import urlencode
import xbmcgui
import xbmc
import requests
import time
try:
    import json
except:
    import simplejson as json
import hashlib

from urlparse import parse_qsl

addon = xbmcaddon.Addon('script.safekodi')
addon_id = addon.getAddonInfo('id')
icon = addon.getAddonInfo('icon')


def notification(heading, message, time=15000, sound=True):
    xbmcgui.Dialog().notification(heading, message, icon, time, sound)


if __name__ == '__main__':
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        xbmc.log(str(addon), xbmc.LOGDEBUG)
        xbmc.log(str(addon_id), xbmc.LOGDEBUG)
        xbmc.log(str(icon), xbmc.LOGDEBUG)
        
        try:
            resp = requests.get(
                "https://safekodi.com/last_update.html",
            )
            last_update_online = resp.content
            xbmc.log(last_update_online, xbmc.LOGDEBUG)
            
            last_update_path = xbmc.translatePath(os.path.join('special://home', 'addons', addon_id, 'resources', 'last_update.txt'))
            with open(last_update_path, 'r') as fp:
                last_update_offline = fp.read()
            xbmc.log(last_update_offline, xbmc.LOGDEBUG)
        
            if last_update_offline != last_update_online:
                # The addon list is updated!
                xbmc.log("send notification!", xbmc.LOGDEBUG)
                notification("SafeKodi list updated", "Open SafeKodi to check latest security suggestions for installed addons.", 15000)
        except Exception as e:
            xbmc.log(str(e), xbmc.LOGDEBUG)


        if monitor.waitForAbort(60*60*12):
            # Abort was requested while waiting. We should exit
            xbmc.log('Closing SafeKodi services', xbmc.LOGNOTICE)
            break
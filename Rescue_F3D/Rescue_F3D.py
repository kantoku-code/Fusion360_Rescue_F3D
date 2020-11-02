#FusionAPI_python addin Rescue_F3D
#Author-kantoku
#Description-F3Dファイルから形状データをインポートします

import adsk.core, adsk.fusion, traceback
from .Rescue_F3D_core import execImportGeo

_app = adsk.core.Application.cast(None)
_ui  = adsk.core.UserInterface.cast(None)
_handlers = []

_cmdInfo = [
    'Rescue_F3D',
    'レスキューF3D',
    'F3Dファイルから形状データをインポートします。',
    './resources/Rescue_F3D'
]

_tabId = 'SolidTab'
_panelId = 'InsertPanel'


# 日本語と英語のメッセージ
def sLng(s):

    global _app
    lang = _app.preferences.generalPreferences.userLanguage

    langs = adsk.core.UserLanguages
    if lang == langs.JapaneseLanguage:
        return s

    sDict = {
        'レスキューF3D':'RescueF3D',
        'F3Dファイルから形状データをインポートします。':'Import shape data from an F3D file.'
    }

    if not s in sDict:
        return s

    return sDict[s]


class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            execImportGeo()

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global _ui, _handlers
            cmd = adsk.core.Command.cast(args.command)
            
            # コマンドのイベントを追加
            onExecute = CommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)


        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        panels :adsk.core.ToolbarPanels = _ui.allToolbarPanels

        global _panelId
        panel :adsk.core.ToolbarPanel = panels.itemById(_panelId)

        global _cmdInfo
        if panel:
            panel.controls.itemById(_cmdInfo[0]).deleteMe()

        global _tabId
        tabs :adsk.core.ToolbarTabs = _ui.allToolbarTabs
        tab :adsk.core.ToolbarTab = tabs.itemById(_tabId)
        if not tab:
            if tab.toolbarPanels.count < 1 and not tab.isNative:
                tab.deleteMe()

    except:
        print('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    ui = None
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # cmdDef 
        cmdDefs :adsk.core.CommandDefinitions = _ui.commandDefinitions

        global _cmdInfo
        cmdDef :adsk.core.CommandDefinition = cmdDefs.itemById(_cmdInfo[0])
        if cmdDef:
            cmdDef.deleteMe()

        cmdDef = cmdDefs.addButtonDefinition(
            _cmdInfo[0], 
            sLng(_cmdInfo[1]),
            sLng(_cmdInfo[2]),
            _cmdInfo[3])

        global _handlers
        onCommandCreated = CommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)


        # panel
        if not _ui.isTabbedToolbarUI: return

        desTabs = adsk.core.ToolbarTabs.cast(None)
        desTabs = _ui.toolbarTabsByProductType('DesignProductType')
        if desTabs.count < 1: return

        global _tabId
        targetTab :adsk.core.ToolbarTab = desTabs.itemById(_tabId)
        if not targetTab:
            _ui.messageBox('Unsupported ID(tab)')
            return

        panels :adsk.core.ToolbarPanels = targetTab.toolbarPanels
        if panels.count < 1: return

        global _panelId
        targetpanel :adsk.core.ToolbarPanel = panels.itemById(_panelId)

        if not targetpanel:
            _ui.messageBox('Unsupported ID(panel)')
            return

        controls :adsk.core.ToolbarControls = targetpanel.controls

        cmdControl :adsk.core.ToolbarControl = controls.itemById(cmdDef.id)
        if cmdControl:
            cmdControl.deleteMe()

        cmdControl = controls.addCommand(cmdDef)

        cmdControl.isVisible = True
        cmdControl.isPromoted = False
        cmdControl.isPromotedByDefault = False

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
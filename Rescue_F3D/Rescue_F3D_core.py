#FusionAPI_python addin Rescue_F3D
#Author-kantoku
#Description-F3Dファイルから形状データをインポートします

import adsk.core, adsk.fusion
import pathlib, shutil, zipfile

_app = adsk.core.Application.cast(None)
_ui  = adsk.core.UserInterface.cast(None)
_prj = adsk.core.DataProject.cast(None)

_PROJECT_NAME = 'Rescue_F3D'
_DOC_BASENAME = 'Rescue_F3D'

# -- Rescue_F3D --
def execImportGeo():
    global _app, _ui
    _app = adsk.core.Application.get()
    _ui = _app.userInterface

    # select file
    paths = showOpenDialog()
    if len(paths) < 1:
        return

    # txtcmd
    initTxtCmd()
    dumpMsg('--- start ---')

    # temp folder
    tmpFolder = getTempFolder()

    # init doc
    doc = _app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)

    # save
    global _prj
    if not _prj:
        setDataProject()
    
    docName = getNewDocName()
    doc.saveAs(docName, _prj.rootFolder, '', '')

    # try import
    for filePath in paths:
        dumpMsg('try - {}'.format(filePath))

        with zipfile.ZipFile(filePath) as existing_zip:

            # get smbh
            smbhFiles = [f for f in existing_zip.namelist() if pathlib.Path(f).suffix == '.smbh']

            # un zip
            [existing_zip.extract(f, tmpFolder) for f in smbhFiles]

            for smbh in smbhFiles:
                # smbh 2 sat
                smb = pathlib.Path(tmpFolder/smbh)
                cmd = u'ASMInterface.convertSabToSat {}'.format(smb)
                _app.executeTextCommand(cmd)

                # import sat
                sat = str(smb.parent/smb.stem) + '.sat'
                cmd = u'NaFusionUI.ImportCmd \"{}\"'.format(sat)
                _app.executeTextCommand(cmd)
                _app.executeTextCommand(u'NuCommands.CommitCmd')

                # save
                doc.save('')

        dumpMsg('done')

    # finish 
    dumpMsg('--- finish ---')


def showOpenDialog(
    initialDirectory :str = None
    ) -> list:

    global _ui
    fileDlg = _ui.createFileDialog()
    fileDlg.isMultiSelectEnabled = True
    fileDlg.title = 'f3d Open File Dialog'
    fileDlg.filter = '*.f3d'
    if initialDirectory:
        fileDlg.initialDirectory = initialDirectory
    else:
        fileDlg.initialDirectory = _app.executeTextCommand(u'Cache.path')

    dlgResult = fileDlg.showOpen()
    if dlgResult != adsk.core.DialogResults.DialogOK:
        return []

    return [p for p in fileDlg.filenames if pathlib.Path(p).exists()]


def setDataProject():

    global _app, _prj, _PROJECT_NAME
    prj = adsk.core.DataProject.cast(None)

    for prj in _app.data.dataProjects:
        if prj.name == _PROJECT_NAME:
            _prj = prj
            return

    _prj = _app.data.dataProjects.add(_PROJECT_NAME)


def initTxtCmd():

    cmdLst = [
        u'Window.Clear',# 効果なし
        u'NuCommands.ShowTextCommandsCommand'
        ]

    global _app
    [_app.executeTextCommand(c) for c in cmdLst]



def getNewDocName() -> str:

    global _prj
    docs = [f.name for f in _prj.rootFolder.dataFiles]

    global _DOC_BASENAME
    tmpName = _DOC_BASENAME

    idx = 0
    while True:
        if not tmpName in docs:
            return tmpName

        idx += 1
        tmpName = _DOC_BASENAME + '_{}'.format(idx)


def dumpMsg(msg :str):

    global _ui
    _ui.palettes.itemById('TextCommands').writeText(str(msg))


def getTempFolder():

    folder = pathlib.Path(__file__).parent/'temp'
    # folder.mkdir(exist_ok=True)
    try:
        shutil.rmtree(folder)
    except:
        pass
    finally:
        folder.mkdir(exist_ok=True)

    return folder
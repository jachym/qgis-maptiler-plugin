import os
import sip
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import *

from .browser_rastermaps import RasterCollection, RasterUserCollection
from .browser_vectormaps import VectorCollection
from .configue_dialog import ConfigueDialog
from .settings_manager import SettingsManager

ICON_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "imgs")

class DataItemProvider(QgsDataItemProvider):
    def __init__(self):
        QgsDataItemProvider.__init__(self)

    def name(self):
        return "MapTilerProvider"

    def capabilities(self):
        return QgsDataProvider.Net

    def createDataItem(self, path, parentItem):
        root = RootCollection()
        sip.transferto(root, None)
        return root


class RootCollection(QgsDataCollectionItem):
    def __init__(self):
        QgsDataCollectionItem.__init__(self, None, "MapTiler", "/MapTiler")
        self.setIcon(QIcon(os.path.join(ICON_PATH, "maptiler_icon.svg")))
    
    def createChildren(self):
        children = []

        #judge vtile is available or not
        qgis_version_str = str(Qgis.QGIS_VERSION_INT) #e.g. QGIS3.10.4 -> 31004
        minor_ver = int(qgis_version_str[1:3])

        smanager = SettingsManager()
        isVectorEnabled = int(smanager.get_setting('isVectorEnabled'))

        #Raster Mode
        if minor_ver < 13 or not isVectorEnabled:
            raster_standard_collection = RasterCollection(' Maps')
            sip.transferto(raster_standard_collection, self)
            children.append(raster_standard_collection)

            raster_user_collection = RasterUserCollection(' User Maps')
            sip.transferto(raster_user_collection, self)
            children.append(raster_user_collection)

        #Vector Mode
        else:
            #init default dataset
            vector_standard_collection = {
                'Basic':r'https://api.maptiler.com/tiles/v3/{z}/{x}/{y}.pbf?key='
            }
            vector_local_collection = {
                'Basic':r'https://api.maptiler.com/tiles/v3/{z}/{x}/{y}.pbf?key='
            }

            vector_standard_collection = VectorCollection('Standard vector tile', vector_standard_collection)
            sip.transferto(vector_standard_collection, self)
            children.append(vector_standard_collection)

            vector_local_collection = VectorCollection('Local vector tile', vector_local_collection)
            sip.transferto(vector_local_collection, self)
            children.append(vector_local_collection)

            vector_user_collection = VectorCollection('User vector tile', {}, user_editable=True)
            sip.transferto(vector_user_collection, self)
            children.append(vector_user_collection)
            
        config_action = RootOpenConfigItem(self)
        sip.transferto(config_action, self)
        children.append(config_action)

        return children

class RootOpenConfigItem(QgsDataItem):
    def __init__(self, parent):
        QgsDataItem.__init__(self, QgsDataItem.Custom, parent, "Account", "/MapTiler/config" )
        self.populate()

    def handleDoubleClick(self):
        self.open_configue_dialog()
        return True

    def actions(self, parent):
        actions = []

        config_action = QAction(QIcon(), 'Open', parent)
        config_action.triggered.connect(self.open_configue_dialog)
        actions.append(config_action)
        
        return actions

    def open_configue_dialog(self):
        configue_dialog = ConfigueDialog()
        configue_dialog.exec_()
        self.parent().refreshConnections()
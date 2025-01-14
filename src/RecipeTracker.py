#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil
import tarfile
import qdarktheme
import requests
import urllib
import json
import orjson
import traceback
import time
import os
import unicodedata
import sys
import atexit
import time
import qtpy
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *
from packaging.version import parse
from loguru import logger

QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

if parse(qtpy.QT_VERSION).major == 6:
    QImageReader.setAllocationLimit(0)

App = QApplication(sys.argv)

fmt = ("<green>{time:YYYY-MM-DD HH:mm:ss}</green> " +
       "| <level>{level}</level> | " +
       "<yellow>{file}</yellow>:<blue>{function}</blue>:<cyan>{line}</cyan> " +
       "- <level>{message}</level>")

if sys.stdout != None:
    config = {
        "handlers": [
            {"sink": sys.stdout, "format": fmt},
        ],
    }
    logger.configure(**config)
else:
    # Handle all uncaught exceptions and forward to loguru
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.critical("Uncaught exception", exc_info=(
            exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

    class LoggerWriter(object):
        def __init__(self, writer):
            self._writer = writer
            self._msg = ''

        def write(self, message):
            self._msg = self._msg + message
            while '\n' in self._msg:
                pos = self._msg.find('\n')
                self._writer(self._msg[:pos])
                self._msg = self._msg[pos+1:]

        def flush(self):
            if self._msg != '':
                self._writer(self._msg)
                self._msg = ''

    sys.stdout = LoggerWriter(logger.info)
    sys.stderr = LoggerWriter(logger.error)

logger.add(
    "./logs/tsh.log",
    format="[{time:YYYY-MM-DD HH:mm:ss}] - {level} - {file}:{function}:{line} | {message}",
    encoding="utf-8",
    level="INFO",
    rotation="20 MB"
)

logger.add(
    "./logs/tsh-error.log",
    format="[{time:YYYY-MM-DD HH:mm:ss}] - {level} - {file}:{function}:{line} | {message}",
    encoding="utf-8",
    level="ERROR",
    rotation="20 MB"
)

logger.critical("=== TSH IS STARTING ===")

logger.info("QApplication successfully initialized")

# autopep8: off
# from .Settings.TSHSettingsWindow import TSHSettingsWindow
# from .TSHHotkeys import TSHHotkeys
# from .TSHPlayerListWidget import TSHPlayerListWidget
# from .TSHCommentaryWidget import TSHCommentaryWidget
# from .TSHGameAssetManager import TSHGameAssetManager
# from .TSHBracketWidget import TSHBracketWidget
# from .TSHTournamentInfoWidget import TSHTournamentInfoWidget
# from .TSHTournamentDataProvider import TSHTournamentDataProvider
# from .TournamentDataProvider.StartGGDataProvider import StartGGDataProvider
# from .TSHAlertNotification import TSHAlertNotification
# from .TSHPlayerDB import TSHPlayerDB
# from .Workers import *
# from .SettingsManager import SettingsManager
# from .Helpers.TSHCountryHelper import TSHCountryHelper
# from .TSHScoreboardManager import TSHScoreboardManager
# from .TSHThumbnailSettingsWidget import TSHThumbnailSettingsWidget
# from src.TSHAssetDownloader import TSHAssetDownloader
# from src.TSHAboutWidget import TSHAboutWidget
# from .TSHScoreboardStageWidget import TSHScoreboardStageWidget
# from src.TSHWebServer import WebServer
# autopep8: on
from.StateManager import StateManager

class WindowSignals(QObject):
    StopTimer = Signal()

class Window(QMainWindow):
    signals = WindowSignals()

    def __init__(self, loop):
        super().__init__()

        StateManager.loop = loop
        StateManager.BlockSaving()

        self.signals = WindowSignals()

        # splash = QSplashScreen(
        #     QPixmap('assets/icons/icon.png').scaled(128, 128))
        # splash.show()

        time.sleep(0.1)

        App.processEvents()

        self.programState = {}
        self.savedProgramState = {}
        self.programStateDiff = {}

        # self.setWindowIcon(QIcon('assets/icons/icon.png'))

        if not os.path.exists("out/"):
            os.mkdir("out/")
        
        # replace this one
        # if os.path.exists("./TSH_old.exe"):
        #     os.remove("./TSH_old.exe")

        # self.font_small = QFont(
        #     "./assets/font/RobotoCondensed.ttf", pointSize=8)

        self.threadpool = QThreadPool()
        self.saveMutex = QMutex()

        # self.player_layouts = []

        # self.allplayers = None
        # self.local_players = None

        # try:
        #     version = json.load(
        #         open('./assets/versions.json', encoding='utf-8')).get("program", "?")
        # except Exception as e:
        #     version = "?"

        self.setGeometry(300, 300, 800, 100)
        # self.setWindowTitle("TournamentStreamHelper v"+version)

        self.setDockOptions(
            QMainWindow.DockOption.AllowTabbedDocks)

        self.setTabPosition(
            Qt.DockWidgetArea.AllDockWidgetAreas, QTabWidget.TabPosition.North)

        # Layout base com status no topo
        central_widget = QWidget()
        pre_base_layout = QVBoxLayout()
        central_widget.setLayout(pre_base_layout)
        self.setCentralWidget(central_widget)
        central_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.dockWidgets = []

        # saving as an example for my thing

        # self.scoreboard = TSHScoreboardManager.instance
        # self.scoreboard.setWindowIcon(QIcon('assets/icons/list.svg'))
        # self.scoreboard.setObjectName(
        #     QApplication.translate("app", "Scoreboard Manager"))
        # self.addDockWidget(
        #     Qt.DockWidgetArea.BottomDockWidgetArea, self.scoreboard)
        # self.dockWidgets.append(self.scoreboard)
        # TSHScoreboardManager.instance.setWindowTitle(
        #     QApplication.translate("app", "Scoreboard Manager"))

        # self.webserver = WebServer(
        #     parent=None, stageWidget=self.stageWidget)
        # StateManager.webServer = self.webserver
        # self.webserver.start()

        # commentary = TSHCommentaryWidget()
        # commentary.setWindowIcon(QIcon('assets/icons/mic.svg'))
        # commentary.setObjectName(QApplication.translate("app", "Commentary"))
        # self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, commentary)
        # self.dockWidgets.append(commentary)

        self.tabifyDockWidget(self.scoreboard, self.stageWidget)
        # self.tabifyDockWidget(self.scoreboard, commentary)
        self.scoreboard.raise_()

        # Game
        base_layout = QHBoxLayout()

        group_box = QWidget()
        group_box.setLayout(QVBoxLayout())
        group_box.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Maximum)
        base_layout.layout().addWidget(group_box)

        # Set tournament
        hbox = QHBoxLayout()
        group_box.layout().addLayout(hbox)

        self.setTournamentBt = QPushButton(
            QApplication.translate("app", "Set tournament"))
        hbox.addWidget(self.setTournamentBt)
        # self.setTournamentBt.clicked.connect(
        #     lambda bt=None, s=self: TSHTournamentDataProvider.instance.SetStartggEventSlug(s))

        self.unsetTournamentBt = QPushButton()
        self.unsetTournamentBt.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.unsetTournamentBt.setIcon(QIcon("./assets/icons/cancel.svg"))
        # self.unsetTournamentBt.clicked.connect(lambda: [
        #     TSHTournamentDataProvider.instance.SetTournament(None)
        # ])
        hbox.addWidget(self.unsetTournamentBt)

        # Follow startgg user
        hbox = QHBoxLayout()
        group_box.layout().addLayout(hbox)

        self.btLoadPlayerSet = QPushButton(
            QApplication.translate("app", "Load tournament and sets from StartGG user"))
        self.btLoadPlayerSet.setIcon(QIcon("./assets/icons/startgg.svg"))
        self.btLoadPlayerSet.clicked.connect(self.LoadUserSetClicked)
        self.btLoadPlayerSet.setIcon(QIcon("./assets/icons/startgg.svg"))
        hbox.addWidget(self.btLoadPlayerSet)

        # TSHTournamentDataProvider.instance.signals.user_updated.connect(
        #     self.UpdateUserSetButton)
        # TSHTournamentDataProvider.instance.signals.tournament_changed.connect(
        #     self.UpdateUserSetButton)

        self.btLoadPlayerSetOptions = QPushButton()
        self.btLoadPlayerSetOptions.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.btLoadPlayerSetOptions.setIcon(
            QIcon("./assets/icons/settings.svg"))
        self.btLoadPlayerSetOptions.clicked.connect(
            self.LoadUserSetOptionsClicked)
        hbox.addWidget(self.btLoadPlayerSetOptions)

        self.UpdateUserSetButton()

        # Settings
        menu_margin = " "*6
        self.optionsBt = QToolButton()
        self.optionsBt.setIcon(QIcon('assets/icons/menu.svg'))
        self.optionsBt.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.optionsBt.setPopupMode(QToolButton.InstantPopup)
        base_layout.addWidget(self.optionsBt)
        self.optionsBt.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.optionsBt.setFixedSize(QSize(32, 32))
        self.optionsBt.setIconSize(QSize(32, 32))
        menu = QMenu()
        self.optionsBt.setMenu(menu)
        action = menu.addAction(
            QApplication.translate("app", "Always on top"))
        action.setCheckable(True)
        action.toggled.connect(self.ToggleAlwaysOnTop)
        action = self.optionsBt.menu().addAction(
            QApplication.translate("app", "Check for updates"))
        self.updateAction = action
        action.setIcon(QIcon('assets/icons/undo.svg'))
        action.triggered.connect(self.CheckForUpdates)
        action = self.optionsBt.menu().addAction(
            QApplication.translate("app", "Download assets"))
        action.setIcon(QIcon('assets/icons/download.svg'))
        # action.triggered.connect(TSHAssetDownloader.instance.DownloadAssets)
        self.downloadAssetsAction = action

        action = self.optionsBt.menu().addAction(
            QApplication.translate("app", "Light mode"))
        action.setCheckable(True)
        self.LoadTheme()
        # action.setChecked(SettingsManager.Get("light_mode", False))
        action.toggled.connect(self.ToggleLightMode)

        toggleWidgets = QMenu(QApplication.translate(
            "app", "Toggle widgets") + menu_margin, self.optionsBt.menu())
        self.optionsBt.menu().addMenu(toggleWidgets)
        toggleWidgets.addAction(self.scoreboard.toggleViewAction())
        toggleWidgets.addAction(self.stageWidget.toggleViewAction())
        # toggleWidgets.addAction(commentary.toggleViewAction())
        # toggleWidgets.addAction(thumbnailSetting.toggleViewAction())
        # toggleWidgets.addAction(tournamentInfo.toggleViewAction())
        # toggleWidgets.addAction(playerList.toggleViewAction())
        # toggleWidgets.addAction(bracket.toggleViewAction())

        self.optionsBt.menu().addSeparator()

        action = self.optionsBt.menu().addAction(
            QApplication.translate("app", "Migrate Layout"))
        action.triggered.connect(self.MigrateWindow)

        self.optionsBt.menu().addSeparator()

        languageSelect = QMenu(QApplication.translate(
            "app", "Program Language") + menu_margin, self.optionsBt.menu())
        self.optionsBt.menu().addMenu(languageSelect)

        languageSelectGroup = QActionGroup(languageSelect)
        languageSelectGroup.setExclusive(True)

        # program_language_messagebox = generate_restart_messagebox(
        #     QApplication.translate("app", "Program language changed successfully."))

        action = languageSelect.addAction(
            QApplication.translate("app", "System language"))
        languageSelectGroup.addAction(action)
        action.setCheckable(True)
        action.setChecked(True)
        # action.triggered.connect(lambda x=None: [
        #     SettingsManager.Set("program_language", "default"),
        #     program_language_messagebox.exec()
        # ])

        # for code, language in TSHLocaleHelper.languages.items():
        #     action = languageSelect.addAction(f"{language[0]} / {language[1]}")
        #     action.setCheckable(True)
        #     languageSelectGroup.addAction(action)
        #     action.triggered.connect(lambda x=None, c=code: [
        #         SettingsManager.Set("program_language", c),
        #         program_language_messagebox.exec()
        #     ])
        #     if SettingsManager.Get("program_language") == code:
        #         action.setChecked(True)

        languageSelect = QMenu(QApplication.translate(
            "app", "Game Asset Language") + menu_margin, self.optionsBt.menu())
        self.optionsBt.menu().addMenu(languageSelect)

        languageSelectGroup = QActionGroup(languageSelect)
        languageSelectGroup.setExclusive(True)

        # game_asset_language_messagebox = generate_restart_messagebox(
        #     QApplication.translate("app", "Game Asset Language changed successfully."))

        action = languageSelect.addAction(
            QApplication.translate("app", "Same as program language"))
        languageSelectGroup.addAction(action)
        action.setCheckable(True)
        action.setChecked(True)
        # action.triggered.connect(lambda x=None: [
        #     SettingsManager.Set("game_asset_language", "default"),
        #     game_asset_language_messagebox.exec()
        # ])

        # for code, language in TSHLocaleHelper.languages.items():
        #     action = languageSelect.addAction(f"{language[0]} / {language[1]}")
        #     action.setCheckable(True)
        #     languageSelectGroup.addAction(action)
        #     action.triggered.connect(lambda x=None, c=code: [
        #         SettingsManager.Set("game_asset_language", c),
        #         game_asset_language_messagebox.exec()
        #     ])
        #     if SettingsManager.Get("game_asset_language") == code:
        #         action.setChecked(True)

        languageSelect = QMenu(QApplication.translate(
            "app", "Tournament term language") + menu_margin, self.optionsBt.menu())
        self.optionsBt.menu().addMenu(languageSelect)

        languageSelectGroup = QActionGroup(languageSelect)
        languageSelectGroup.setExclusive(True)

        # fg_language_messagebox = generate_restart_messagebox(
        #     QApplication.translate("app", "Tournament term language changed successfully."))

        action = languageSelect.addAction(
            QApplication.translate("app", "Same as program language"))
        languageSelectGroup.addAction(action)
        action.setCheckable(True)
        action.setChecked(True)
        # action.triggered.connect(lambda x=None: [
        #     SettingsManager.Set("fg_term_language", "default"),
        #     fg_language_messagebox.exec()
        # ])

        # for code, language in TSHLocaleHelper.languages.items():
        #     action = languageSelect.addAction(f"{language[0]} / {language[1]}")
        #     action.setCheckable(True)
        #     languageSelectGroup.addAction(action)
        #     action.triggered.connect(lambda x=None, c=code: [
        #         SettingsManager.Set("fg_term_language", c),
        #         fg_language_messagebox.exec()
        #     ])
        #     if SettingsManager.Get("fg_term_language") == code:
        #         action.setChecked(True)

        self.optionsBt.menu().addSeparator()

        # Help menu code
        help_messagebox = QMessageBox()
        help_messagebox.setWindowTitle(
            QApplication.translate("app", "Warning"))
        help_messagebox.setText(QApplication.translate(
            "app", "A new window has been opened in your default webbrowser."))

        helpMenu = QMenu(QApplication.translate(
            "app", "Help") + menu_margin, self.optionsBt.menu())
        self.optionsBt.menu().addMenu(helpMenu)
        action = helpMenu.addAction(
            QApplication.translate("app", "Open the Wiki"))
        wiki_url = "https://github.com/joaorb64/TournamentStreamHelper/wiki"
        action.triggered.connect(lambda x=None: [
            QDesktopServices.openUrl(QUrl(wiki_url)),
            help_messagebox.exec()
        ])

        action = helpMenu.addAction(
            QApplication.translate("app", "Look for Help on the forum"))
        help_url = "https://github.com/joaorb64/TournamentStreamHelper/discussions/categories/q-a"
        action.triggered.connect(lambda x=None: [
            QDesktopServices.openUrl(QUrl(help_url)),
            help_messagebox.exec()
        ])

        action = helpMenu.addAction(
            QApplication.translate("app", "Report a bug"))
        issues_url = "https://github.com/joaorb64/TournamentStreamHelper/issues"
        action.triggered.connect(lambda x=None: [
            QDesktopServices.openUrl(QUrl(issues_url)),
            help_messagebox.exec()
        ])

        action = helpMenu.addAction(
            QApplication.translate("app", "Ask for Help on Discord"))
        discord_url = "https://discord.gg/X9Sp2FkcHF"
        action.triggered.connect(lambda x=None: [
            QDesktopServices.openUrl(QUrl(discord_url)),
            help_messagebox.exec()
        ])

        helpMenu.addSeparator()

        action = helpMenu.addAction(
            QApplication.translate("app", "Contribute to the Asset Database"))
        asset_url = "https://github.com/joaorb64/StreamHelperAssets/"
        action.triggered.connect(lambda x=None: [
            QDesktopServices.openUrl(QUrl(asset_url)),
            help_messagebox.exec()
        ])

        # self.settingsWindow = TSHSettingsWindow(self)

        # action = self.optionsBt.menu().addAction(
        #     QApplication.translate("Settings", "Settings"))
        # action.setIcon(QIcon('assets/icons/settings.svg'))
        # action.triggered.connect(lambda: self.settingsWindow.show())

        # Game Select and Scoreboard Count
        hbox = QHBoxLayout()
        group_box.layout().addLayout(hbox)

        self.gameSelect = QComboBox()
        self.gameSelect.setEditable(True)
        self.gameSelect.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.gameSelect.completer().setCompletionMode(QCompleter.PopupCompletion)
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        proxyModel.setSourceModel(self.gameSelect.model())
        self.gameSelect.model().setParent(proxyModel)
        self.gameSelect.setModel(proxyModel)
        self.gameSelect.setFont(self.font_small)
        # self.gameSelect.activated.connect(
        #     lambda x: TSHGameAssetManager.instance.LoadGameAssets(self.gameSelect.currentData()))
        # TSHGameAssetManager.instance.signals.onLoad.connect(
        #     self.SetGame)
        # TSHGameAssetManager.instance.signals.onLoadAssets.connect(
        #     self.ReloadGames)
        # TSHGameAssetManager.instance.signals.onLoad.connect(
        #     TSHAssetDownloader.instance.CheckAssetUpdates
        # )
        # TSHAssetDownloader.instance.signals.AssetUpdates.connect(
        #     self.OnAssetUpdates
        # )
        # TSHTournamentDataProvider.instance.signals.tournament_changed.connect(
        #     self.SetGame)

        pre_base_layout.addLayout(base_layout)
        hbox.addWidget(self.gameSelect)

        self.scoreboardAmount = QSpinBox()
        self.scoreboardAmount.setMaximumWidth(100)
        self.scoreboardAmount.lineEdit().setReadOnly(True)
        self.scoreboardAmount.setMinimum(1)
        self.scoreboardAmount.setMaximum(10)

        # self.scoreboardAmount.valueChanged.connect(
        #     lambda val:
        #     TSHScoreboardManager.instance.signals.ScoreboardAmountChanged.emit(
        #         val)
        # )

        label_margin = " "*18
        label = QLabel(
            label_margin + QApplication.translate("app", "Number of Scoreboards"))
        label.setSizePolicy(QSizePolicy.Policy.Fixed,
                            QSizePolicy.Policy.Minimum)

        self.btLoadModifyTabName = QPushButton(
            QApplication.translate("app", "Modify Tab Name"))
        self.btLoadModifyTabName.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.btLoadModifyTabName.clicked.connect(self.ChangeTab)

        hbox.addWidget(label)
        hbox.addWidget(self.scoreboardAmount)
        hbox.addWidget(self.btLoadModifyTabName)

        # TSHScoreboardManager.instance.UpdateAmount(1)

        self.CheckForUpdates(True)
        self.ReloadGames()

        self.qtSettings = QSettings("joao_shino", "TournamentStreamHelper")

        if self.qtSettings.value("geometry"):
            self.restoreGeometry(self.qtSettings.value("geometry"))

        if self.qtSettings.value("windowState"):
            self.restoreState(self.qtSettings.value("windowState"))

        # splash.finish(self)
        self.show()

        # TSHCountryHelper.LoadCountries()
        # self.settingsWindow.UiMounted()
        # TSHTournamentDataProvider.instance.UiMounted()
        # TSHGameAssetManager.instance.UiMounted()
        # TSHAlertNotification.instance.UiMounted()
        # TSHAssetDownloader.instance.UiMounted()
        # TSHHotkeys.instance.UiMounted(self)
        # TSHPlayerDB.LoadDB()

        StateManager.ReleaseSaving()

        # TSHScoreboardManager.instance.signals.ScoreboardAmountChanged.connect(
        #     self.ToggleTopOption)

    def ChangeTab(self):
        tabNameWindow = QDialog(self)
        tabNameWindow.setWindowTitle(
            QApplication.translate("app", "Change Tab Title"))
        tabNameWindow.setMinimumWidth(400)
        vbox = QVBoxLayout()
        tabNameWindow.setLayout(vbox)
        hbox = QHBoxLayout()
        label = QLabel(QApplication.translate("app", "Scoreboard Number"))
        number = QSpinBox()
        number.setMinimum(1)
        # number.setMaximum(TSHScoreboardManager.instance.GetTabAmount())
        hbox.addWidget(label)
        hbox.addWidget(number)
        vbox.addLayout(hbox)
        name = QLineEdit()
        vbox.addWidget(name)

        setSelection = QPushButton(
            text=QApplication.translate("app", "Set Tab Title"))

        def UpdateTabName():
            # TSHScoreboardManager.instance.SetTabName(
            #     number.value(), name.text())
            tabNameWindow.close()

        setSelection.clicked.connect(UpdateTabName)

        vbox.addWidget(setSelection)

        tabNameWindow.show()

    def MigrateWindow(self):
        migrateWindow = QDialog(self)
        migrateWindow.setWindowTitle(
            QApplication.translate("app", "Migrate Scoreboard Layout"))
        migrateWindow.setMinimumWidth(800)
        vbox = QVBoxLayout()
        migrateWindow.setLayout(vbox)
        hbox = QHBoxLayout()
        label = QLabel(QApplication.translate("app", "File Path"))
        filePath = QLineEdit()
        fileExplorer = QPushButton(
            text=QApplication.translate("app", "Find File..."))
        hbox.addWidget(label)
        hbox.addWidget(filePath)
        hbox.addWidget(fileExplorer)
        vbox.addLayout(hbox)

        migrate = QPushButton(
            text=QApplication.translate("app", "Migrate Layout"))

        def open_dialog():
            fname, _ok = QFileDialog.getOpenFileName(
                migrateWindow,
                QApplication.translate("app", "Open Layout Javascript File"),
                os.getcwd(),
                QApplication.translate("app", "Javascript File") + "  (*.js)",
            )
            if fname:
                filePath.setText(str(fname))

        fileExplorer.clicked.connect(open_dialog)

        def MigrateLayout():
            data = None
            with open(filePath.text(), 'r') as file:
                data = file.read()

                data = data.replace("data.score.", "data.score[1].")
                data = data.replace("oldData.score.", "oldData.score[1].")
                data = data.replace(
                    "_.get(data, \"score.stage_strike.", "_.get(data, \"score.1.stage_strike.")
                data = data.replace(
                    "_.get(oldData, \"score.stage_strike.", "_.get(oldData, \"score.1.stage_strike.")
                data = data.replace(
                    "source: `score.team.${t + 1}`", "source: `score.1.team.${t + 1}`")
                data = data.replace(
                    "data.score[1].ruleset", "data.score.ruleset")

            with open(filePath.text(), 'w') as file:
                file.write(data)

            logger.info("Completed Layout Migration at: " + filePath.text())

            completeDialog = QDialog(migrateWindow)
            completeDialog.setWindowTitle(
                QApplication.translate("app", "Migration Complete"))
            completeDialog.setMinimumWidth(500)
            vbox2 = QVBoxLayout()
            completeDialog.setLayout(vbox2)
            completeText = QLabel(QApplication.translate(
                "app", "Layout Migration has completed!"))
            completeText.setAlignment(Qt.AlignmentFlag.AlignCenter)
            closeButton = QPushButton(
                text=QApplication.translate("app", "Close Window"))
            vbox2.addWidget(completeText)
            vbox2.addWidget(closeButton)
            closeButton.clicked.connect(completeDialog.close)
            completeDialog.show()

        migrate.clicked.connect(MigrateLayout)

        vbox.addWidget(migrate)

        migrateWindow.show()

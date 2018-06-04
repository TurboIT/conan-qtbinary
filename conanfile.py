from conans import ConanFile, tools
import os


QtInstallerTemplate = '''function Controller() {
    installer.installationFinished.connect(function() {
        gui.clickButton(buttons.NextButton, 500);
    })
}

Controller.prototype.WelcomePageCallback = function() {
    gui.clickButton(buttons.NextButton, 1000);
}

Controller.prototype.CredentialsPageCallback = function() {
    gui.clickButton(buttons.NextButton, 500);
}

Controller.prototype.IntroductionPageCallback = function() {
    gui.clickButton(buttons.NextButton, 500);
} 

Controller.prototype.TargetDirectoryPageCallback = function() {
    gui.currentPageWidget().TargetDirectoryLineEdit.setText("*INSTALL_PATH*");
    gui.clickButton(buttons.NextButton, 500)
}

Controller.prototype.ComponentSelectionPageCallback = function() {
    
    var widget = gui.currentPageWidget();
    widget.deselectAll()
    widget.selectComponent("*PLATFORM_MODULE*");
    gui.clickButton(buttons.NextButton, 500)
}

Controller.prototype.LicenseAgreementPageCallback = function() {
    gui.currentPageWidget().AcceptLicenseRadioButton.setChecked(true);
    gui.clickButton(buttons.NextButton);
}


Controller.prototype.StartMenuDirectoryPageCallback = function() {
    gui.clickButton(buttons.NextButton, 500)
}

Controller.prototype.ReadyForInstallationPageCallback = function() {
    gui.clickButton(buttons.NextButton, 500);
}


Controller.prototype.InstallationFinishedPageCallback = function() {
    gui.clickButton(buttons.NextButton, 500)
}


Controller.prototype.FinishedPageCallback = function() {
    var checkBoxForm = gui.currentPageWidget().LaunchQtCreatorCheckBoxForm
    if (checkBoxForm && checkBoxForm.launchQtCreatorCheckBox) {
        checkBoxForm.launchQtCreatorCheckBox.checked = false;
    }
    gui.clickButton(buttons.FinishButton, 500);
}'''

class Qt5BinaryConan(ConanFile):
    name = "qt5binary"
    version = "5.11"
    license = "LGPL"
    url = "http://code.turboit.co.uk/conan/catch2.git"
    description = "Qt5"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "*"
    qt_version = "5.11.0"
    qt_module_version = "5110"
    url_base = "http://download.qt.io/official_releases/qt/%s/%s/" % (version, qt_version)
    keep_imports = "yes"
    short_paths = True
    qt_binarydir = None
    qt_module = None
    qt_installer = None
		
    def build(self):
        qt_module = None
        qt_installer = None

        if self.settings.os == 'Linux':
            if self.settings.compiler == 'gcc' or self.settings.compiler == 'clang':
                self.qt_binarydir = "gcc_64"
                self.qt_module = 'qt.qt5.%s.gcc_64' % self.qt_module_version
                self.qt_installer = 'qt-opensource-linux-x64-%s.run' % self.qt_version

        if self.settings.os == 'Windows':
            if self.settings.compiler == 'Visual Studio':
                self.qt_binarydir = "msvc2017_64"
                self.qt_installer = 'qt-opensource-windows-x86-%s.exe' % self.qt_version
                if self.settings.compiler.version == '15':
                    self.qt_module = 'qt.qt5.%s.win64_msvc2017_64' % self.qt_module_version

        if self.settings.os == 'Macos':
            if self.settings.compiler == 'clang' or self.settings.compiler == 'apple-clang':
                self.qt_module = None
                self.qt_installer = None

        if self.qt_module == None or self.qt_installer == None or self.qt_binarydir == None:
            self.output.error("OS:%s and Compiler:%s:%s not supported" % (self.settings.os, self.settings.compiler, self.settings.compiler.version))
            exit(1)

        tools.get(self.url_base + self.qt_installer)
        build_folder = self.build_folder
        if self.settings.os == 'Windows':
            build_folder = build_folder.replace("/","\\")

        install_folder = os.path.join(build_folder, 'Qt')
        if self.settings.os == 'Windows':
            install_folder = install_folder.replace("\\", "\\\\")
			
        script = QtInstallerTemplate.replace('*PLATFORM_MODULE*', self.qt_module)
        script = script.replace('*INSTALL_PATH*', install_folder)
        f = open(os.path.join(build_folder, 'install.qs'),'w')
        f.write(script)
        f.close()
		
        if self.settings.os == 'Linux' or self.settings.os == "Macos":
            self.run("chmod +x %s/%s" % (build_folder,  self.qt_installer))
        print("%s --script %s" % (os.path.join(build_folder,  self.qt_installer), os.path.join(build_folder, "install.qs")))
        self.run("%s --script %s" % (os.path.join(build_folder,  self.qt_installer), os.path.join(build_folder, "install.qs")))

    def package(self):
        build_folder = self.build_folder
        if self.settings.os == 'Windows':
            build_folder = build_folder.replace("/","\\")

        src_folder = os.path.join(build_folder, "Qt", self.qt_version, self.qt_binarydir)
        self.copy(pattern="*", dst="lib", src="%s/lib" % src_folder, keep_path=True)
        self.copy(pattern="*", dst="bin", src="%s/bin" % src_folder, keep_path=True)
        self.copy(pattern="*", dst="include", src="%s/include" % src_folder, keep_path=True)
        self.copy(pattern="*", dst="mkspecs", src="%s/mkspecs" % src_folder, keep_path=True)
        self.copy(pattern="*", dst="plugins", src="%s/plugins" % src_folder, keep_path=True)

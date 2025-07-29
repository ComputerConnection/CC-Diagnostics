import QtQuick
import QtQuick.Controls
import App.Styles 1.0
import "."

ApplicationWindow {
    id: root
    visible: true
    title: qsTr("CC Diagnostics")
    property bool darkMode: false
    Material.theme: darkMode ? Material.Dark : Material.Light

    Component.onCompleted: {
        var val = diagnostics.loadSetting("dark_mode")
        if (val !== undefined && val !== null) {
            darkMode = val
        }
    }

    property int progressValue: 0
    property string logText: ""
    property var recommendationItems: []
    property bool remoteEnabled: false
    property string uploadStatus: ""
    property string exportFormat: "html"
    property bool scanRunning: false

    SettingsDialog {
        id: settingsDialog
    }

    StackView {
        id: stack
        anchors.fill: parent
        initialItem: mainPage
    }

    Component {
        id: mainPage
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Styles.spacingLarge
            spacing: Styles.spacingLarge

            StatusCard {
                Layout.fillWidth: true
                loading: root.scanRunning
                content: Column {
                    spacing: Styles.spacingMedium
                    Text {
                        id: statusLabel
                        text: qsTr("Ready to scan")
                        font.family: Styles.fontFamily
                        font.pixelSize: Styles.fontSizeLarge
                        color: Styles.primaryColor
                    }

                    ProgressBar {
                        id: bar
                        from: 0
                        to: 100
                        value: root.progressValue
                        Layout.fillWidth: true
                    }

                    Row {
                        spacing: Styles.spacingMedium
                        CheckBox {
                            id: remoteToggle
                            checked: root.remoteEnabled
                            text: qsTr("Remote")
                            font.family: Styles.fontFamily
                            font.pixelSize: Styles.fontSizeMedium
                            onCheckedChanged: {
                                root.remoteEnabled = checked
                                diagnostics.setRemoteEnabled(checked)
                            }
                        }
                        Text {
                            text: root.uploadStatus
                            font.family: Styles.fontFamily
                            font.pixelSize: Styles.fontSizeSmall
                            color: Styles.secondaryColor
                        }
                    }
                }
            }



            Button {
                text: qsTr("Run Scan")
                icon.name: "play_arrow"
                onClicked: {
                    root.progressValue = 0
                    root.logText = ""
                    root.scanRunning = true
                    reportView.loading = true
                    diagnostics.runScan()
                }
            }

            ComboBox {
                id: formatBox
                model: ["HTML", "PDF"]
                onActivated: {
                    root.exportFormat = currentIndex === 0 ? "html" : "pdf"
                }
            }

            Button {
                text: qsTr("Export")
                icon.name: "save"
                onClicked: {
                    var dir = StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
                    diagnostics.exportReport(dir, root.exportFormat)
                }
            }

            Button {
                text: qsTr("Settings")
                icon.name: "settings"
                onClicked: settingsDialog.open()
            }

            TextArea {
                id: logArea
                text: root.logText
                readOnly: true
                Layout.fillWidth: true
                Layout.preferredHeight: 120
                font.family: Styles.fontFamily
                font.pixelSize: Styles.fontSizeSmall
            }

            Recommendations {
                id: recList
                items: root.recommendationItems
            }
        }
    }

    Component {
        id: reportPage
        ReportView {
            id: reportView
            anchors.fill: parent
            onBackRequested: stack.pop()
        }
    }

    Connections {
        target: diagnostics
        function onProgress(percent, message) {
            root.progressValue = percent
            root.logText += message + "\n"
        }
        function onLog(message) {
            root.logText += message + "\n"
        }
        function onCompleted(msg) {
            statusLabel.text = msg
            reportView.reportData = diagnostics.loadLatestReport()
            stack.push(reportPage)
            root.scanRunning = false
        }
        function onRecommendationsUpdated(list) {
            root.recommendationItems = list
        }
        function onUploadStatus(status) {
            root.uploadStatus = status
        }
        function onLoading(flag) {
            root.scanRunning = flag
            if (flag) {
                reportView.loading = true
            }
        }
    }
}

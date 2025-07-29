import QtQuick
import QtQuick.Controls

ApplicationWindow {
    id: root
    visible: true
    width: 400
    height: 300
    title: qsTr("CC Diagnostics")

    property int progressValue: 0
    property string logText: ""
    property var recommendationItems: []
    property bool remoteEnabled: false
    property string uploadStatus: ""
    property string exportFormat: "html"

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
        Column {
            anchors.centerIn: parent
            spacing: 20

            Text {
                id: statusLabel
                text: qsTr("Ready to scan")
            }

            ProgressBar {
                id: bar
                from: 0
                to: 100
                value: root.progressValue
                width: 300
            }

            Row {
                spacing: 10
                CheckBox {
                    id: remoteToggle
                    checked: root.remoteEnabled
                    text: qsTr("Remote")
                    onCheckedChanged: {
                        root.remoteEnabled = checked
                        diagnostics.setRemoteEnabled(checked)
                    }
                }
                Text { text: root.uploadStatus }
            }

            Button {
                text: qsTr("Run Scan")
                icon.name: "play_arrow"
                onClicked: {
                    root.progressValue = 0
                    root.logText = ""
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
                width: 350
                height: 120
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
        }
        function onRecommendationsUpdated(list) {
            root.recommendationItems = list
        }
        function onUploadStatus(status) {
            root.uploadStatus = status
        }
    }
}

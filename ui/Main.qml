import QtQuick
import QtQuick.Controls

ApplicationWindow {
    id: root
    visible: true
    width: 400
    height: 300
    title: qsTr("CC Diagnostics")

    Column {
        anchors.centerIn: parent
        spacing: 20

        Text {
            id: statusLabel
            text: qsTr("Ready to scan")
        }

        Button {
            text: qsTr("Run Scan")
            onClicked: diagnostics.runScan()
        }
    }
}

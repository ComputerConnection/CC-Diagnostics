import QtQuick
import QtQuick.Controls

Dialog {
    id: root
    modal: true
    property string serverEndpoint: ""
    property bool remoteUpload: false
    property bool darkMode: false

    onOpened: {
        darkCheck.checked = root.parent.darkMode
        endpointField.text = root.serverEndpoint
        remoteCheck.checked = root.remoteUpload
    }

    title: qsTr("Settings")

    Column {
        spacing: 10
        anchors.fill: parent
        anchors.margins: 20

        TextField {
            id: endpointField
            placeholderText: qsTr("Server Endpoint")
            text: root.serverEndpoint
        }

        CheckBox {
            id: remoteCheck
            text: qsTr("Enable Remote Upload")
            checked: root.remoteUpload
        }

        CheckBox {
            id: darkCheck
            text: qsTr("Dark Mode")
            checked: root.darkMode
        }

        Row {
            spacing: 8
            Button {
                text: qsTr("Save")
                onClicked: {
                    diagnostics.updateSetting("server_endpoint", endpointField.text)
                    diagnostics.updateSetting("remote_upload", remoteCheck.checked)
                    diagnostics.updateSetting("dark_mode", darkCheck.checked)
                    root.darkMode = darkCheck.checked
                    root.parent.darkMode = darkCheck.checked
                    root.close()
                }
            }
            Button {
                text: qsTr("Cancel")
                onClicked: root.close()
            }
        }
    }
}

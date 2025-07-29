import QtQuick
import QtQuick.Controls

Dialog {
    id: root
    modal: true
    property string serverEndpoint: ""
    property bool remoteUpload: false

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

        Row {
            spacing: 8
            Button {
                text: qsTr("Save")
                onClicked: {
                    diagnostics.updateSetting("server_endpoint", endpointField.text)
                    diagnostics.updateSetting("remote_upload", remoteCheck.checked)
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

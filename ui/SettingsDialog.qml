import QtQuick
import QtQuick.Controls
import App.Styles 1.0

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
        spacing: Styles.spacingMedium
        anchors.fill: parent
        anchors.margins: Styles.spacingLarge

        TextField {
            id: endpointField
            placeholderText: qsTr("Server Endpoint")
            text: root.serverEndpoint
            font.family: Styles.fontFamily
            font.pixelSize: Styles.fontSizeMedium
        }

        CheckBox {
            id: remoteCheck
            text: qsTr("Enable Remote Upload")
            checked: root.remoteUpload
            font.family: Styles.fontFamily
            font.pixelSize: Styles.fontSizeMedium
        }

        CheckBox {
            id: darkCheck
            text: qsTr("Dark Mode")
            checked: root.darkMode
            font.family: Styles.fontFamily
            font.pixelSize: Styles.fontSizeMedium
        }

        Row {
            spacing: Styles.spacingMedium
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

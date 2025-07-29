import QtQuick
import QtQuick.Controls
import App.Styles 1.0

Column {
    id: root
    property var items: []
    spacing: Styles.spacingSmall

    Repeater {
        model: root.items
        delegate: Row {
            spacing: Styles.spacingMedium
            Text {
                text: "\ud83d\udca1" // lightbulb emoji
                font.family: Styles.fontFamily
                font.pixelSize: Styles.fontSizeLarge
                color: Styles.tertiaryColor
            }
            Text {
                text: modelData.text
                font.family: Styles.fontFamily
                font.pixelSize: Styles.fontSizeMedium
            }
            Button {
                text: qsTr("More")
                visible: modelData.action !== undefined
                onClicked: diagnostics.runAction(modelData.action)
            }
        }
    }
}

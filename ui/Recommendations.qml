import QtQuick
import QtQuick.Controls

Column {
    id: root
    property var items: []
    spacing: 6

    Repeater {
        model: root.items
        delegate: Row {
            spacing: 8
            Text { text: "\ud83d\udca1" } // lightbulb emoji
            Text { text: modelData.text }
            Button {
                text: qsTr("More")
                visible: modelData.action !== undefined
                onClicked: diagnostics.runAction(modelData.action)
            }
        }
    }
}

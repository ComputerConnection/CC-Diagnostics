import QtQuick
import QtQuick.Controls
import "Styles.qml" as Styles

Rectangle {
    id: card
    radius: 6
    color: Qt.application.palette.base
    border.color: Styles.primaryColor

    default property alias content: contentArea.data

    Column {
        id: contentArea
        anchors.fill: parent
        anchors.margins: Styles.spacingMedium
        spacing: Styles.spacingSmall
    }
}

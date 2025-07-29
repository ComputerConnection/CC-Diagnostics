import QtQuick
import QtQuick.Controls
import "Styles.qml" as Styles

Rectangle {
    id: card
    radius: 6
    color: Qt.application.palette.base
    border.color: Styles.primaryColor

    property bool loading: false

    default property alias content: contentArea.data

    Column {
        id: contentArea
        anchors.fill: parent
        anchors.margins: Styles.spacingMedium
        spacing: Styles.spacingSmall
        opacity: card.loading ? Styles.disabledOpacity : 1
        Behavior on opacity { NumberAnimation { duration: 200 } }
    }

    Rectangle {
        anchors.fill: parent
        radius: 6
        color: Qt.lighter(Styles.secondaryColor, 1.5)
        opacity: card.loading ? Styles.overlayOpacity : 0
        visible: opacity > 0
        Behavior on opacity { NumberAnimation { duration: 200 } }

        BusyIndicator {
            anchors.centerIn: parent
            running: card.loading
            visible: card.loading
        }
    }
}

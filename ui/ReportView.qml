import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import App.Styles 1.0

Page {
    id: root
    title: qsTr("Diagnostic Report")
    signal backRequested()
    property var reportData: {}
    property bool loading: true

    onReportDataChanged: loading = false

    ColumnLayout {
        id: contentArea
        anchors.fill: parent
        anchors.margins: Styles.spacingLarge
        spacing: Styles.spacingMedium
        opacity: root.loading ? 0 : 1
        Behavior on opacity { NumberAnimation { duration: 200 } }

        RowLayout {
            Layout.fillWidth: true
            spacing: Styles.spacingMedium
            Label {
                text: qsTr("Status:")
                font.family: Styles.fontFamily
                font.pixelSize: Styles.fontSizeMedium
            }
            Text {
                text: root.reportData.status || ""
                font.family: Styles.fontFamily
                font.pixelSize: Styles.fontSizeMedium
                font.bold: true
                color: Styles.primaryColor
            }
        }

        Column {
            spacing: Styles.spacingSmall
            visible: (root.reportData.warnings || []).length > 0
            Label {
                text: qsTr("Warnings")
                font.family: Styles.fontFamily
                font.pixelSize: Styles.fontSizeMedium
                font.bold: true
                color: Styles.secondaryColor
            }
            Repeater {
                model: root.reportData.warnings || []
                delegate: RowLayout {
                    spacing: Styles.spacingSmall
                    Label {
                        text: Material.icons.warning
                        color: Styles.secondaryColor
                        font.pixelSize: Styles.fontSizeMedium
                    }
                    Text {
                        text: modelData
                        font.family: Styles.fontFamily
                        font.pixelSize: Styles.fontSizeSmall
                    }
                }
            }
        }

        Recommendations {
            id: recList
            items: root.reportData.recommendations || []
        }

        Button {
            text: qsTr("Back")
            icon.name: "arrow_back"
            onClicked: root.backRequested()
        }
    }

    BusyIndicator {
        anchors.centerIn: parent
        running: root.loading
        visible: root.loading
        opacity: root.loading ? Styles.overlayOpacity : 0
        Behavior on opacity { NumberAnimation { duration: 200 } }
    }
}

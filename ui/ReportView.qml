import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

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
        anchors.margins: 20
        spacing: 12
        opacity: root.loading ? 0 : 1
        Behavior on opacity { NumberAnimation { duration: 200 } }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            Label { text: qsTr("Status:") }
            Text { text: root.reportData.status || ""; font.bold: true }
        }

        Column {
            spacing: 4
            visible: (root.reportData.warnings || []).length > 0
            Label { text: qsTr("Warnings") ; font.bold: true }
            Repeater {
                model: root.reportData.warnings || []
                delegate: RowLayout {
                    spacing: 6
                    Label { text: Material.icons.warning }
                    Text { text: modelData }
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
        opacity: root.loading ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 200 } }
    }
}

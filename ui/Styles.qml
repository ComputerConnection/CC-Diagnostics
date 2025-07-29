import QtQuick
import QtQuick.Controls

QtObject {
    readonly property int spacingSmall: 4
    readonly property int spacingMedium: 8
    readonly property int spacingLarge: 16
    readonly property color primaryColor: Material.color(Material.Blue)
    readonly property color secondaryColor: Material.color(Material.Grey)
    readonly property color tertiaryColor: Material.color(Material.Green)

    readonly property string fontFamily: "Segoe UI"
    readonly property int fontSizeSmall: 12
    readonly property int fontSizeMedium: 14
    readonly property int fontSizeLarge: 18

    readonly property real elevationLow: 2
    readonly property real elevationMedium: 6
    readonly property real elevationHigh: 12
    readonly property real overlayOpacity: 0.6
    readonly property real disabledOpacity: 0.3
}

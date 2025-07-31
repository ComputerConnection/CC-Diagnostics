pragma Singleton
import QtQuick
import QtQuick.Controls

QtObject {
    // === SPACING SYSTEM ===
    // 8px base unit following Apple's grid system
    readonly property int spacingXs: 4      // 0.5x
    readonly property int spacingSmall: 8   // 1x - base unit
    readonly property int spacingMedium: 16 // 2x
    readonly property int spacingLarge: 24  // 3x
    readonly property int spacingXl: 32     // 4x
    readonly property int spacingXxl: 48    // 6x
    readonly property int spacingXxxl: 64   // 8x
    
    // === TYPOGRAPHY SYSTEM ===
    // Apple-inspired type scale with perfect readability
    readonly property string fontFamily: Qt.platform.os === "osx" ? "SF Pro Display" : 
                                         Qt.platform.os === "windows" ? "Segoe UI Variable" : "Inter"
    readonly property string fontFamilyMono: Qt.platform.os === "osx" ? "SF Mono" : 
                                            Qt.platform.os === "windows" ? "Cascadia Code" : "JetBrains Mono"
    
    // Type scale (modular scale 1.250 - major third)
    readonly property int fontSizeXs: 10     // Caption 2
    readonly property int fontSizeSmall: 12  // Caption 1  
    readonly property int fontSizeMedium: 14 // Footnote
    readonly property int fontSizeLarge: 16  // Body
    readonly property int fontSizeXl: 20     // Headline
    readonly property int fontSizeXxl: 24    // Title 3
    readonly property int fontSizeXxxl: 28   // Title 2
    readonly property int fontSizeDisplay: 34 // Title 1
    
    // Font weights
    readonly property int fontWeightLight: Font.Light      // 300
    readonly property int fontWeightRegular: Font.Normal   // 400
    readonly property int fontWeightMedium: Font.DemiBold  // 600
    readonly property int fontWeightSemibold: Font.Bold    // 700
    
    // === COLOR SYSTEM ===
    // Semantic color palette with dark mode support
    readonly property bool isDarkMode: Material.theme === Material.Dark
    
    // Primary colors - Dynamic blue system
    readonly property color primaryColor: isDarkMode ? "#007AFF" : "#007AFF"
    readonly property color primaryColorLight: isDarkMode ? "#5AC8FA" : "#5AC8FA"  
    readonly property color primaryColorDark: isDarkMode ? "#0051D5" : "#0051D5"
    
    // Secondary colors - Neutral grays
    readonly property color secondaryColor: isDarkMode ? "#8E8E93" : "#8E8E93"
    readonly property color tertiaryColor: isDarkMode ? "#48C78E" : "#48C78E"
    
    // Background colors - Adaptive system
    readonly property color backgroundPrimary: isDarkMode ? "#000000" : "#FFFFFF"
    readonly property color backgroundSecondary: isDarkMode ? "#1C1C1E" : "#F2F2F7"
    readonly property color backgroundTertiary: isDarkMode ? "#2C2C2E" : "#FFFFFF"
    readonly property color backgroundGrouped: isDarkMode ? "#000000" : "#F2F2F7"
    
    // Surface colors with elevation
    readonly property color surfaceColor: isDarkMode ? "#1C1C1E" : "#FFFFFF"
    readonly property color surfaceColorElevated: isDarkMode ? "#2C2C2E" : "#FFFFFF"
    
    // Text colors - High contrast hierarchy  
    readonly property color textPrimary: isDarkMode ? "#FFFFFF" : "#000000"
    readonly property color textSecondary: isDarkMode ? "#EBEBF5" : "#3C3C43"
    readonly property color textTertiary: isDarkMode ? "#EBEBF5" : "#3C3C43"
    readonly property color textQuaternary: isDarkMode ? "#EBEBF5" : "#3C3C43"
    
    // Status colors - Semantic feedback
    readonly property color successColor: "#30D158"    // System Green
    readonly property color warningColor: "#FF9F0A"    // System Orange  
    readonly property color errorColor: "#FF3B30"      // System Red
    readonly property color infoColor: "#5AC8FA"       // System Blue
    
    // Border and separator colors
    readonly property color borderColor: isDarkMode ? "#38383A" : "#C6C6C8"
    readonly property color separatorColor: isDarkMode ? "#38383A" : "#C6C6C8"
    readonly property color separatorColorOpaque: isDarkMode ? "#38383A" : "#C6C6C8"
    
    // === ELEVATION SYSTEM ===
    // Consistent shadow system for depth
    readonly property real elevationNone: 0
    readonly property real elevationLow: 1      // 1dp - subtle
    readonly property real elevationMedium: 4   // 4dp - cards  
    readonly property real elevationHigh: 8     // 8dp - modals
    readonly property real elevationExtreme: 16 // 16dp - floating
    
    // Shadow properties
    readonly property color shadowColor: isDarkMode ? "#000000" : "#000000"
    readonly property real shadowOpacity: isDarkMode ? 0.3 : 0.15
    
    // === OPACITY SYSTEM ===
    readonly property real opacityDisabled: 0.3      // Disabled elements
    readonly property real opacitySecondary: 0.6     // Secondary elements
    readonly property real opacityTertiary: 0.4      // Tertiary elements  
    readonly property real opacityOverlay: 0.6       // Modal overlays
    readonly property real opacityHover: 0.04        // Hover states
    readonly property real opacityPressed: 0.08      // Pressed states
    readonly property real opacityFocus: 0.12        // Focus states
    
    // === BORDER RADIUS SYSTEM ===
    readonly property real radiusNone: 0
    readonly property real radiusSmall: 4     // Small elements
    readonly property real radiusMedium: 8    // Standard elements  
    readonly property real radiusLarge: 12    // Cards, panels
    readonly property real radiusXl: 16       // Large containers
    readonly property real radiusRound: 999   // Fully rounded
    
    // === ANIMATION SYSTEM ===
    // Apple-inspired easing curves and durations
    readonly property int durationFast: 200      // Quick feedback
    readonly property int durationMedium: 300    // Standard transitions
    readonly property int durationSlow: 500      // Complex animations
    readonly property int durationEnter: 250     // Enter animations
    readonly property int durationExit: 200      // Exit animations
    
    // Easing curves - Apple-style motion
    readonly property var easingStandard: Easing.OutCubic       // Most common
    readonly property var easingDecelerate: Easing.OutQuart     // Enter animations  
    readonly property var easingAccelerate: Easing.InQuart      // Exit animations
    readonly property var easingSharp: Easing.OutBack          // Attention-getting
    
    // === LAYOUT SYSTEM ===
    // Consistent layout constraints
    readonly property int layoutMarginSmall: spacingMedium    // 16px
    readonly property int layoutMarginMedium: spacingLarge    // 24px  
    readonly property int layoutMarginLarge: spacingXl        // 32px
    
    // Component specific sizes
    readonly property int buttonHeight: 44        // Apple's minimum touch target
    readonly property int inputHeight: 44         // Consistent form controls
    readonly property int cardMinHeight: 120      // Minimum card height
    readonly property int headerHeight: 64        // Standard header height
    readonly property int toolbarHeight: 56       // Toolbar height
    
    // === ACCESSIBILITY SYSTEM ===
    readonly property int focusOutlineWidth: 2
    readonly property color focusOutlineColor: primaryColor
    readonly property real accessibilityMinContrast: 4.5  // WCAG AA standard
    
    // === Z-INDEX SYSTEM ===
    readonly property int zIndexBase: 0
    readonly property int zIndexDropdown: 1000
    readonly property int zIndexSticky: 1020  
    readonly property int zIndexFixed: 1030
    readonly property int zIndexModal: 1040
    readonly property int zIndexPopover: 1050
    readonly property int zIndexTooltip: 1060
    readonly property int zIndexToast: 1070
    
    // === BREAKPOINT SYSTEM ===
    readonly property int breakpointMobile: 480    // Small phones
    readonly property int breakpointTablet: 768    // Tablets  
    readonly property int breakpointDesktop: 1024  // Desktop
    readonly property int breakpointWide: 1440     // Wide screens
}

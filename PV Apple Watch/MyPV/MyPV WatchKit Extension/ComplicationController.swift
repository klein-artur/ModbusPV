//
//  ComplicationController.swift
//  MyPV WatchKit Extension
//
//  Created by Artur Hellmann on 15.08.22.
//

import ClockKit


class ComplicationController: NSObject, CLKComplicationDataSource {
    
    // MARK: - Complication Configuration

    func getComplicationDescriptors(handler: @escaping ([CLKComplicationDescriptor]) -> Void) {
        let descriptors = [
            CLKComplicationDescriptor(identifier: "batteryState", displayName: "Batterieladung", supportedFamilies: [.graphicCorner])
        ]
        
        // Call the handler with the currently supported complication descriptors
        handler(descriptors)
    }
    
    func handleSharedComplicationDescriptors(_ complicationDescriptors: [CLKComplicationDescriptor]) {
        // Do any necessary work to support these newly shared complication descriptors
    }

    // MARK: - Timeline Configuration
    
    func getTimelineEndDate(for complication: CLKComplication, withHandler handler: @escaping (Date?) -> Void) {
        // Call the handler with the last entry date you can currently provide or nil if you can't support future timelines
        handler(nil)
    }
    
    func getPrivacyBehavior(for complication: CLKComplication, withHandler handler: @escaping (CLKComplicationPrivacyBehavior) -> Void) {
        // Call the handler with your desired behavior when the device is locked
        handler(.showOnLockScreen)
    }

    // MARK: - Timeline Population
    
    func getCurrentTimelineEntry(for complication: CLKComplication, withHandler handler: @escaping (CLKComplicationTimelineEntry?) -> Void) {

        guard let currentData = DataRepository.shared.lastStatus else {
            handler(nil)
            return
        }

        let timelineEntry = CLKComplicationTimelineEntry(
            date: .now,
            complicationTemplate: CLKComplicationTemplateGraphicCornerGaugeImage(
                gaugeProvider: CLKSimpleGaugeProvider(
                    style: .fill,
                    gaugeColors: [.green, .yellow, .orange, .red].reversed(),
                    gaugeColorLocations: [0, 0.25, 0.5, 0.75],
                    fillFraction: Float(currentData.batteryState) / 100.0
                ),
                leadingTextProvider: CLKSimpleTextProvider(text: currentData.batteryState.pcString),
                trailingTextProvider: nil,
                imageProvider: CLKFullColorImageProvider(fullColorImage: UIImage(systemName: "bolt.batteryblock")!.withTintColor(.orange, renderingMode: .alwaysTemplate))
            )
        )

        handler(timelineEntry)
    }
    
    func getTimelineEntries(for complication: CLKComplication, after date: Date, limit: Int, withHandler handler: @escaping ([CLKComplicationTimelineEntry]?) -> Void) {
        // Call the handler with the timeline entries after the given date
        handler(nil)
    }

    // MARK: - Sample Templates
    
    func getLocalizableSampleTemplate(for complication: CLKComplication, withHandler handler: @escaping (CLKComplicationTemplate?) -> Void) {
        // This method will be called once per supported complication, and the results will be cached
        handler(
            CLKComplicationTemplateGraphicCornerGaugeImage(
                gaugeProvider: CLKSimpleGaugeProvider(
                    style: .fill,
                    gaugeColors: [.green, .yellow, .orange, .red].reversed(),
                    gaugeColorLocations: [0, 0.25, 0.5, 0.75],
                    fillFraction: 0.5
                ),
                leadingTextProvider: CLKSimpleTextProvider(text: "0"),
                trailingTextProvider: CLKSimpleTextProvider(text: "100"),
                imageProvider: CLKFullColorImageProvider(fullColorImage: UIImage(systemName: "bolt.batteryblock")!.withTintColor(.orange, renderingMode: .alwaysTemplate))
            )
        )
    }
}

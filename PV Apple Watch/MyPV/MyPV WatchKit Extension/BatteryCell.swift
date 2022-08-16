//
//  ConsumptionCell.swift
//  MyPV WatchKit Extension
//
//  Created by Artur Hellmann on 15.08.22.
//

import SwiftUI

struct BatteryCell: View {
    let state: PVState?

    var body: some View {
        if let state = state {
            VStack(alignment: .center) {
                Text("Batterie")
                    .font(.caption2)

                HStack {
                    Text("Ladung")
                    Spacer()
                    Gauge(value: Double(state.batteryState), in: 0.0...100.0) {
                    } currentValueLabel: {
                        Text("\(state.batteryState)")
                            .foregroundColor(Color.green)
                    } minimumValueLabel: {
                        Text("\(0)")
                            .foregroundColor(Color.green)
                    } maximumValueLabel: {
                        Text("\(100)")
                            .foregroundColor(Color.red)
                    }
                    .gaugeStyle(CircularGaugeStyle(tint: Gradient(colors: [.green, .yellow, .orange, .red].reversed())))
                }

                if state.batteryCharge > 0 {
                    HStack {
                        Text("Ladestrom:")
                        Spacer()
                        Text(state.batteryCharge.kwString)
                    }
                }

            }
        }
    }
}

struct BatteryCell_Previews: PreviewProvider {
    static var previews: some View {
        BatteryCell(
            state: PVState(gridOutput: -0.0275, batteryCharge: -0.625, pvInput: 0.0, batteryState: 84, consumption: 0.6525, pvSystemOutput: 0.625, timestamp: 1660590867)
        )
    }
}

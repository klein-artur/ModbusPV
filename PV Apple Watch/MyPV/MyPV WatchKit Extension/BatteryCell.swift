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

                Gauge(value: Double(state.batteryState), in: 0.0...100.0) {
                    } currentValueLabel: {
                        Text("\(state.batteryState)")
                            .foregroundColor(Color.green)
                    } minimumValueLabel: {
                        Text("\(0)")
                            .foregroundColor(Color.red)
                    } maximumValueLabel: {
                        Text("\(100)")
                            .foregroundColor(Color.green)
                    }
                    .gaugeStyle(CircularGaugeStyle(tint: Gradient(colors: [.green, .yellow, .orange, .red].reversed())))

                HStack {
                    Text(state.batteryCharge >= 0 ? "Lädt:" : "Entlädt:")
                    Spacer()
                    Text(abs(state.batteryCharge).kwString)
                        .foregroundColor(state.batteryCharge >= 0 ? .green : .red)
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

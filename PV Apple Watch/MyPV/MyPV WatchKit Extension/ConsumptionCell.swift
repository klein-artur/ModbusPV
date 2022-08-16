//
//  ConsumptionCell.swift
//  MyPV WatchKit Extension
//
//  Created by Artur Hellmann on 15.08.22.
//

import SwiftUI

struct ConsumptionCell: View {
    let state: PVState?

    var body: some View {
        if let state = state {
            VStack(alignment: .center) {
                Text("Verbrauch")
                    .font(.caption2)
                Text(state.consumption.kwString)
                    .font(.largeTitle)
                    .foregroundColor(state.consumptionColor)

                HStack {
                    Text("PV")
                    Spacer()
                    Text(state.pvInput.kwString)
                }
                Gauge(value: state.pvPercent) { }
                    .gaugeStyle(LinearGaugeStyle(tint: Gradient(colors: [.green, .yellow, .orange, .red].reversed())))

                HStack {
                    Text("Batterie")
                    Spacer()
                    Text((state.batteryCharge <= 0 ? state.batteryCharge * -1 : 0.0).kwString)
                }
                Gauge(value: state.batteryPercent) { }
                    .gaugeStyle(LinearGaugeStyle(tint: Gradient(colors: [.green, .yellow, .orange])))

                HStack {
                    Text("Netz")
                    Spacer()
                    Text((state.gridOutput <= 0 ? state.gridOutput * -1 : 0.0).kwString)
                }
                Gauge(value: state.gridPercent) { }
                    .gaugeStyle(LinearGaugeStyle(tint: Gradient(colors: [.green, .yellow, .orange, .red])))
            }
        }
    }
}

struct ConsumptionCell_Previews: PreviewProvider {
    static var previews: some View {
        ConsumptionCell(
            state: PVState(gridOutput: -0.0275, batteryCharge: -0.625, pvInput: 0.0, batteryState: 84, consumption: 0.6525, pvSystemOutput: 0.625, timestamp: 1660590867)
        )
    }
}

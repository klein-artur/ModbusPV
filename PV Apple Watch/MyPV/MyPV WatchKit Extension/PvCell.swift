//
//  ConsumptionCell.swift
//  MyPV WatchKit Extension
//
//  Created by Artur Hellmann on 15.08.22.
//

import SwiftUI

struct PvCell: View {
    let state: PVState?

    var body: some View {
        if let state = state {
            VStack(alignment: .center) {
                Text("PV Leistung")
                    .font(.caption2)
                Text(state.pvInput.kwString)
                    .font(.largeTitle)
                    .foregroundColor(Color.green)
                HStack {
                    Text("Netz:")
                    Spacer()
                    Text(abs(state.gridOutput).kwString)
                        .foregroundColor(state.gridOutputColor)
                }
                if state.batteryCharge > 0 {
                    HStack {
                        Text("Batterie:")
                        Spacer()
                        Text(abs(state.batteryCharge).kwString)
                            .foregroundColor(Color.green)
                    }
                }
            }
        }
    }
}

struct PvCell_Previews: PreviewProvider {
    static var previews: some View {
        PvCell(
            state: PVState(gridOutput: -0.4055, batteryCharge: 3.978, pvInput: 6.005, batteryState: 66, consumption: 2.4325, pvSystemOutput: 2.027, timestamp: 1660632147)
        )
    }
}

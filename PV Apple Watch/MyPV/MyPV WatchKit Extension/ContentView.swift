//
//  ContentView.swift
//  MyPV WatchKit Extension
//
//  Created by Artur Hellmann on 15.08.22.
//

import SwiftUI

struct ContentView: View {

    @ObservedObject var viewModel = MainViewModel()

    var body: some View {
        List {
            HStack {
                Text("PV Leistung:")
                Spacer()
                Text(String(format: "%.3f", viewModel.data?.pvInput ?? 0.0))
            }
            HStack {
                Text("System Out:")
                Spacer()
                Text(String(format: "%.3f", viewModel.data?.pvSystemOutput ?? 0.0))
            }
            if ((viewModel.data?.batteryCharge ?? 0.0) < 0) {
                HStack {
                    Text("Bat. Ant:")
                    Spacer()
                    Text(String(format: "%.3f", abs(viewModel.data?.batteryCharge ?? 0.0)))
                }
            }
            HStack {
                Text("Verbrauch:")
                Spacer()
                Text(String(format: "%.3f", viewModel.data?.consumption ?? 0.0))
            }
            HStack {
                Text((viewModel.data?.gridOutput ?? 0.0) >= 0 ? "Einsp:" : "Netzbez:")
                Spacer()
                Text(String(format: "%.3f", abs(viewModel.data?.gridOutput ?? 0.0)))
            }
            HStack {
                Text("Batterie:")
                Spacer()
                Text(String(format: "%d %%", viewModel.data?.batteryState ?? 0.0))
            }

        }
        .refreshable {
            await self.viewModel.loadData()
        }
        .toolbar {
            ToolbarItem(placement: ToolbarItemPlacement.primaryAction) {
                Button {
                    Task {
                        await self.viewModel.loadData()
                    }
                } label: {
                    Text("Aktualisieren")
                }
            }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}

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
            PvCell(state: viewModel.data)
                .padding(.vertical, 8.0)
            ConsumptionCell(state: viewModel.data)
                .padding(.vertical, 8.0)
            BatteryCell(state: viewModel.data)
                .padding(.vertical, 8.0)
        }
        .refreshable {
            await self.viewModel.loadData()
        }
        .onAppear {
            viewModel.startViewModelObservation()
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}

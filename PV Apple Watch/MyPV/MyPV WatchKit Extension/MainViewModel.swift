//
//  File.swift
//  MyPV WatchKit Extension
//
//  Created by Artur Hellmann on 15.08.22.
//

import Foundation
import SwiftUI

class MainViewModel: ObservableObject {

    @Published var data: PVState?

    private let dataRepository = DataRepository.shared

    // private let timer: Timer

    init() {
        Task {
            await loadData()
        }
    }

    func loadData() async {
        self.data = await self.dataRepository.getStatus()
    }

}

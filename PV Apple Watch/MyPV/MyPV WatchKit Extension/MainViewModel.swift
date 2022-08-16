//
//  File.swift
//  MyPV WatchKit Extension
//
//  Created by Artur Hellmann on 15.08.22.
//

import Foundation
import SwiftUI

@MainActor
class MainViewModel: ObservableObject {

    @Published var data: PVState?

    private let dataRepository = DataRepository.shared

    private var timer: Timer?

    init() {
        Task {
            await loadData()
        }
    }

    func loadData() async {
        do {
            self.data = try await self.dataRepository.getStatus()
        } catch {
            print(error)
        }
    }

    func startViewModelObservation() {
        print("Starting overservation")
        timer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { [weak self] _ in
            Task {
                await self?.loadData()
            }
        }
    }

}

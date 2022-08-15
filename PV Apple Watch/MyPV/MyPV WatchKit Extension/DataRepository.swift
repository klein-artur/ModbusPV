//
//  DataRepository.swift
//  MyPV WatchKit Extension
//
//  Created by Artur Hellmann on 15.08.22.
//

import Foundation

typealias DataListener = (PVState) -> Void

struct PVState: Decodable {
    let gridOutput: Float
    let batteryCharge: Float
    let pvInput: Float
    let batteryState: Int
    let consumption: Float
    let pvSystemOutput: Float
    let timestamp: Int
}

class DataRepository {
    static let shared = DataRepository()

    private var timer: Timer?

    private var currentListener: DataListener?

    func getStatus() async -> PVState? {
        if let url = URL(string: "\(SERVER_ADRESS)/Server/state.php") {
            let (data, _) = try! await URLSession.shared.data(from: url)
            return try! JSONDecoder().decode(PVState.self, from: data)
        } else {
            return nil
        }
    }
}

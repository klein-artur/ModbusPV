//
//  DataRepository.swift
//  MyPV WatchKit Extension
//
//  Created by Artur Hellmann on 15.08.22.
//

import Foundation
import SwiftUI
import ClockKit

typealias DataListener = (PVState) -> Void

struct PVState: Codable {
    let gridOutput: Float
    let batteryCharge: Float
    let pvInput: Float
    let batteryState: Int
    let consumption: Float
    let pvSystemOutput: Float
    let timestamp: Int
}

class DataRepository: NSObject {

    static let stateURL = "\(SERVER_ADRESS)/state.php"

    static let LAST_DATA_KEY = "LAST_DATA_KEY"

    static let shared = DataRepository()

    private let defaults: UserDefaults = UserDefaults.standard

    private var timer: Timer?

    private var currentListener: DataListener?

    var lastStatus: PVState? {
        guard let data = defaults.data(forKey: Self.LAST_DATA_KEY) else {
            return nil
        }
        return try? JSONDecoder().decode(PVState.self, from: data)
    }

    func getStatus() async throws -> PVState? {
        if let url = URL(string: Self.stateURL) {
            let (data, _) = try! await URLSession.shared.data(from: url) // (try! JSONEncoder().encode(PVState(gridOutput: -0.4055, batteryCharge: 3.978, pvInput: 6.005, batteryState: 66, consumption: 2.4325, pvSystemOutput: 2.027, timestamp: 1660632147)), nil as Any?)
            defaults.set(data, forKey: Self.LAST_DATA_KEY)
            defaults.synchronize()
            return try JSONDecoder().decode(PVState.self, from: data)
        } else {
            return nil
        }
    }
}

extension Float {
    var kwString: String {
        String(format: "%.3f KW", self)
    }
}

extension Int {
    var pcString: String {
        String(format: "%d %%", self)
    }
}

extension PVState {
    var consumptionColor: Color {
        if consumption / pvSystemOutput < 0.7 {
            return Color.green
        } else if consumption / pvSystemOutput > 1 {
            return Color.red
        } else {
            return Color.orange
        }
    }

    var gridOutputColor: Color {
        if gridOutput < 0 {
            return Color.red
        } else {
            return Color.green
        }
    }

    var pvProportionOfConsumption: Float {
        pvInput - (batteryCharge > 0 ? batteryCharge : 0)
    }

    var pvPercent: Float {
        pvInput / consumption
    }

    var batteryPercent: Float {
        abs(batteryCharge <= 0 ? batteryCharge / consumption : 0.0)
    }

    var gridPercent: Float {
        abs(gridOutput <= 0 ? gridOutput / consumption : 0.0)
    }
}

//
//  DataRepository.swift
//  MyPV WatchKit Extension
//
//  Created by Artur Hellmann on 15.08.22.
//

import Foundation
import SwiftUI

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

    func getStatus() async throws -> PVState? {
        if let url = URL(string: "\(SERVER_ADRESS)/Server/state.php") {
            let (data, _) = try! await URLSession.shared.data(from: url)
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

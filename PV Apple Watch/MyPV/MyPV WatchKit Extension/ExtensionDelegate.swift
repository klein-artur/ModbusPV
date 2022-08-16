//
//  ExtensionDelegate.swift
//  MyPV WatchKit Extension
//
//  Created by Artur Hellmann on 16.08.22.
//

import WatchKit

class ExtensionDelegate: NSObject, WKExtensionDelegate, ObservableObject {
    func handle(_ backgroundTasks: Set<WKRefreshBackgroundTask>) {
        if WKExtension.shared().applicationState == .background {
            Task {
                _ = try? await DataRepository.shared.getStatus()
            }
        }
    }

}

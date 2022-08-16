//
//  ExtensionDelegate.swift
//  MyPV WatchKit Extension
//
//  Created by Artur Hellmann on 16.08.22.
//

import WatchKit

class ExtensionDelegate: NSObject, WKExtensionDelegate, ObservableObject {
    
    func handle(_ backgroundTasks: Set<WKRefreshBackgroundTask>) {
        Task {
            WKExtension.shared().scheduleBackgroundRefresh(
                withPreferredDate: Date.now.addingTimeInterval(15 * 60),
                userInfo: nil) { _ in }
            _ = try? await DataRepository.shared.getStatus()

            backgroundTasks.forEach { $0.setTaskCompletedWithSnapshot(false) }
        }
    }

    func applicationWillResignActive() {
        WKExtension.shared().scheduleBackgroundRefresh(
            withPreferredDate: Date.now.addingTimeInterval(15 * 60),
            userInfo: nil) { _ in }
    }

}

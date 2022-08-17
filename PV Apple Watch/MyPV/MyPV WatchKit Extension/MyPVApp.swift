//
//  MyPVApp.swift
//  MyPV WatchKit Extension
//
//  Created by Artur Hellmann on 15.08.22.
//

import SwiftUI

@main
struct MyPVApp: App {

    @WKExtensionDelegateAdaptor private var extensionDelegate: ExtensionDelegate

    @SceneBuilder var body: some Scene {

        WindowGroup {
            NavigationView {
                ContentView()
            }
        }

        WKNotificationScene(controller: NotificationController.self, category: "myCategory")
    }
}
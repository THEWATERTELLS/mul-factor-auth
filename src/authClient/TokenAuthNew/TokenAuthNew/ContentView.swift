//
//  ContentView.swift
//  TokenAuth
//
//  Created by 张鹏浩 on 2024/12/5.
//
import SwiftUI
import Network
import CryptoKit
import SwiftUI
import Network
import CryptoKit
import CoreLocation

struct ContentView: View {
    @State private var responseMessage = "No response yet..."

    var body: some View {
            VStack(spacing: 20) {

                Text("Login Request")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .padding(.top, 230)
                
                Text(responseMessage)
                    .font(.system(size: 18, weight: .medium, design: .monospaced))
                    .foregroundColor(.blue)
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .center)
                    .background(Color(.systemGray6))
                    .cornerRadius(10)
                    .shadow(radius: 5)
                
                Button(action: {
                    sendHello { response in
                        DispatchQueue.main.async {
                            self.responseMessage = response
                        }
                    }
                }) {
                    Text("Send Login Request")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.blue)
                        .cornerRadius(10)
                        .shadow(radius: 5)
                }
                .padding(.horizontal, 20)
                
                Spacer()
            }
            .padding()
            .background(Color(.systemBackground)) // 背景颜色根据系统模式自动调整
        }

    func sendHello(completion: @escaping (String) -> Void) {
        // Network connection setup
        let host = NWEndpoint.Host("127.0.0.1")
        let port = NWEndpoint.Port(integerLiteral: 12345)

        let connection = NWConnection(host: host, port: port, using: .tcp)
        connection.start(queue: .global())

        connection.stateUpdateHandler = { state in
            switch state {
            case .ready:
                print("Connected to server")
                
                // Send message to server
                let message = "admin,104.00:30.56"
                connection.send(content: message.data(using: .utf8), completion: .contentProcessed { error in
                    if let error = error {
                        print("Send error: \(error)")
                        completion("Failed to send message")
                        connection.cancel()
                        return
                    }

                    print("Message sent")
                })

                print("about to activate receive...")
                // Receive encrypted OTP
                connection.receive(minimumIncompleteLength: 1, maximumLength: 1024) { data, _, isComplete, error in
                    if let error = error {
                        print("Receive error: \(error)")
                        completion("Failed to receive response")
                        connection.cancel()
                        return
                    }
                    print("receive activated")


                    if let data = data {
                        print("Received encrypted OTP (Base64): \(String(data: data, encoding: .utf8) ?? "Invalid Data")")

                        // Decode Base64 and decrypt OTP
                        if let otp = decryptOTP(data) {
                            completion("Decrypted OTP: \(otp)")
                        } else {
                            completion("Failed to decrypt OTP")
                        }

                        connection.cancel()
                    }
                }
            case .failed(let error):
                print("Connection failed: \(error)")
                completion("Connection failed")
            case .cancelled:
                print("Connection cancelled")
            default:
                break
            }
        }
    }

    func decryptOTP(_ encryptedData: Data) -> String? {
        // Load private key from file (replace this with your method of accessing the private key)
        guard let privateKeyPath = Bundle.main.path(forResource: "adminSK", ofType: "pem"),
              let privateKeyPem = try? String(contentsOfFile: privateKeyPath, encoding: .utf8) else {
            print("Failed to load private key")
            return nil
        }
        //print("private key pem content: \(privateKeyPem)")

        // Parse the private key from PEM format
        guard let privateKey = try? loadPrivateKey() else {
            print("Failed to parse private key")
            return nil
        }

        // Decrypt the data
        let base64DecodedData = Data(base64Encoded: encryptedData)
        guard let encryptedBytes = base64DecodedData else {
            print("Base64 decoding failed")
            return nil
        }

        var error: Unmanaged<CFError>?
        guard let decryptedData = SecKeyCreateDecryptedData(
            privateKey,
            SecKeyAlgorithm.rsaEncryptionOAEPSHA256,
            encryptedBytes as CFData,
            &error
        ) else {
            print("Decryption failed: \(error?.takeRetainedValue().localizedDescription ?? "Unknown error")")
            return nil
        }

        // Convert decrypted data to string
        return String(data: decryptedData as Data, encoding: .utf8)
    }
}

// Helper function to parse PEM formatted private key

func loadPrivateKey() -> SecKey? {
    guard let privateKeyPath = Bundle.main.path(forResource: "adminSK", ofType: "pem") else {
        print("Private key file not found")
        return nil
    }
    guard let pemContent = try? String(contentsOfFile: privateKeyPath, encoding: .utf8) else {
        print("Failed to read private key file")
        return nil
    }

    print("Original PEM content:\n\(pemContent)")

    let cleanedPem = pemContent
        .replacingOccurrences(of: "\r", with: "")
        .replacingOccurrences(of: "-----BEGIN PRIVATE KEY-----", with: "")
        .replacingOccurrences(of: "-----END PRIVATE KEY-----", with: "")
        .replacingOccurrences(of: "\n", with: "")
        .trimmingCharacters(in: .whitespacesAndNewlines)

    print("Cleaned base64 key string: \(cleanedPem)")

    guard let derData = Data(base64Encoded: cleanedPem) else {
        print("Failed to base64 decode the private key")
        return nil
    }

    print("DER data length: \(derData.count) bytes")

    let attributes: [CFString: Any] = [
        kSecAttrKeyType: kSecAttrKeyTypeRSA,
        kSecAttrKeyClass: kSecAttrKeyClassPrivate,
        kSecAttrKeySizeInBits: 2048
    ]

    var error: Unmanaged<CFError>?
    guard let privateKey = SecKeyCreateWithData(derData as CFData, attributes as CFDictionary, &error) else {
        let errorMessage = error?.takeRetainedValue().localizedDescription ?? "Unknown error"
        print("Failed to create SecKey: \(errorMessage)")
        return nil
    }

    print("Private key successfully created")
    return privateKey
}
class LocationManager: NSObject, ObservableObject, CLLocationManagerDelegate {
    private let locationManager = CLLocationManager()

    @Published var currentLocation: CLLocationCoordinate2D?
    @Published var validationResult: String?

    override init() {
        super.init()
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.requestWhenInUseAuthorization()
        locationManager.startUpdatingLocation()
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        DispatchQueue.main.async {
            self.currentLocation = location.coordinate
            self.validationResult = self.validateLocationCraftMessage(username: "admin", location: location.coordinate)
        }
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("Failed to get location: \(error.localizedDescription)")
    }

    private func validateLocationCraftMessage(username: String, location: CLLocationCoordinate2D) -> String? {
        // 目标位置和容差范围
        let targetLatitude: Double = 30.56
        let targetLongitude: Double = 104.00
        let tolerance: Double = 0.01 // 容差范围

        let isWithinLatitude = abs(location.latitude - targetLatitude) <= tolerance
        let isWithinLongitude = abs(location.longitude - targetLongitude) <= tolerance

        if isWithinLatitude && isWithinLongitude {
            return String(format: "%@,%.2f:%.2f", username, location.longitude, location.latitude)
        } else {
            return nil
        }
    }
}

//func SecKeyCreateWithPEMKey(_ pemKey: String, isPrivate: Bool) throws -> SecKey? {
//    let keyData = pemKey
//        .replacingOccurrences(of: "-----BEGIN PRIVATE KEY-----", with: "")
//        .replacingOccurrences(of: "-----END PRIVATE KEY-----", with: "")
//        .replacingOccurrences(of: "\n", with: "")
//        .trimmingCharacters(in: .whitespacesAndNewlines)
//
//    print("stripped base64 key data: \(keyData)")
//    
//    guard let data = Data(base64Encoded: keyData) else {
//        throw NSError(domain: "Invalid PEM format", code: -1, userInfo: nil)
//    }
//    
//    print("base64 decoding succeeded. data lenth: \(data.count) bytes")
//    
////    let fileURL = FileManager.default.temporaryDirectory.appendingPathComponent("private_key.der")
////    try? data.write(to: fileURL)
////    print("Saved decoded private key to: \(fileURL.path)")
//
//    let attributes: [CFString: Any] = [
//        kSecAttrKeyType: kSecAttrKeyTypeRSA,
//        kSecAttrKeyClass: isPrivate ? kSecAttrKeyClassPrivate : kSecAttrKeyClassPublic,
//        kSecAttrKeySizeInBits: 2048
//    ]
//
//    var error: Unmanaged<CFError>?
//    guard let secKey = SecKeyCreateWithData(data as CFData, attributes as CFDictionary, &error) else {
//            let errorMessage = error?.takeRetainedValue().localizedDescription ?? "Unknown error"
//            throw NSError(domain: "Failed to create SecKey: \(errorMessage)", code: -1, userInfo: nil)
//        }
//
//    return secKey
//}

#Preview {
    ContentView()
}

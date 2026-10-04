import Foundation
import Security

// Only stdin carries the value; no credentials in argv, files or diagnostic output.
struct Input: Decodable { let action: String; let account: String; let value: String? }
let input = try JSONDecoder().decode(Input.self, from: FileHandle.standardInput.readDataToEndOfFile())
var query: [String: Any] = [kSecClass as String: kSecClassGenericPassword,
    kSecAttrService as String: "affiliate-console.local", kSecAttrAccount as String: input.account,
    kSecAttrSynchronizable as String: false]
var status: OSStatus = errSecParam
switch input.action {
case "save":
    let data = Data((input.value ?? "").utf8)
    status = SecItemUpdate(query as CFDictionary, [kSecValueData as String: data] as CFDictionary)
    if status == errSecItemNotFound {
        query[kSecValueData as String] = data
        query[kSecAttrAccessible as String] = kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        status = SecItemAdd(query as CFDictionary, nil)
    }
case "read":
    query[kSecReturnData as String] = true
    query[kSecMatchLimit as String] = kSecMatchLimitOne
    var result: CFTypeRef?
    status = SecItemCopyMatching(query as CFDictionary, &result)
    if status == errSecSuccess, let data = result as? Data {
        FileHandle.standardOutput.write(data)
        exit(0)
    }
case "remove":
    status = SecItemDelete(query as CFDictionary)
    if status == errSecItemNotFound { status = errSecSuccess }
default: break
}
if status != errSecSuccess { exit(1) }

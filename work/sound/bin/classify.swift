import Foundation
import SoundAnalysis
import AVFoundation

// Usage: classify.swift <audio-file> [windowSeconds]
// Prints per-window top classifications from the built-in sound classifier.
// This is machine classifier evidence, not human audition.

let args = CommandLine.arguments
guard args.count >= 2 else {
    FileHandle.standardError.write("usage: classify.swift file [window_s]\n".data(using: .utf8)!)
    exit(2)
}
let path = args[1]
let windowSec: Double = args.count > 2 ? Double(args[2])! : 1.5

let url = URL(fileURLWithPath: path)
guard let analyzer = try? SNAudioFileAnalyzer(url: url) else {
    FileHandle.standardError.write("cannot open \(path)\n".data(using: .utf8)!)
    exit(1)
}
guard let request = try? SNClassifySoundRequest(classifierIdentifier: .version1) else {
    FileHandle.standardError.write("no classifier\n".data(using: .utf8)!)
    exit(1)
}
request.overlapFactor = 0.5
request.windowDuration = CMTime(seconds: windowSec, preferredTimescale: 1000)

final class Obs: NSObject, SNResultsObserving {
    var last: CMTime = .zero
    func request(_ request: SNRequest, didProduce result: SNResult) {
        guard let r = result as? SNClassificationResult else { return }
        let t = CMTimeGetSeconds(r.timeRange.start)
        let top = r.classifications.filter { $0.confidence > 0.05 }.prefix(4)
        let line = top.map { String(format: "%@:%.2f", $0.identifier, $0.confidence) }.joined(separator: ",")
        if !line.isEmpty { print(String(format: "%7.2f %@", t, line)) }
    }
    func request(_ request: SNRequest, didFailWithError error: Error) {
        FileHandle.standardError.write("err: \(error.localizedDescription)\n".data(using: .utf8)!)
    }
    func requestDidComplete(_ request: SNRequest) {}
}
let obs = Obs()
try? analyzer.add(request, withObserver: obs)
analyzer.analyze()
print("DONE")

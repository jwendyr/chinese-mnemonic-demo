import AVFoundation
import CoreMedia
import Foundation

// Usage: concat_mp4 <output.mp4> <input1.mp4> <input2.mp4> ...
let args = CommandLine.arguments
guard args.count >= 3 else {
    fputs("Usage: concat_mp4 <output.mp4> <input1.mp4> [input2.mp4 ...]\n", stderr)
    exit(1)
}

let outputURL = URL(fileURLWithPath: args[1])
let inputURLs = args[2...].map { URL(fileURLWithPath: $0) }
try? FileManager.default.removeItem(at: outputURL)

func runExport(comp: AVMutableComposition, preset: String, dest: URL) async -> Error? {
    try? FileManager.default.removeItem(at: dest)
    guard let exporter = AVAssetExportSession(asset: comp, presetName: preset) else {
        return NSError(domain: "concat_mp4", code: 1, userInfo: [NSLocalizedDescriptionKey: "Cannot create AVAssetExportSession for \(preset)"])
    }
    exporter.outputURL = dest
    exporter.outputFileType = .mp4
    exporter.shouldOptimizeForNetworkUse = true
    await exporter.export()
    if exporter.status == .completed {
        return nil
    }
    return exporter.error ?? NSError(domain: "concat_mp4", code: 2, userInfo: [NSLocalizedDescriptionKey: "Export failed with status \(exporter.status.rawValue)"])
}

let group = DispatchGroup()
group.enter()
Task {
    do {
        let comp = AVMutableComposition()
        guard let compV = comp.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid),
              let compA = comp.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid) else {
            fputs("Failed to create composition tracks\n", stderr)
            exit(1)
        }

        var cursor = CMTime.zero
        for url in inputURLs {
            let asset = AVURLAsset(url: url)
            guard let vTrack = try await asset.loadTracks(withMediaType: .video).first,
                  let aTrack = try await asset.loadTracks(withMediaType: .audio).first else {
                fputs("Missing video/audio track in \(url.path)\n", stderr)
                exit(1)
            }
            let vRange = try await vTrack.load(.timeRange)
            let aRange = try await aTrack.load(.timeRange)
            let segDur = CMTimeMinimum(vRange.duration, aRange.duration)
            try compV.insertTimeRange(CMTimeRange(start: vRange.start, duration: segDur), of: vTrack, at: cursor)
            try compA.insertTimeRange(CMTimeRange(start: aRange.start, duration: segDur), of: aTrack, at: cursor)
            cursor = CMTimeAdd(cursor, segDur)
        }

        if let err = await runExport(comp: comp, preset: AVAssetExportPresetPassthrough, dest: outputURL) {
            fputs("Passthrough fallback (\(err.localizedDescription)), retrying HighestQuality...\n", stderr)
            if let err2 = await runExport(comp: comp, preset: AVAssetExportPresetHighestQuality, dest: outputURL) {
                fputs("Export failed: \(err2.localizedDescription)\n", stderr)
                exit(1)
            }
        }
        print("Stitched \(outputURL.path) (\(String(format: "%.2f", cursor.seconds))s)")
        group.leave()
    } catch {
        fputs("Stitch error: \(error)\n", stderr)
        exit(1)
    }
}
group.wait()

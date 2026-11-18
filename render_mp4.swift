import AVFoundation
import AppKit
import CoreGraphics
import CoreMedia
import Foundation

// Usage: render_mp4 <output.mp4> <audio.wav> <img1:dur1> <img2:dur2> ...
let args = CommandLine.arguments
guard args.count >= 4 else {
    fputs("Usage: render_mp4 <output.mp4> <audio.wav> <img1:dur1> ...\n", stderr)
    exit(1)
}

let outputURL = URL(fileURLWithPath: args[1])
let audioURL = URL(fileURLWithPath: args[2])
try? FileManager.default.removeItem(at: outputURL)

var segments: [(URL, Double)] = []
for item in args[3...] {
    let parts = item.split(separator: ":", maxSplits: 1)
    guard parts.count == 2, let dur = Double(parts[1]) else {
        fputs("Invalid segment: \(item)\n", stderr)
        exit(1)
    }
    segments.append((URL(fileURLWithPath: String(parts[0])), dur))
}

let width = 1080
let height = 1920
let fps: Int32 = 30

// Step 1: Write video-only MP4 using AVAssetWriter
let videoOnlyURL = FileManager.default.temporaryDirectory.appendingPathComponent("video_only_\(UUID().uuidString).mp4")
try? FileManager.default.removeItem(at: videoOnlyURL)

let writer = try AVAssetWriter(outputURL: videoOnlyURL, fileType: .mp4)
let videoSettings: [String: Any] = [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width,
    AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [
        AVVideoAverageBitRateKey: 6_000_000,
        AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel,
    ],
]
let writerInput = AVAssetWriterInput(mediaType: .video, outputSettings: videoSettings)
writerInput.expectsMediaDataInRealTime = false

let adaptor = AVAssetWriterInputPixelBufferAdaptor(
    assetWriterInput: writerInput,
    sourcePixelBufferAttributes: [
        kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
        kCVPixelBufferWidthKey as String: width,
        kCVPixelBufferHeightKey as String: height,
    ]
)

writer.add(writerInput)
writer.startWriting()
writer.startSession(atSourceTime: .zero)

func makePixelBuffer(from imageURL: URL, alpha: CGFloat = 1.0) -> CVPixelBuffer? {
    guard let nsImage = NSImage(contentsOf: imageURL),
          let cgImage = nsImage.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        return nil
    }
    var pxBuffer: CVPixelBuffer?
    let attrs: [String: Any] = [
        kCVPixelBufferCGImageCompatibilityKey as String: true,
        kCVPixelBufferCGBitmapContextCompatibilityKey as String: true,
    ]
    CVPixelBufferCreate(kCFAllocatorDefault, width, height, kCVPixelFormatType_32ARGB, attrs as CFDictionary, &pxBuffer)
    guard let buffer = pxBuffer else { return nil }
    CVPixelBufferLockBaseAddress(buffer, [])
    defer { CVPixelBufferUnlockBaseAddress(buffer, []) }
    if let ctx = CGContext(
        data: CVPixelBufferGetBaseAddress(buffer),
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: CVPixelBufferGetBytesPerRow(buffer),
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue
    ) {
        ctx.setFillColor(red: 250/255, green: 246/255, blue: 240/255, alpha: 1.0)
        ctx.fill(CGRect(x: 0, y: 0, width: width, height: height))
        ctx.setAlpha(alpha)
        ctx.draw(cgImage, in: CGRect(x: 0, y: 0, width: width, height: height))
    }
    return buffer
}

var frameIndex: Int64 = 0
for (imgURL, dur) in segments {
    let frameCount = max(1, Int64(round(dur * Double(fps))))
    guard let baseBuffer = makePixelBuffer(from: imgURL, alpha: 1.0) else {
        fputs("Failed to load image: \(imgURL.path)\n", stderr)
        exit(1)
    }
    let fadeFrames = min(6, frameCount / 4)
    for f in 0..<fadeFrames {
        while !writerInput.isReadyForMoreMediaData {
            Thread.sleep(forTimeInterval: 0.002)
        }
        let alpha = CGFloat(f + 1) / CGFloat(fadeFrames + 1)
        let buf = makePixelBuffer(from: imgURL, alpha: alpha) ?? baseBuffer
        adaptor.append(buf, withPresentationTime: CMTime(value: frameIndex + f, timescale: fps))
    }
    // Append opaque static hold at fadeFrames and at segment tail to preserve exact duration without redundant frame copies
    while !writerInput.isReadyForMoreMediaData {
        Thread.sleep(forTimeInterval: 0.002)
    }
    adaptor.append(baseBuffer, withPresentationTime: CMTime(value: frameIndex + fadeFrames, timescale: fps))
    if frameCount - 1 > fadeFrames {
        while !writerInput.isReadyForMoreMediaData {
            Thread.sleep(forTimeInterval: 0.002)
        }
        adaptor.append(baseBuffer, withPresentationTime: CMTime(value: frameIndex + frameCount - 1, timescale: fps))
    }
    frameIndex += frameCount
}

writerInput.markAsFinished()
writer.endSession(atSourceTime: CMTime(value: frameIndex, timescale: fps))
let writeGroup = DispatchGroup()
writeGroup.enter()
writer.finishWriting {
    writeGroup.leave()
}
writeGroup.wait()

if writer.status != .completed {
    fputs("Writer failed: \(writer.error?.localizedDescription ?? "unknown")\n", stderr)
    exit(1)
}

// Step 2: Mux video + WAV audio into final MP4 with AAC audio
let comp = AVMutableComposition()
let videoAsset = AVURLAsset(url: videoOnlyURL)
let audioAsset = AVURLAsset(url: audioURL)

let vGroup = DispatchGroup()
vGroup.enter()
Task {
    do {
        if let vTrack = try await videoAsset.loadTracks(withMediaType: .video).first {
            let compV = comp.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid)
            let vDur = try await videoAsset.load(.duration)
            try compV?.insertTimeRange(CMTimeRange(start: .zero, duration: vDur), of: vTrack, at: .zero)
        }
        if let aTrack = try await audioAsset.loadTracks(withMediaType: .audio).first {
            let compA = comp.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid)
            let aDur = try await audioAsset.load(.duration)
            try compA?.insertTimeRange(CMTimeRange(start: .zero, duration: aDur), of: aTrack, at: .zero)
        }
        guard let exporter = AVAssetExportSession(asset: comp, presetName: AVAssetExportPresetHighestQuality) else {
            fputs("Failed to create AVAssetExportSession\n", stderr)
            exit(1)
        }
        exporter.outputURL = outputURL
        exporter.outputFileType = .mp4
        exporter.shouldOptimizeForNetworkUse = true
        await exporter.export()
        if exporter.status != .completed {
            fputs("Export failed: \(exporter.error?.localizedDescription ?? "unknown")\n", stderr)
            exit(1)
        }
        try? FileManager.default.removeItem(at: videoOnlyURL)
        vGroup.leave()
    } catch {
        fputs("Mux error: \(error)\n", stderr)
        exit(1)
    }
}
vGroup.wait()
print("Exported \(outputURL.path)")

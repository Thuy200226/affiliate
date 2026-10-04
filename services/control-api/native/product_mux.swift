import Foundation
import AVFoundation
import AudioToolbox

func mux(_ video: URL, _ voices: [AVURLAsset], _ lengths: [Double], _ starts: [Double], _ duration: Double, _ output: URL) async throws {
    let composition = AVMutableComposition(), asset = AVURLAsset(url:video)
    guard let source = try await asset.loadTracks(withMediaType:.video).first,
        let vt = composition.addMutableTrack(withMediaType:.video,preferredTrackID:kCMPersistentTrackID_Invalid),
        let at = composition.addMutableTrack(withMediaType:.audio,preferredTrackID:kCMPersistentTrackID_Invalid) else { throw RenderError.invalid("tracks") }
    try vt.insertTimeRange(CMTimeRange(start:.zero,duration:CMTime(seconds:duration,preferredTimescale:60000)),of:source,at:.zero)
    for i in voices.indices {
        guard let voice = try await voices[i].loadTracks(withMediaType:.audio).first else { throw RenderError.invalid("voice") }
        try at.insertTimeRange(CMTimeRange(start:.zero,duration:CMTime(seconds:lengths[i],preferredTimescale:60000)),of:voice,at:CMTime(seconds:starts[i],preferredTimescale:60000))
    }
    let reader = try AVAssetReader(asset:composition)
    let v = AVAssetReaderTrackOutput(track:vt,outputSettings:nil)
    let a = AVAssetReaderTrackOutput(track:at,outputSettings:[AVFormatIDKey:kAudioFormatLinearPCM,AVSampleRateKey:48000,AVNumberOfChannelsKey:2,AVLinearPCMBitDepthKey:16,AVLinearPCMIsFloatKey:false])
    reader.add(v); reader.add(a)
    let writer = try AVAssetWriter(outputURL:output,fileType:.mp4)
    guard let format = try await vt.load(.formatDescriptions).first else { throw RenderError.invalid("format") }
    let vi = AVAssetWriterInput(mediaType:.video,outputSettings:nil,sourceFormatHint:format)
    let ai = AVAssetWriterInput(mediaType:.audio,outputSettings:[AVFormatIDKey:kAudioFormatMPEG4AAC,AVSampleRateKey:48000,AVNumberOfChannelsKey:2,AVEncoderBitRateKey:128000])
    writer.add(vi); writer.add(ai); writer.shouldOptimizeForNetworkUse = true
    guard reader.startReading(),writer.startWriting() else { throw RenderError.invalid("mux start") }
    writer.startSession(atSourceTime:.zero)
    var openV = true, openA = true
    let deadline = Date().addingTimeInterval(120)
    while openV || openA {
        guard Date() < deadline,reader.status != .failed,writer.status != .failed else { throw RenderError.invalid("mux timeout") }
        try autoreleasepool {
            if openV && vi.isReadyForMoreMediaData {
                if let sample = v.copyNextSampleBuffer() { guard vi.append(sample) else { throw RenderError.invalid("append video") } }
                else { openV = false; vi.markAsFinished() }
            }
            if openA && ai.isReadyForMoreMediaData {
                if let sample = a.copyNextSampleBuffer() { guard ai.append(sample) else { throw RenderError.invalid("append audio") } }
                else { openA = false; ai.markAsFinished() }
            }
        }
        try await Task.sleep(for:.milliseconds(1))
    }
    guard reader.status == .completed else { throw RenderError.invalid("decode") }
    await writer.finishWriting()
    guard writer.status == .completed else { throw RenderError.invalid("mux finish") }
}

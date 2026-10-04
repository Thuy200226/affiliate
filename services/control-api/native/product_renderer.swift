import Foundation
import AVFoundation
import CoreVideo

@main struct ProductRenderer {
    static func main() async throws {
        guard CommandLine.arguments.count == 3 else { throw RenderError.invalid("arguments") }
        let manifest = try JSONDecoder().decode(Manifest.self,from:Data(contentsOf:URL(fileURLWithPath:CommandLine.arguments[1])))
        guard manifest.scenes.count == 5 else { throw RenderError.invalid("scenes") }
        if CommandLine.arguments[2] == "--check" { try check(manifest.scenes); print("{\"ok\":true}"); return }
        let output = URL(fileURLWithPath:CommandLine.arguments[2]), video = output.deletingLastPathComponent().appendingPathComponent("graphics.mp4")
        guard manifest.scenes.count == 5,!FileManager.default.fileExists(atPath:output.path),!FileManager.default.fileExists(atPath:video.path) else { throw RenderError.invalid("exists or scenes") }
        let voices = try manifest.scenes.map { scene -> AVURLAsset in
            guard let file = scene.audio_file else { throw RenderError.invalid("audio missing") }
            return AVURLAsset(url:URL(fileURLWithPath:file))
        }
        var lengths: [Double] = [], starts: [Double] = [], slots: [Double] = [], total = 0.0
        for voice in voices {
            let length = CMTimeGetSeconds(try await voice.load(.duration))
            guard length.isFinite,length > 0,length <= 12 else { throw RenderError.invalid("voice duration") }
            let slot = ceil(max(3,length + 0.3) * Double(fps)) / Double(fps)
            lengths.append(length); starts.append(total); slots.append(slot); total += slot
        }
        guard total <= 45 else { throw RenderError.invalid("duration") }
        try await render(manifest.scenes,starts,slots,total,video)
        try await mux(video,voices,lengths,starts,total,output)
        print("{\"ok\":true}")
    }
    static func check(_ scenes: [Scene]) throws {
        guard let ctx = CGContext(data:nil,width:width,height:height,bitsPerComponent:8,bytesPerRow:width * 4,
          space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue) else { throw RenderError.invalid("context") }
        for scene in scenes {
            try drawText(scene.label,size:31,top:1680,color:accent,lines:2,ctx:ctx)
            try drawText(scene.headline,size:74,top:1510,color:white,lines:4,ctx:ctx)
            try drawText(scene.voice,size:40,top:520,color:white,lines:5,ctx:ctx)
        }
    }
    static func render(_ scenes: [Scene], _ starts: [Double], _ slots: [Double], _ total: Double, _ file: URL) async throws {
        let writer = try AVAssetWriter(outputURL:file,fileType:.mp4)
        let input = AVAssetWriterInput(mediaType:.video,outputSettings:[AVVideoCodecKey:AVVideoCodecType.h264,AVVideoWidthKey:width,AVVideoHeightKey:height,
            AVVideoCompressionPropertiesKey:[AVVideoAverageBitRateKey:4000000,AVVideoExpectedSourceFrameRateKey:fps]])
        let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput:input,sourcePixelBufferAttributes:[
            kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32BGRA,kCVPixelBufferWidthKey as String:width,kCVPixelBufferHeightKey as String:height,
            kCVPixelBufferCGImageCompatibilityKey as String:true,kCVPixelBufferCGBitmapContextCompatibilityKey as String:true])
        writer.add(input); guard writer.startWriting() else { throw RenderError.invalid("writer") }; writer.startSession(atSourceTime:.zero)
        guard let pool = adaptor.pixelBufferPool else { throw RenderError.invalid("pool") }
        let deadline = Date().addingTimeInterval(180)
        for number in 0..<Int((total * Double(fps)).rounded()) {
            while !input.isReadyForMoreMediaData {
                guard Date() < deadline,writer.status != .failed else { throw RenderError.invalid("render timeout") }
                try await Task.sleep(for:.milliseconds(5))
            }
            let t = Double(number) / Double(fps), i = starts.lastIndex(where: { $0 <= t }) ?? 0
            try autoreleasepool {
                let frame = try productFrame(scene:scenes[i],index:i,progress:(t - starts[i]) / slots[i],pool:pool)
                guard adaptor.append(frame,withPresentationTime:CMTime(value:Int64(number),timescale:Int32(fps))) else { throw RenderError.invalid("frame") }
            }
        }
        input.markAsFinished(); await writer.finishWriting(); guard writer.status == .completed else { throw RenderError.invalid("finish") }
    }
}

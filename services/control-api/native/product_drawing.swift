import Foundation
import CoreGraphics
import CoreText
import CoreVideo

enum RenderError: Error { case invalid(String) }
struct Scene: Decodable { let headline: String; let label: String; let voice: String; let audio_file: String? }
struct Manifest: Decodable { let scenes: [Scene] }
let width = 1080, height = 1920, fps = 24
let background = CGColor(red:0.07,green:0.1,blue:0.2,alpha:1)
let accent = CGColor(red:0.68,green:0.78,blue:1,alpha:1)
let white = CGColor(red:1,green:1,blue:1,alpha:1)

func textLine(_ value: String, _ size: CGFloat, _ color: CGColor) -> CTLine {
    let font = CTFontCreateWithName("HelveticaNeue-Bold" as CFString,size,nil)
    return CTLineCreateWithAttributedString(NSAttributedString(string:value,attributes:[
        NSAttributedString.Key(kCTFontAttributeName as String):font,
        NSAttributedString.Key(kCTForegroundColorAttributeName as String):color]))
}
func drawText(_ value: String, size: CGFloat, top: CGFloat, color: CGColor, lines: Int, ctx: CGContext) throws {
    var rows: [String] = [], current = ""
    for word in value.split(whereSeparator: { $0.isWhitespace }) {
        let next = current.isEmpty ? String(word) : current + " " + word
        if CTLineGetTypographicBounds(textLine(next,size,color),nil,nil,nil) > 860 {
            guard !current.isEmpty else { throw RenderError.invalid("word too wide") }
            rows.append(current); current = String(word)
        } else { current = next }
    }
    if !current.isEmpty { rows.append(current) }
    guard rows.count <= lines else { throw RenderError.invalid("too many lines") }
    for (index,row) in rows.enumerated() {
        let line = textLine(row,size,color)
        guard CTLineGetTypographicBounds(line,nil,nil,nil) <= 860 else { throw RenderError.invalid("overflow") }
        ctx.textPosition = CGPoint(x:110,y:top - CGFloat(index) * size * 1.3); CTLineDraw(line,ctx)
    }
}
func rect(_ rect: CGRect, _ radius: CGFloat, _ color: CGColor, _ ctx: CGContext) {
    ctx.setFillColor(color); ctx.addPath(CGPath(roundedRect:rect,cornerWidth:radius,cornerHeight:radius,transform:nil)); ctx.fillPath()
}
func productFrame(scene: Scene, index: Int, progress: Double, pool: CVPixelBufferPool) throws -> CVPixelBuffer {
    var raw: CVPixelBuffer?
    guard CVPixelBufferPoolCreatePixelBuffer(nil,pool,&raw) == kCVReturnSuccess, let buffer = raw else { throw RenderError.invalid("buffer") }
    CVPixelBufferLockBaseAddress(buffer,[]); defer { CVPixelBufferUnlockBaseAddress(buffer,[]) }
    guard let ctx = CGContext(data:CVPixelBufferGetBaseAddress(buffer),width:width,height:height,bitsPerComponent:8,
        bytesPerRow:CVPixelBufferGetBytesPerRow(buffer),space:CGColorSpaceCreateDeviceRGB(),
        bitmapInfo:CGImageAlphaInfo.premultipliedFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue) else { throw RenderError.invalid("context") }
    ctx.setFillColor(background); ctx.fill(CGRect(x:0,y:0,width:width,height:height))
    for i in 0..<5 { rect(CGRect(x:110 + i * 176,y:1770,width:145,height:8),4,i <= index ? accent : CGColor(gray:0.3,alpha:1),ctx) }
    try drawText(scene.label,size:31,top:1680,color:accent,lines:2,ctx:ctx)
    try drawText(scene.headline,size:74,top:1510,color:white,lines:4,ctx:ctx)
    // Neutral kinetic card, not a drawing/photo of an unverified product.
    let offset = CGFloat(50 * sin(progress * Double.pi))
    rect(CGRect(x:110,y:700 + offset,width:860,height:310),34,CGColor(red:0.15,green:0.2,blue:0.37,alpha:1),ctx)
    try drawText(String(format:"%02d",index + 1),size:100,top:880 + offset,color:accent,lines:1,ctx:ctx)
    rect(CGRect(x:90,y:260,width:900,height:330),30,CGColor(red:0.11,green:0.15,blue:0.28,alpha:1),ctx)
    try drawText(scene.voice,size:40,top:520,color:white,lines:5,ctx:ctx)
    return buffer
}

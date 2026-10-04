const assert = require("node:assert/strict");
const {youtubeId} = require("../apps/console/media-preview.js");
const {metric} = require("../apps/console/results-view.js");
for (const url of ["https://www.youtube.com/watch?v=abcdefghijk", "https://youtube.com/shorts/abcdefghijk", "https://youtu.be/abcdefghijk"]) {
  assert.equal(youtubeId(url), "abcdefghijk");
}
for (const url of ["javascript:alert(1)", "https://evil.test/abcdefghijk", "http://youtu.be/abcdefghijk", "https://x@youtu.be/abcdefghijk", "https://youtu.be:123/abcdefghijk", "https://youtu.be/a"]) {
  assert.equal(youtubeId(url), null);
}
for (const value of [null, undefined, "", " ", true, false, [], {}, -1, "bad", Infinity]) {
  assert.equal(metric(value), "Chưa có dữ liệu");
}
assert.equal(metric(0), "0"); assert.equal(metric("240"), "240");
console.log("PASS: preview URL whitelist; metrics null/zero/invalid distinction");

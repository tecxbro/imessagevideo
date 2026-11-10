# Current Pillow worst-frame qualification

The reviewed Pillow picture is `34143aa92f1179e6231e0e8126a4ca2a9c20c888650df994e95a3569deadb504`, from unchanged final20 scene `658184bb…`. Its fresh full1,458-frame encoded parity meanSSIM is.997471473, minimum.983041 at native1206/40.2s, with no heuristic outlier flag.

Native and encoded source/G/P views were manually inspected, together with native airport, code and passenger crops. All visible boarding UI is present: airport/city/terminal copy, ATL/plane/SFO, passenger Nikki Hanse, gate37, seat10C, date2July2026 and boarding2:50pm. The viewport clips the same lower content in every1206 view. No blank, truncated interior, missing image, changed semantic state or lifecycle error is observed.

Pillow has a sharper glyph/edge profile and visible dark ringing around airport/code ink, plus panel-edge/detail sampling and material differences. They already occur in its native PNG; encoding adds a separate smaller change. NativeP/G MAE is1.337195, encodedP/G1.551348; P's encoded/native difference is.920715. Source/nativeG MAE is3.752643 and source/nativeP4.279633. These are real visible residuals, not a claim of exact original filters or source identity.

A defined edge mask (nativeG adjacent-channel contrast at least12, expanded by3pixels) covers20.24% of pixels and contains70.15% of nativeP/G absolute error. Within-band MAE is4.635136; outside-band.500417. This supports a predominantly edge/material sampling attribution, without proving a universal exact decomposition or dismissing all other differences as antialiasing.

The lower boarding code is a horizontal barcode, not a square QR. It lies outside the1206 source viewport too. Existing source/nativeG/nativeP frame1218 was additionally inspected: the barcode and lower UI are present in all three, with no dropped internal artwork. No new render, supersampling experiment, production PNG, master, scene or engine change was made for this qualification.

All review images are same-folder portable copies, with hashes in `qualification.json`. `index.html` provides the native/encoded and barcode views. Source and G images are diagnostic only and never substituted into the native output.

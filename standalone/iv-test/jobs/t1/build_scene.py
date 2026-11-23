import json

P = json.load(open("fit/params.json"))
FPS = 30
FIRST = 15

# keyframes for learned interval scene (t=0 at src frame 15)
def keys(name):
    ks=[]
    for f in sorted(int(x) for x in P):
        v = P[str(f)][name]
        ks.append({"t": round((f-FIRST)/FPS, 7), "value": v})
    return ks

yk = [{"t":k["t"],"value":k["value"]} for k in keys("Y")]
sxk = [{"t":k["t"],"value":k["value"]} for k in keys("sx")]
syk = [{"t":k["t"],"value":k["value"]} for k in keys("sy")]

def base_layers():
    return [
      {"id":"divider","type":"rect","x":0,"y":126,"width":960,"height":3,"fill":"#c4c4c4"},
      {"id":"avatar","type":"circle","x":456,"y":20,"width":48,"height":48,"fill":"#d0d0d3"},
      {"id":"sam","type":"text","x":457,"y":75,"text":"Sam","fontSize":22,"fontFamily":"Helvetica","fill":"#000000","textAnchor":"middle"},
      {"id":"chevron","type":"text","x":41,"y":60,"text":"‹","fontSize":43,"fontFamily":"Helvetica","fill":"#0483ff"},
      {"id":"bubble-out","type":"group","x":0,"y":0,"children":[
        {"id":"bubble-out-bg","type":"rect","x":560,"y":180,"width":340,"height":60,"radius":30,"fill":"#0883fc"},
        {"id":"bubble-out-text","type":"text","x":638,"y":196,"text":"train gets in at 6","fontSize":26,"fontFamily":"Helvetica","fill":"#ffffff"}]},
      {"id":"bubble-in1","type":"group","x":0,"y":0,"children":[
        {"id":"bubble-in1-bg","type":"rect","x":60,"y":270,"width":311,"height":61,"radius":30.5,"fill":"#e7e7e9"},
        {"id":"bubble-in1-text","type":"text","x":136,"y":285,"text":"see you there","fontSize":26,"fontFamily":"Helvetica","fill":"#000000"}]},
    ]

def doors_group(t0, yk, sxk, syk):
    def shift(ks): return [{"t":round(k["t"]+t0,7),"value":k["value"]} for k in ks]
    return {"id":"doors","type":"group","x":60,"y":360,"originX":125.5,"originY":61,
      "children":[
        {"id":"doors-bubble","type":"rect","x":0,"y":0,"width":251,"height":61,"radius":30.5,"fill":"#e7e7e9"},
        {"id":"doors-text","type":"text","x":67,"y":15,"text":"doors at 7","fontSize":26,"fontFamily":"Helvetica","fill":"#000000"}],
      "keyframes":{"y":shift(yk),"scaleX":shift(sxk),"scaleY":shift(syk)}}

# learned interval scene: 135 frames = src 15..149
scene = {"width":960,"height":720,"fps":30,"duration":135/30,"background":"#fdfdfd",
         "layers": base_layers()+[doors_group(0, yk, sxk, syk)]}
json.dump(scene, open("scene_learn.json","w"), indent=1)

# film scene: 150 frames = src 0..149; doors hidden until 0.5s
scene2 = {"width":960,"height":720,"fps":30,"duration":150/30,"background":"#fdfdfd",
          "layers": base_layers()+[dict(doors_group(0.5, yk, sxk, syk), start=0.5)]}
json.dump(scene2, open("scene_film.json","w"), indent=1)
print("wrote scene_learn.json, scene_film.json")

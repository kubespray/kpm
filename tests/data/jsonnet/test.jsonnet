local hash(data, hashtype='sha1') =
    std.native("hash")(std.toString(data), hashtype);

local to_yaml(data) =
    std.native("to_yaml")(std.toString(data));

local jinja2(template, env={}) =
    std.native("jinja2")(template, std.toString(env));

local jsonnet(template, env={}) =
    std.native("jsonnet")(template, std.toString(env));

local jsonLoads(data) =
     std.native("json_loads")(data);

local yamlLoads(data) =
     std.native("yaml_loads")(data);

local randAlphaNum(size=32, seed="") =
    std.native("rand_alphanum")(std.toString(size), seed=seed);

local randAlpha(size=32, seed="") =
    std.native("rand_alpha")(std.toString(size), seed=seed);

local randInt(size=32, seed="") =
    std.native("randint")(std.toString(size), seed=seed);

local initSeed = randAlpha();

local genPrivateKey(keytype, key="") =
     std.native("privatekey")(keytype, key=key, seed=initSeed);

{
  env: {
   cookie: "'A124D'"
  },
  a: initSeed,
  b: initSeed,
  c: randInt(8),
  jinja2: jinja2("yo: {{cookie}}", self.env),
  jsonnet: jsonnet("function(cookie='titi')({cookieT: cookie})", self.env),
  json: jsonLoads('{"a": "b"}'),
  yaml_obj: yamlLoads(to_yaml({"a": "b", "t": [1,2,3,4]})),
  hashsha1: hash("titi"),
  hashmd5: hash("titi", 'md5'),
  hashsha256: hash("titi", 'sha256'),
  yaml: to_yaml({"a": "b", "t": [1,2,3,4]}),
  rand_alphnum32: randAlphaNum(),
  rand_alphnum8: randAlphaNum(8),
  rand_alpha8: randAlpha(8),
  rand_alpha32: randAlpha(),
  rand_int32: randInt(seed="4"),
  rand_int8: randInt(8),
  rsa: genPrivateKey("rsa"),
  rsaX: genPrivateKey("rsa", 'x'),
  rsaZ: genPrivateKey("rsa", 'z'),
  rsaZ2: genPrivateKey("rsa", 'z'),
  rsaX2: genPrivateKey("rsa", 'x'),
  dsa: genPrivateKey("dsa"),
  ecdsa: genPrivateKey("ecdsa"),
}
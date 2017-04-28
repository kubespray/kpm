{

   # KPM extended std
   local kpmutils = self,
   # Returns hash of the string representation of an object.
   hash(data, hashtype='sha1'):: (
      std.native("hash")(std.toString(data), hashtype)
   ),

   # Converts an object to yaml string
   to_yaml(data):: (
      std.native("to_yaml")(std.toString(data))
   ),

   # Read a file
   readfile(filepath):: (
      std.native("read")(filepath)
   ),

   # Random alpha-numeric string of length `size`
   randAlphaNum(size=32, seed=""):: (
      std.native("rand_alphanum")(std.toString(size), seed=seed)
   ),

   # Random alpha string of length `size`
   randAlpha(size=32, seed=""):: (
      std.native("rand_alpha")(std.toString(size), seed=seed)
   ),

   # Random numeric string of length `size`
   randInt(size=32, seed=""):: (
      std.native("randint")(std.toString(size), seed=seed)
   ),

   # Generate privateKeys.
   # Keytype choices: 'rsa', 'ecdsa', 'dsa'.
   # key allows to generate a unique key per run
   genPrivateKey(keytype, key=""):: (
      std.native("privatekey")(keytype, key=key, seed=initSeed)
   ),

   loadObject(data):: (
      std.native("obj_loads")(std.toString(data))
   ),

   # Render jinja2 template
   jinja2(template, env={}):: (
      std.native("jinja2")(template, std.toString(env))
   ),

   # Render jsonnet template
   jsonnet(template, env={}):: (
      std.native("jsonnet")(template, std.toString(env))
   ),

   # Convert json string to object
   jsonLoads(data):: (
      std.native("json_loads")(data)
   ),

   # Convert yaml string to object
   yamlLoads(data):: (
      std.native("yaml_loads")(data)),

   # Generate a sequence array from 1 to i
   seq(i):: (
      [x for x in std.range(1, i)]
   ),

   compact(array):: (
     [x for x in array if x != null]
   ),

   local initSeed = kpmutils.randAlpha(256),
}

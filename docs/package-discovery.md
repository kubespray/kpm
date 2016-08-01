## Package discovery

By default, a package name is composed of 2 parts: `namespace/name`.

When this format is used to reference a package, the package must be stored and available in the 'default' registry.
This can quickly become an issue as different registries will appear and packages may move from one to an another or a dependency list refer to packages that exist in differents registries only.
Another point: with the default format there is no source mirror.

To solve this, as suggested in [issue#28](https://github.com/kubespray/kpm/issues/28) KPM has a discovery process to retrieve the sources of a package.

To use this discovery feature, a package must have a URL-like structure: `example.com/name`.

The following spec/proposal is largely inspired from https://github.com/appc/spec/blob/master/spec/discovery.md

### Discovery URL
The template for the discovery URL is:

```html
https://{host}?kpm-discovery=1
```
For example, if the client is looking for `example.com/package-1` it will request:

```html
https://example.com?kpm-discovery=1
```

then inspect HTML returned for meta tags that have the following format:

```html
<meta name="kpm-package" content="package-name url-source">
```

### Templates
It's possible to use variables for basic replacement.

Currently supported variables:

##### name

```html
<meta name="kpm-package" content="example.com/{name} https//myregistry.example.com/{name}">
```


### Example
To perform a deployment `kpm deploy kpm.sh/kpm-registry`
the client will:

- get `https://kpm.sh?kpm-discovery=1`

```html
	<head>
      <meta name="kpm-package" content="kpm.sh/kpm-registry https://api-stg.kpm.sh/api/v1/packages/kubespsray/kpm-registry/pull">
     </head>
```
- Find the tag with `content="kpm.sh/kpm-registry"` and retrieve the url
- use the url `https://api-stg.kpm.sh/api/v1/packages/kubespsray/kpm-registry/pull` to fetch the package

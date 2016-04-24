## Package discovery

By default, a package name is composed of 2 parts: `namespace/name`.
When you use this format to reference it, the package must be stored and available in the 'default' registry.
This can quickly become an issue as different registry will appear, packages maybe move from one to an another or a dependency list may refer to packages that exist in differents registry only.
Another point is the redundancy, using the default format there is no way to use mirrors automatically.

To solve those issues, KPM has a discovery process to retrieve the sources of a package. See https://github.com/kubespray/kpm/issues/28 for more details


To use this discovery feature, a package name can have a URL-like structure: `example.com/name`.
The following spec is largely inspired from https://github.com/appc/spec/blob/master/spec/discovery.md

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


### Example
To deploy `kpm.sh/kpm-registry`
the client will:

- GET https://kpm.sh?kpm-discovery=1

```html
	<head>
      <meta name="kpm-package" content="kpm.sh/kpm-registry https://api-stg.kpm.sh/api/v1/packages/kubespsray/kpm-registry/pull">
     </head>
```

- Find the tag with `content="kpm.sh/kpm-registry"` and retrieve the source
- FETCH the package from `https://api-stg.kpm.sh/api/v1/packages/kubespsray/kpm-registry/pull`

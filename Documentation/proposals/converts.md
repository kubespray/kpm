docker-compose.kpm -> docker-compose (default)
```kpm deploy wordpress --format docker-compose [--to docker]```

docker-compose.kpm -> kompose -> kubernetes
```kpm deploy wordpress --format docker-compose --to kubernetes```

dab.kpm -> dab
```kpm deploy wordpress --format dab [--to docker]```

dab.kpm -> kompose -> kubernetes
```kpm deploy wordpress --format dab --to kubernetes```

kpm -> kubernetes
```kpm deploy workdress [--format kub] [--to kubernetes]```

helm -> helm-manifest -> kubernetes
```kpm deploy wordpress --format chart [--to kubernetes]```

helm.kpm -> helm-manifest -> kubernetes
```kpm deploy wordpress --format helm [--to kubernetes]```

helm.native-kpm -> kubernetes
```kpm deploy wordpress --format chart [--to kubernetes]```
